CLASSIFY_PROMPT = (
    "사용자가 가진 재료: {available_ingredients}\n"
    "레시피에는 있지만 사용자가 갖고 있지 않은 재료(필수 여부 포함): {missing_ingredients}\n\n"
    "위 부족 재료들을 검토해 '생략해도 조리 가능한 재료(optional)'와 "
    "'빠지면 조리가 불가능한 필수 재료(required)'로 나누어라. "
    "부족 재료가 1개 이하이고 흔한 조미료(소금, 후추, 식용유 등)라면 생략 가능으로 분류해도 된다. "
    "주재료·주단백질이 없는 경우는 required로 분류한다. "
    "판단 근거를 reason에 함께 설명하라."
)
