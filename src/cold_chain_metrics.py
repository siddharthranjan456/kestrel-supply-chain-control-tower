import pandas as pd


def shipment_excursions(
    readings: pd.DataFrame,
) -> pd.DataFrame:
    required_columns = {
        "shipment_id",
        "temperature_c",
        "min_temperature_c",
        "max_temperature_c",
    }

    missing_columns = required_columns.difference(
        readings.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing cold-chain columns: {sorted(missing_columns)}"
        )

    data = readings.copy()

    data["is_excursion"] = (
        data["temperature_c"]
        < data["min_temperature_c"]
    ) | (
        data["temperature_c"]
        > data["max_temperature_c"]
    )

    return data.groupby(
        "shipment_id",
        as_index=False,
    ).agg(
        excursion=("is_excursion", "max"),
        minimum_recorded=("temperature_c", "min"),
        maximum_recorded=("temperature_c", "max"),
        reading_count=("temperature_c", "size"),
    )


def near_expiry_inventory(
    inventory: pd.DataFrame,
    reference_date,
    days: int = 30,
) -> pd.DataFrame:
    required_columns = {
        "expiry_date",
        "available_quantity",
        "unit_cost",
    }

    missing_columns = required_columns.difference(
        inventory.columns
    )

    if missing_columns:
        raise ValueError(
            f"Missing inventory columns: {sorted(missing_columns)}"
        )

    result = inventory.copy()

    result["expiry_date"] = pd.to_datetime(
        result["expiry_date"],
        errors="coerce",
    )

    result["days_to_expiry"] = (
        result["expiry_date"]
        - pd.Timestamp(reference_date)
    ).dt.days

    result["inventory_value"] = (
        result["available_quantity"].fillna(0)
        * result["unit_cost"].fillna(0)
    )

    return result[
        result["days_to_expiry"].between(0, days)
    ].copy()