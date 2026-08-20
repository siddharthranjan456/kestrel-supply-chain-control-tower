import pandas as pd


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator in (0, None) or pd.isna(denominator):
        return 0.0

    return numerator / denominator


def fill_rate(
    ordered_eaches: float,
    delivered_eaches: float,
) -> float:
    return safe_ratio(
        delivered_eaches,
        ordered_eaches,
    )


def case_equivalents(
    eaches: pd.Series,
    case_pack_at_order: pd.Series,
) -> pd.Series:
    pack_size = pd.to_numeric(
        case_pack_at_order,
        errors="coerce",
    ).replace(0, pd.NA)

    quantities = pd.to_numeric(
        eaches,
        errors="coerce",
    ).fillna(0)

    return quantities.div(pack_size).fillna(0)


def add_financial_period(
    dataframe: pd.DataFrame,
    date_column: str,
) -> pd.DataFrame:
    result = dataframe.copy()

    dates = pd.to_datetime(
        result[date_column],
        errors="coerce",
    )

    start_year = dates.dt.year.where(
        dates.dt.month >= 4,
        dates.dt.year - 1,
    )

    result["financial_year"] = (
        "FY"
        + start_year.astype("Int64").astype(str)
        + "-"
        + (start_year + 1)
        .astype("Int64")
        .astype(str)
        .str[-2:]
    )

    quarter_mapping = {
        4: "Q1",
        5: "Q1",
        6: "Q1",
        7: "Q2",
        8: "Q2",
        9: "Q2",
        10: "Q3",
        11: "Q3",
        12: "Q3",
        1: "Q4",
        2: "Q4",
        3: "Q4",
    }

    result["financial_quarter"] = (
        dates.dt.month.map(quarter_mapping)
    )

    return result


def order_level_otif(
    order_lines: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = {
        "order_id",
        "ordered_eaches",
        "delivered_eaches",
        "promised_date",
        "actual_delivery_date",
    }

    missing_columns = required_columns.difference(
        order_lines.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing OTIF columns: {sorted(missing_columns)}"
        )

    data = order_lines.copy()

    data["promised_date"] = pd.to_datetime(
        data["promised_date"],
        errors="coerce",
    )

    data["actual_delivery_date"] = pd.to_datetime(
        data["actual_delivery_date"],
        errors="coerce",
    )

    orders = data.groupby(
        "order_id",
        as_index=False,
    ).agg(
        ordered_eaches=("ordered_eaches", "sum"),
        delivered_eaches=("delivered_eaches", "sum"),
        promised_date=("promised_date", "max"),
        actual_delivery_date=(
            "actual_delivery_date",
            "max",
        ),
    )

    orders["on_time"] = (
        orders["actual_delivery_date"].notna()
        & (
            orders["actual_delivery_date"]
            <= orders["promised_date"]
        )
    )

    orders["in_full"] = (
        orders["delivered_eaches"]
        >= orders["ordered_eaches"]
    )

    orders["otif"] = (
        orders["on_time"]
        & orders["in_full"]
    )

    return orders