# LangGraph Agent 구현 계획 — Pydantic Tool Schema + ReAct Loop + Service Layer

> 대상 범위: 자연어 재료 입력 → 도구 기반 판단 → 재료 부족 분류/대체재 탐색 → 검증 → 응답 생성까지의 LangGraph 에이전트 코어.
> 전체 로드맵(Day1~7) 중 **2단계(MVP)~4단계(검증)**, 즉 Day3~6에 해당하는 부분을 구체화한다. Day1~2 데이터 적재, Day7 배포는 본 문서 범위 밖.

## 0. 설계 원칙

- **Tool은 얇게, Service는 두껍게.** Tool은 Pydantic 스키마 검증 + Service 호출만 담당하고, 실제 DB 쿼리/비즈니스 로직은 Service Layer에 둔다. 이렇게 하면 Tool을 LangGraph 없이도(유닛 테스트에서) 직접 호출 가능.
- **판단은 구조화된 출력으로.** 분류·검증처럼 LLM이 판단하는 단계는 반드시 Pydantic 모델로 구조화된 출력을 받는다(자유 텍스트 파싱 금지).
- **Text-to-SQL은 "자유 SQL 생성"이 아니라 "파라미터화된 쿼리 빌더"로 구현.** LLM이 원시 SQL 문자열을 생성해 실행하는 방식은 SQL Injection·비용 폭주 리스크가 크다. 대신 LLM이 필터 조건(재료 ID, 제외 재료, 조리시간 등)을 구조화 출력으로 뽑고, Service가 이를 안전한 Supabase 쿼리로 변환하는 방식을 기본값으로 한다. (진짜 자유 SQL이 필요하면 읽기 전용 DB 계정 + 화이트리스트 검증을 별도 단계로 추가)
- **ReAct 루프는 LangGraph의 조건부 엣지로 명시.** `agent → (tool_calls 있으면) tool_node → agent → ... → (tool_calls 없으면) validate → respond` 구조를 그래프로 명시적으로 그린다.

## 1. 디렉토리 구조 (제안)

```
RatBox-BE/app/
├── main.py                      # FastAPI 앱, 라우터 등록만
├── api/
│   └── routes/
│       └── chat.py              # POST /chat (SSE) 엔드포인트
├── agents/
│   ├── state.py                 # AgentState (Pydantic) 정의
│   ├── graph.py                 # build_graph(): 노드/엣지 조립
│   └── nodes/
│       ├── input_guardrail.py
│       ├── extract.py           # 재료/알레르기 추출 (LLM, structured output)
│       ├── react_agent.py       # ReAct 판단 노드 (tool binding)
│       ├── validate.py          # 제약 위반 재검증
│       ├── output_guardrail.py
│       └── respond.py           # 최종 자연어 응답 생성
├── tools/
│   ├── schemas.py                # 모든 Tool의 Input/Output Pydantic 스키마
│   ├── recipe_tools.py           # search_recipes (Text-to-SQL 대체)
│   ├── classification_tools.py   # classify_missing_ingredients
│   ├── substitute_tools.py       # find_substitutes
│   ├── rag_tools.py               # search_similar_recipes (pgvector)
│   └── registry.py               # ALL_TOOLS = [...] (LLM에 bind)
├── services/
│   ├── ingredient_service.py     # 재료 정규화/동의어 매핑
│   ├── recipe_service.py         # 레시피 후보 검색 쿼리
│   ├── substitute_service.py     # 대체재 탐색
│   ├── guardrail_service.py      # 입력/출력 가드레일 판정 로직
│   └── rag_service.py            # pgvector 유사도 검색
├── schemas/
│   └── domain.py                 # Ingredient, Recipe, Allergy 등 공용 도메인 모델
├── core/
│   ├── llm.py                    # LLM 클라이언트 팩토리 (Claude/GPT, function calling)
│   └── checkpointer.py           # LangGraph Checkpointer 설정
└── db/
    └── supabase_client.py        # (기존)
```

## 2. 단계별 구현 계획

### Step 1 — State 스키마 정의 (`agents/state.py`)

멀티턴 동안 유지되는 그래프 state를 Pydantic으로 명시한다.

```python
class AgentState(BaseModel):
    messages: list[AnyMessage]          # ReAct 루프의 대화/도구 호출 기록
    ingredients: list[str] = []          # 사용자가 가진 재료
    excluded_ingredients: list[str] = []  # "빼줘" 로 제외된 재료
    allergies: list[str] = []
    candidate_recipes: list[RecipeCandidate] = []
    missing_classification: ClassificationResult | None = None
    substitutes: list[SubstituteResult] = []
    guardrail_blocked: bool = False
    guardrail_reason: str | None = None
    final_answer: str | None = None
```

- `messages`는 `add_messages` reducer로 누적(LangGraph의 `Annotated[list, add_messages]`).
- 나머지 필드는 turn마다 override 되는 필드와 누적되는 필드를 구분해 reducer를 다르게 지정(예: `excluded_ingredients`는 append, `candidate_recipes`는 override).

