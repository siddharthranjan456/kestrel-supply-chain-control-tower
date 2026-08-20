import pandas as pd

from src.service_metrics import (
    add_financial_period,
    fill_rate,
    order_level_otif,
)


def test_fill_rate():
    assert fill_rate(100, 80) == 0.8


def test_fill_rate_with_zero_orders():
    assert fill_rate(0, 0) == 0.0


def test_financial_period():
    data = pd.DataFrame(
        {
            "date": [
                "2026-04-01",
                "2027-03-31",
            ]
        }
    )

    result = add_financial_period(data, "date")

    assert result["financial_year"].tolist() == [
        "FY2026-27",
        "FY2026-27",
    ]

    assert result["financial_quarter"].tolist() == [
        "Q1",
        "Q4",
    ]


def test_order_level_otif():
    data = pd.DataFrame(
        {
            "order_id": [1, 1],
            "ordered_eaches": [5, 5],
            "delivered_eaches": [5, 5],
            "promised_date": [
                "2026-06-10",
                "2026-06-10",
            ],
            "actual_delivery_date": [
                "2026-06-10",
                "2026-06-10",
            ],
        }
    )

    result = order_level_otif(data)

    assert bool(result.loc[0, "otif"]) is True