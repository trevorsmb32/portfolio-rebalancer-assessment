"""Portfolio rebalancing calculator."""

from decimal import Decimal

HUNDRED = Decimal("100")


def rebalance(securities, total_assets):
    """Return {symbol: share count}. Positive = buy, negative = sell, 0 = no trade.

    Works from the weights the exercise supplies. The variance is derived as
    current % - target %, matching the exercise's convention that a negative variance
    means buy. No share holdings are modelled, because the exercise states none.

    Quantities are exact. The exercise asks how to reach zero target variance, and only
    an exact quantity does: reducing IBM's 66.6667 to 66 leaves it at 19.90%.
    """
    if not securities:
        return {}

    result = {}
    for s in securities:
        variance_pct = s.current_pct - s.target_pct
        trade_value = -variance_pct / HUNDRED * total_assets
        result[s.symbol] = trade_value / s.price

    return result
