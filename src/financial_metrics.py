import pandas as pd

from src.service_metrics import safe_ratio


def return_rate(
    returned_eaches: float,
    delivered_eaches: float,
) -> float:
    return safe_ratio(
        returned_eaches,
        delivered_eaches,
    )


def freight_cost_per_case(
    freight_cost: float,
    delivered_eaches: float,
    case_pack: float,
) -> float:
    delivered_cases = safe_ratio(
        delivered_eaches,
        case_pack,
    )

    return safe_ratio(
        freight_cost,
        delivered_cases,
    )


def leakage_summary(
    returns: pd.DataFrame,
) -> dict[str, float]:
    returned_eaches = returns.get(
        "returned_eaches",
        pd.Series(dtype=float),
    ).sum()

    return_value = returns.get(
        "return_value",
        pd.Series(dtype=float),
    ).sum()

    credit_note_value = returns.get(
        "credit_note_value",
        pd.Series(dtype=float),
    ).sum()

    return {
        "returned_eaches": float(returned_eaches),
        "return_value": float(return_value),
        "credit_note_value": float(credit_note_value),
    }