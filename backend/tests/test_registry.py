from evaluation.registry import get_compared_models, get_default_judge, list_judge_models


def test_no_compared_model_is_judge_eligible() -> None:
    assert all(not model.is_judge_eligible for model in get_compared_models())


def test_judges_and_compared_models_are_disjoint() -> None:
    compared = {model.model_name for model in get_compared_models()}
    judges = {model.model_name for model in list_judge_models()}

    assert compared.isdisjoint(judges)


def test_both_judges_are_listed_and_eligible() -> None:
    providers = {model.provider for model in list_judge_models()}

    assert providers == {"azure_ai_foundry", "google_ai_studio"}
    assert all(model.is_judge_eligible for model in list_judge_models())


def test_default_judge_is_azure_and_itself_eligible() -> None:
    default = get_default_judge()

    assert default.provider == "azure_ai_foundry"
    assert default.model_name == "Llama-3.3-70B-Instruct"
    assert default in list_judge_models()
