"""조리 중 음성 질의(B흐름) 노드 모음.

Phase A의 react_agent/tool_node ReAct 루프와 동일한 패턴으로, 대체재/생략 질문일 때만
LLM이 스스로 find_substitutes 툴을 호출하도록 하고, 그 외 질문은 일반 조리 지식으로
바로 답하게 한다.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from app.agent.services.guardrail_service import check_substitute_conflict
from app.agent.text_utils import strip_markdown
from app.agent.tools.registry import VOICE_TOOLS
from app.agent.voice_state import VoiceQueryState
from app.core.llm import get_llm
from app.data.repositories.allergen_repository import get_allergen_names_by_ids
from app.data.repositories.recipe_repository import get_recipe_by_id

VOICE_TOOLS_BY_NAME = {tool.name: tool for tool in VOICE_TOOLS}
MAX_VOICE_TURNS = 3

VOICE_SYSTEM_PROMPT = (
    "당신은 '뚜이', 영화 <라따뚜이>의 레미처럼 요리를 진심으로 사랑하는 작은 생쥐 셰프입니다. "
    "지금 사용자 옆에서 함께 요리하며 부지런히 돕고 있습니다.\n\n"
    "말투는 딱딱한 설명문이 아니라, 요리를 좋아하는 친구가 옆에서 같이 고민해주듯 "
    "다정하고 활기차게 답하세요. 사용자를 믿어주고 응원하되, 수다스럽게 늘어지지 말고 "
    "핵심은 분명하고 실용적으로 전달하세요.\n\n"
    "현재 조리 중인 레시피: {recipe_name} (분류: {recipe_category}).\n"
    "사용자의 알레르기 성분: {allergies}.\n\n"
    "재료 대체나 생략 가능 여부를 물으면 반드시 find_substitutes 도구로 확인한 뒤 답하세요. "
    "그 외 조리 방법/순서 질문은 알고 있는 일반 조리 지식으로 답하세요. "
    "알레르기 유발 재료는 절대 대체재로 추천하지 마세요.\n\n"
    "답변 형식 규칙:\n"
    "- 한두 문단으로 나누어 답하세요. 문단 사이는 반드시 빈 줄(줄바꿈 두 번)로 구분하세요.\n"
    "- 이모티콘은 전체 답변에 최대 1개까지만, 정말 어울릴 때만 쓰세요. 남발하지 마세요.\n"
    "- 마크다운 문법(**볼드**, 백틱, #, 인용부호(>), 목록 기호(-) 등)은 절대 쓰지 마세요 "
    "— 화면에 그대로 텍스트로 표시됩니다."
)


def voice_resolve_inputs(state: VoiceQueryState) -> dict:
    recipe = get_recipe_by_id(state.recipe_id)
    return {
        "recipe_name": recipe["name"] if recipe else None,
        "recipe_category": recipe.get("category") if recipe else None,
        "allergies": get_allergen_names_by_ids(state.allergen_ids),
    }


def voice_input_guardrail(state: VoiceQueryState) -> dict:
    if not state.question.strip():
        return {
            "guardrail_blocked": True,
            "final_answer": "질문 내용이 비어있어요. 다시 말씀해주세요.",
        }
    return {"guardrail_blocked": False}


def voice_react_agent(state: VoiceQueryState) -> dict:
    new_messages = []
    if not state.messages:
        new_messages.extend(
            [
                SystemMessage(
                    content=VOICE_SYSTEM_PROMPT.format(
                        recipe_name=state.recipe_name or "알 수 없음",
                        recipe_category=state.recipe_category or "알 수 없음",
                        allergies=", ".join(state.allergies) or "없음",
                    )
                ),
                HumanMessage(content=state.question),
            ]
        )

    conversation = [*state.messages, *new_messages]
    llm = get_llm().bind_tools(VOICE_TOOLS)
    response = llm.invoke(conversation)
    new_messages.append(response)

    return {"messages": new_messages, "turns": state.turns + 1}


def voice_tool_node(state: VoiceQueryState) -> dict:
    last_message = state.messages[-1]
    tool_messages = []
    substitutes = list(state.substitutes)

    for call in last_message.tool_calls:
        tool = VOICE_TOOLS_BY_NAME[call["name"]]
        result = tool.invoke(call["args"])
        tool_messages.append(ToolMessage(content=result.model_dump_json(), tool_call_id=call["id"]))

        if call["name"] == "find_substitutes":
            substitutes.extend(result.substitutes)

    return {"messages": tool_messages, "substitutes": substitutes}


def voice_validate(state: VoiceQueryState) -> dict:
    flagged = [
        substitute.model_copy(
            update={
                "allergy_conflict": check_substitute_conflict(
                    substitute.substitute_name, state.allergies
                )
            }
        )
        for substitute in state.substitutes
    ]
    return {"substitutes": flagged}


def voice_respond(state: VoiceQueryState) -> dict:
    if state.guardrail_blocked:
        return {}

    conflicts = [s for s in state.substitutes if s.allergy_conflict]
    if conflicts:
        warnings = [
            f"{strip_markdown(s.ingredient_name)} 대신 {strip_markdown(s.substitute_name)}을(를) "
            "쓸 수 있지만 알레르기 성분일 수 있어요. 다른 대체재를 찾아드릴까요?"
            for s in conflicts
        ]
        return {"final_answer": " ".join(warnings)}

    last_ai = next(
        (m for m in reversed(state.messages) if isinstance(m, AIMessage) and m.content),
        None,
    )
    answer = strip_markdown(last_ai.content) if last_ai else "답변을 생성하지 못했어요."
    return {"final_answer": answer}
