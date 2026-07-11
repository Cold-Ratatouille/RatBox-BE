from langfuse import observe

from app.agent.prompts.classify_prompt import CLASSIFY_PROMPT
from app.agent.tools.schemas import ClassifyMissingOutput
from app.core.llm import get_llm
from app.data.repositories.recipe_repository import get_recipe_ingredient_names


@observe(name="classify_missing_ingredients", as_type="generation")
def classify(recipe_id: str, available_ingredients: list[str]) -> ClassifyMissingOutput:
    recipe_ingredients = get_recipe_ingredient_names(recipe_id)
    missing = [item for item in recipe_ingredients if item["name"] not in available_ingredients]

    prompt = CLASSIFY_PROMPT.format(
        available_ingredients=available_ingredients,
        missing_ingredients=missing,
    )
    llm = get_llm().with_structured_output(ClassifyMissingOutput)
    return llm.invoke(prompt)