**DoD**: `AgentState`가 pydantic으로 정의되고, 최소 1개 유닛 테스트로 reducer 동작(누적 vs 덮어쓰기) 확인.

### Step 2 — Service Layer 구현 (`services/*.py`)

기존 `app/main.py`의 `get_ingredient_id` 로직을 `IngredientService`로 이전하고, 나머지 Service를 신규 작성.

- `IngredientService.resolve(name: str) -> IngredientMatch | None`: `ingredients_master` → `ingredient_synonyms` 순으로 조회. 매칭 실패 시 유사 문자열(예: `pg_trgm` 또는 rapidfuzz) 기반 후보 반환 → 상위 레이어에서 "확인 질문" 분기에 사용.
- `RecipeService.search(ingredient_ids, exclude_ids=None, max_cooking_time=None) -> list[RecipeCandidate]`: `recipe_ingredients` 조인 쿼리를 파라미터 기반으로 구성.
- `SubstituteService.find(ingredient_id) -> list[SubstituteCandidate]`: 대체재 테이블(신규 설계 필요, 예: `ingredient_substitutes(ingredient_id, substitute_id, note)`) 조회.
- `GuardrailService.check_input(text) -> GuardrailVerdict`: 욕설/무관 입력 판정(키워드 블록리스트 + LLM 판정 이중화).
- `GuardrailService.filter_allergens(recipes, allergies) -> (filtered, violations)`: 알레르기 재료 하드 필터링.
- `RagService.similar_recipes(recipe_id | query_embedding, top_k) -> list[RecipeCandidate]`: pgvector 코사인 유사도 검색.

**DoD**: 각 Service에 Supabase 없이도 동작 확인 가능한 유닛 테스트(Supabase 클라이언트는 mock/fixture로 대체) 작성. `SubstituteService`가 참조할 테이블 스키마를 이 단계에서 확정.

### Step 3 — Pydantic Tool Schema 정의 (`tools/schemas.py`)

각 Tool의 Input/Output을 명시적 Pydantic 모델로 정의하고, LLM function calling에 그대로 노출한다.

```python
class SearchRecipesInput(BaseModel):
    ingredients: list[str] = Field(..., description="사용자가 보유한 재료명 목록")
    excluded_ingredients: list[str] = Field(default_factory=list)
    max_cooking_time: int | None = Field(None, description="분 단위")

class SearchRecipesOutput(BaseModel):
    recipes: list[RecipeCandidate]

class ClassifyMissingInput(BaseModel):
    recipe_id: int
    available_ingredients: list[str]

class ClassifyMissingOutput(BaseModel):
    필수재료: list[str]
    생략가능: list[str]
    이유: str

class FindSubstitutesInput(BaseModel):
    ingredient_name: str
    recipe_id: int | None = None

class FindSubstitutesOutput(BaseModel):
    substitutes: list[SubstituteCandidate]
    이유: str
```

- `ClassifyMissingOutput`처럼 **판단이 들어가는 출력은 반드시 `이유` 필드를 포함**(PRD 요구사항 — 근거 명시).
- 각 스키마는 `docstring`/`Field(description=...)`를 촘촘히 채운다 — 이게 그대로 LLM에 전달되는 tool spec이 되므로 설명 품질이 tool 선택 정확도에 직결.

**DoD**: 모든 스키마에 `model_config = {"json_schema_extra": {...}}` 또는 `Field(description=...)`가 채워져 있고, `model_json_schema()` 출력을 눈으로 확인.

### Step 4 — Tool 구현 (`tools/*.py`)

LangChain `@tool` 데코레이터 + `args_schema`로 Step 2 Service를 감싼다.

```python
@tool("search_recipes", args_schema=SearchRecipesInput)
def search_recipes(ingredients: list[str], excluded_ingredients: list[str] = [], max_cooking_time: int | None = None) -> SearchRecipesOutput:
    ids = [ingredient_service.resolve(n) for n in ingredients]
    ...
    return SearchRecipesOutput(recipes=recipe_service.search(ids, ...))
```

`registry.py`에서 `ALL_TOOLS = [search_recipes, classify_missing_ingredients, find_substitutes, search_similar_recipes]`로 모아 ReAct 노드에 bind.

**DoD**: 각 Tool을 LangGraph 없이 직접 `.invoke({...})` 호출해 스키마 검증 + Service 연동이 되는지 확인하는 유닛 테스트.

### Step 5 — ReAct 루프 그래프 구성 (`agents/graph.py`, `nodes/react_agent.py`)

```
input_guardrail → extract → react_agent ⇄ tool_node → validate → output_guardrail → respond → END
                     │(차단 시)                              
                     └──────────────→ END (반려 메시지)
```

