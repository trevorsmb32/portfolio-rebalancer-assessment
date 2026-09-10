from decimal import Decimal as D

import pytest

from src.models import Security
from src.rebalance import rebalance

TOTAL_ASSETS = D("100000")
CENT = D("0.01")


@pytest.fixture
def account_to_balance():
    return [
        Security("IBM", D("20"), D("10"), D("150")),
        Security("MSFT", D("20"), D("20"), D("90")),
        Security("ORCL", D("20"), D("30"), D("220")),
        Security("AAPL", D("20"), D("20"), D("450")),
        Security("HD", D("20"), D("20"), D("70")),
    ]


def test_buys_the_underweight_and_sells_the_overweight():
    securities = [
        Security("AAA", D("50"), D("40"), D("100")),
        Security("BBB", D("50"), D("60"), D("100")),
    ]

    assert rebalance(securities, D("10000")) == {"AAA": 10, "BBB": -10}


def test_zero_variance_security_is_not_traded():
    securities = [
        Security("BUY", D("40"), D("30"), D("100")),
        Security("BALANCED", D("30"), D("30"), D("100")),
        Security("SELL", D("30"), D("40"), D("100")),
    ]

    orders = rebalance(securities, D("10000"))

    assert orders["BUY"] == D("10")
    assert orders["BALANCED"] == D("0")
    assert orders["SELL"] == D("-10")


def test_supports_fractional_shares():
    securities = [
        Security("AAA", D("25"), D("20"), D("300")),
        Security("BBB", D("75"), D("80"), D("100")),
    ]

    orders = rebalance(securities, D("10000"))

    assert orders["AAA"] == D("1.666666666666666666666666667")
    assert orders["BBB"] == D("-5")


def test_assessment_scenario_produces_expected_share_counts(account_to_balance):

    result = rebalance(account_to_balance, TOTAL_ASSETS)

    assert result == {
        "IBM": D("66.66666666666666666666666667"),  # $10,000 / $150
        "MSFT": D("0"),
        "ORCL": D("-45.45454545454545454545454545"),  # $10,000 / $220
        "AAPL": D("0"),
        "HD": D("0"),
    }


def test_every_security_reaches_its_target_exactly(account_to_balance):
    orders = rebalance(account_to_balance, TOTAL_ASSETS)

    for s in account_to_balance:
        value_after = s.current_pct / D("100") * TOTAL_ASSETS + orders[s.symbol] * s.price
        target_value = s.target_pct / D("100") * TOTAL_ASSETS

        assert value_after == target_value, (
            f"{s.symbol} ended at ${value_after}, target ${target_value}"
        )


def test_the_rebalance_is_self_funding(account_to_balance):
    orders = rebalance(account_to_balance, TOTAL_ASSETS)
    price = {s.symbol: s.price for s in account_to_balance}

    spent = sum(q * price[s] for s, q in orders.items() if q > 0)
    raised = sum(-q * price[s] for s, q in orders.items() if q < 0)

    # a tolerance, not rounding: $10,000 / $220 does not terminate, so multiplying the
    # quantity back by the price leaves a residue in the 24th decimal. A cent is the
    # smallest unit the money is meaningful in.
    assert abs(spent - raised) < CENT, f"out by ${spent - raised}"

    # exact -- the buy side divides evenly, so no rounding is needed or wanted here
    assert spent == D("10000")


def test_already_balanced_account_generates_no_orders():

    securities = [
        Security("AAA", D("50"), D("50"), D("100")),
        Security("BBB", D("50"), D("50"), D("100")),
    ]

    assert rebalance(securities, D("10000")) == {"AAA": 0, "BBB": 0}


def test_uneven_weights_that_total_100_rebalance_correctly():

    securities = [
        Security("AAA", D("33.33"), D("33.34"), D("100")),
        Security("BBB", D("33.33"), D("33.33"), D("100")),
        Security("CCC", D("33.34"), D("33.33"), D("100")),
    ]

    orders = rebalance(securities, D("10000"))

    assert orders["AAA"] == D("-0.01"), "0.01 points of $10,000 at $100 a share"
    assert orders["BBB"] == 0
    assert orders["CCC"] == D("0.01")


def test_same_input_produces_identical_output(account_to_balance):

    first = rebalance(account_to_balance, TOTAL_ASSETS)
    second = rebalance(account_to_balance, TOTAL_ASSETS)

    assert first == second


