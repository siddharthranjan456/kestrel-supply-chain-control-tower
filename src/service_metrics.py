import pandas as pd


def safe_ratio(numerator: float, denominator: float) -> float:
    return 0.0 if denominator in (0, None) or pd.isna(denominator) else numerator / denominator


def fill_rate(ordered_eaches: float, delivered_eaches: float) -> float:
    return safe_ratio(delivered_eaches, ordered_eaches)


def to_eaches(quantity, qty_uom, case_pack):
    factor = pd.Series(qty_uom).str.upper().eq("CASE") if not isinstance(qty_uom, str) else qty_uom.upper() == "CASE"
    return quantity * case_pack if isinstance(factor, bool) and factor else quantity if isinstance(factor, bool) else pd.Series(quantity).where(~factor, pd.Series(quantity) * pd.Series(case_pack))


def financial_period(date_value) -> tuple[str, str]:
    date = pd.Timestamp(date_value)
    start = date.year if date.month >= 4 else date.year - 1
    quarter = {4:"Q1",5:"Q1",6:"Q1",7:"Q2",8:"Q2",9:"Q2",10:"Q3",11:"Q3",12:"Q3",1:"Q4",2:"Q4",3:"Q4"}[date.month]
    return f"FY{start}-{str(start + 1)[-2:]}", quarter


def aggregate_service(data: pd.DataFrame, group: str) -> pd.DataFrame:
    grouped = data.groupby(group, dropna=False).agg(
        ordered_eaches=("ordered_eaches", "sum"),
        delivered_eaches=("delivered_eaches", "sum"),
        ordered_cases=("ordered_cases", "sum"),
        delivered_cases=("delivered_cases", "sum"),
        orders=("order_id", "nunique"),
        otif_orders=("otif", "sum"),
    ).reset_index()
    grouped["fill_rate_eaches"] = grouped["delivered_eaches"] / grouped["ordered_eaches"].replace(0, pd.NA)
    grouped["fill_rate_cases"] = grouped["delivered_cases"] / grouped["ordered_cases"].replace(0, pd.NA)
    grouped["otif_rate"] = grouped["otif_orders"] / grouped["orders"].replace(0, pd.NA)
    return grouped.fillna(0)