- `react_agent` 노드: `llm.bind_tools(ALL_TOOLS)`로 호출 → 응답에 `tool_calls`가 있으면 `tool_node`로, 없으면(최종 답변 준비됨) `validate`로 조건부 라우팅(`add_conditional_edges`).
- `tool_node`: LangGraph의 `ToolNode` 사용(또는 커스텀), 실행 결과를 `messages`에 `ToolMessage`로 append 후 다시 `react_agent`로 복귀 — 이게 "판단→도구선택→재판단" 루프.
- 무한루프 방지: 그래프 실행 시 `recursion_limit` 설정 + `react_agent` 진입 횟수를 state에 카운트, 임계치 초과 시 안전 응답으로 강제 종료.

**DoD**: "계란, 밥, 김치 있고 새우 알레르기 있어" 입력 시 `search_recipes` → (필요시) `classify_missing_ingredients` → `find_substitutes` 순으로 도구가 실제 호출되는 것을 Langfuse/로그로 확인. 최소 3개 시나리오로 루프가 종료(무한루프 없음) 확인.

### Step 6 — 결과 검증 & 가드레일 노드

- `validate` 노드: `guardrail_service.filter_allergens`로 최종 추천 목록에 알레르기 재료가 남아있는지 재검사. 남아있으면 `output_guardrail`에서 자동 제외 또는 대체재로 치환 후 `guardrail_reason`에 기록.
- `input_guardrail`은 그래프 최초 진입점 — 차단 판정 시 즉시 `END`로 라우팅하고 `respond` 없이 고정 반려 메시지 반환.

**DoD**: 알레르기 재료가 섞인 인위적 테스트 케이스에서 최종 응답에 해당 재료가 0건인지 확인(목표: 알레르기 노출 0건).

### Step 7 — Checkpointer 연동 (멀티턴)

- `core/checkpointer.py`에서 `MemorySaver`(로컬 개발) → 필요 시 Postgres 기반 checkpointer로 교체 가능하게 인터페이스 분리.
- `thread_id` = 대화 세션 ID로 사용, `excluded_ingredients`/`allergies`는 세션 내 계속 누적.
- "빼줘"/"못 먹어" 같은 후속 입력은 `extract` 노드가 새 제약을 뽑아 기존 state에 merge하고, `react_agent`부터 재진입(전체 그래프를 처음부터 다시 돌리지 않음).

**DoD**: 동일 `thread_id`로 2턴 이상 호출 시 1턴의 재료/알레르기 정보가 2턴 판단에 반영되는지 통합 테스트로 확인.

### Step 8 — FastAPI 통합 + SSE (`api/routes/chat.py`)

- 그래프를 `graph.astream_events(..., version="v2")`로 실행하며, 노드 진입/도구 호출/최종 응답을 SSE 이벤트로 매핑해 스트리밍.
- 이벤트 타입 예: `status`(현재 어떤 노드/도구 실행 중), `token`(응답 생성 중 토큰), `final`(최종 결과 JSON), `error`.

**DoD**: `curl -N`으로 SSE 응답이 순서대로 흘러나오는지 수동 확인 + 프론트 연동 전 최소 스모크 테스트.

### Step 9 — 테스트 & 관찰가능성

- **유닛**: Service/Tool 단위(Supabase mock).
- **통합**: 그래프 전체를 5~10개 시나리오(정상/재료 0건/알레르기 위반 시도/필수재료 제거 시도/무관 입력)로 실행.
- **Langfuse**: `core/llm.py`의 LLM 클라이언트에 Langfuse 콜백 연결, tool 호출 순서·파라미터·지연시간이 트레이스에 남는지 확인.

**DoD**: PRD의 KPI(핵심 루프 성공률 80%, 알레르기 노출 0건, 멀티턴 100%)를 시나리오 테스트 결과로 수치화.

## 3. 우선 확정이 필요한 설계 이슈

- `ingredient_substitutes` 테이블 스키마 미존재 — Step 2 진행 전 확정 필요.
- Text-to-SQL을 "자유 SQL"로 갈지 "구조화 필터"로 갈지 팀 합의 필요(본 문서는 구조화 필터를 기본값으로 제안).
- 분류 Tool(`classify_missing_ingredients`)이 DB 조회 없이 LLM 판단만 하는 경우, Service Layer 없이 Tool이 직접 LLM을 호출하는 예외를 허용할지 여부.

## 4. 로드맵 매핑

| Step | 내용 | 대략적 Day |
|---|---|---|
| 1~4 | State, Service, Pydantic Tool Schema, Tool 구현 | Day 3 |
| 5 | ReAct 루프 그래프 | Day 3~4 |
| 6 | 검증/가드레일 노드 | Day 5 |
| 7 | Checkpointer 멀티턴 | Day 5 |
| 8 | FastAPI + SSE | Day 4 (뼈대) → Day 5 (완성) |
| 9 | 테스트/Langfuse | Day 6 |
