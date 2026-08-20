import pandas as pd
from src.service_metrics import aggregate_service, fill_rate, financial_period, to_eaches
from src.competitor_prices import normalize_name


def test_fill_rate_and_zero_denominator():
    assert fill_rate(100,80)==0.8
    assert fill_rate(0,0)==0


def test_mixed_uom_conversion():
    assert to_eaches(2,"CASE",12)==24
    assert to_eaches(7,"EACH",12)==7


def test_financial_year_boundaries():
    assert financial_period("2026-04-01")==('FY2026-27','Q1')
    assert financial_period("2027-03-31")==('FY2026-27','Q4')


def test_service_aggregation():
    df=pd.DataFrame({"region":["West"],"ordered_eaches":[100],"delivered_eaches":[80],"ordered_cases":[10],"delivered_cases":[8],"order_id":[1],"otif":[0]})
    result=aggregate_service(df,"region")
    assert result.loc[0,"fill_rate_eaches"]==0.8


def test_competitor_title_normalisation():
    assert normalize_name("Pack of 1 Kestrel Juice 200ML (New)")=="kestrel juice 200ml"

