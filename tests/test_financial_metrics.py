from src.financial_metrics import (
    freight_cost_per_case,
    return_rate,
)


def test_return_rate():
    assert return_rate(5, 100) == 0.05


def test_return_rate_with_zero_deliveries():
    assert return_rate(0, 0) == 0.0


def test_freight_cost_per_case():
    assert freight_cost_per_case(
        freight_cost=200,
        delivered_eaches=100,
        case_pack=10,
    ) == 20