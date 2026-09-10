"""Domain model for the portfolio rebalancing calculator."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Security:
    """One row of the account table, exactly as the exercise presents it.

    The exercise supplies target %, current % and unit price per security, and no
    share counts anywhere. The calculator works from those three figures alone.
    """

    symbol: str
    target_pct: Decimal
    current_pct: Decimal
    price: Decimal