def test_zero_target_sells_the_whole_of_that_security():

    securities = [
        Security("AAA", D("0"), D("30"), D("100")),
        Security("BBB", D("100"), D("70"), D("50")),
    ]

    orders = rebalance(securities, D("10000"))

    assert orders["AAA"] == -30, "30% of $10,000 at $100 a share is exactly 30 shares"
    assert orders["BBB"] == 60


def test_a_variance_far_smaller_than_the_price_still_trades():
    securities = [
        Security("AAA", D("5"), D("0"), D("600000")),
        Security("BBB", D("95"), D("100"), D("1")),
    ]

    orders = rebalance(securities, TOTAL_ASSETS)

    assert orders["AAA"] == D("0.008333333333333333333333333333")  # $5,000 / $600,000
    assert orders["BBB"] == -5000


def test_truncating_to_whole_shares_never_overshoots_the_variance(account_to_balance):
    orders = rebalance(account_to_balance, TOTAL_ASSETS)

    assert round(orders["IBM"]) == 67, "rounding to nearest would give 67"
    assert round(orders["ORCL"]) == -45, "truncation applies in both directions"


def test_sub_penny_prices_stay_exact():
    securities = [
        Security("AAA", D("1"), D("0.71"), D("0.01")),
        Security("BBB", D("99"), D("99.29"), D("0.01")),
    ]

    orders = rebalance(securities, D("100"))

    assert orders["AAA"] == 29, "float arithmetic would give 28.999... here"
    assert orders["BBB"] == -29


@pytest.mark.parametrize("bad_price", ["0", "-100"])
@pytest.mark.xfail(strict=True, reason="Price should never be zero or negative")
def test_rejects_a_non_positive_price(bad_price):
    securities = [
        Security("AAA", D("50"), D("40"), D(bad_price)),
        Security("BBB", D("50"), D("60"), D("100")),
    ]

    with pytest.raises(ValueError, match="price must be positive"):
        rebalance(securities, TOTAL_ASSETS)


@pytest.mark.xfail(strict=True, reason="Field should never be missing")
def test_rejects_a_security_with_a_missing_required_field():

    field = "price"
    values = {"target_pct": D("50"), "current_pct": D("50"), "price": D("100")}
    values[field] = None

    securities = [Security("AAA", **values), Security("BBB", D("50"), D("50"), D("100"))]

    with pytest.raises(ValueError, match=rf"AAA: missing required field\(s\): {field}"):
        rebalance(securities, TOTAL_ASSETS)


def test_empty_account_returns_no_orders():
    assert rebalance([], TOTAL_ASSETS) == {}


@pytest.mark.xfail(strict=True, reason="Security should not accept an empty symbol")
def test_rejects_an_invalid_security_symbol():
    securities = [
        Security("", D("50"), D("50"), D("100")),
        Security("BBB", D("50"), D("50"), D("100")),
    ]

    with pytest.raises(ValueError, match="symbol"):
        rebalance(securities, TOTAL_ASSETS)


@pytest.mark.xfail(strict=True, reason="Weighting logic should total 100, not less")
def test_rejects_target_weights_that_do_not_sum_to_100():
    """The target column totals 40%. The calculator returns orders selling down every
    security rather than refusing an incomplete model."""
    securities = [
        Security("AAA", D("20"), D("50"), D("100")),
        Security("BBB", D("20"), D("50"), D("100")),
    ]

    with pytest.raises(ValueError, match="target weights must sum to 100%, got 40%"):
        rebalance(securities, TOTAL_ASSETS)


@pytest.mark.xfail(strict=True, reason="Should not be able to accept a negative weight")
def test_rejects_a_negative_weight():

    securities = [
        Security("AAA", D("-10"), D("50"), D("100")),
        Security("BBB", D("110"), D("50"), D("100")),
    ]

    with pytest.raises(ValueError, match="cannot be negative"):
        rebalance(securities, TOTAL_ASSETS)


@pytest.mark.xfail(strict=True, reason="Incorrect total asset amount is accepted")
def test_rejects_non_positive_total_assets(account_to_balance):

    with pytest.raises(ValueError, match="total assets must be positive"):
        rebalance(account_to_balance, D("0"))


@pytest.mark.xfail(strict=True, reason="The same security should not appear twice")
def test_rejects_a_duplicate_security():

    securities = [
        Security("AAA", D("25"), D("25"), D("100")),
        Security("AAA", D("25"), D("25"), D("100")),
        Security("BBB", D("50"), D("50"), D("100")),
    ]

    with pytest.raises(ValueError, match="duplicate securities: AAA"):
        rebalance(securities, TOTAL_ASSETS)
