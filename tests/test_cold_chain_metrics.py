import pandas as pd

from src.cold_chain_metrics import (
    near_expiry_inventory,
    shipment_excursions,
)


def test_excursion_is_aggregated_per_shipment():
    data = pd.DataFrame(
        {
            "shipment_id": [1, 1],
            "temperature_c": [4, 9],
            "min_temperature_c": [2, 2],
            "max_temperature_c": [8, 8],
        }
    )

    result = shipment_excursions(data)

    assert bool(result.loc[0, "excursion"]) is True


def test_near_expiry_inventory():
    data = pd.DataFrame(
        {
            "expiry_date": [
                "2026-06-20",
                "2026-08-01",
            ],
            "available_quantity": [10, 10],
            "unit_cost": [2, 2],
        }
    )

    result = near_expiry_inventory(
        data,
        reference_date="2026-06-01",
        days=30,
    )

    assert len(result) == 1
    assert result.iloc[0]["inventory_value"] == 20