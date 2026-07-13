"""Commission, exchange-fee and slippage model. All values from config."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    commission_per_side: float   # dollars per contract per side
    exchange_fees_per_side: float
    slippage_ticks: int          # applied to market/stop fills, not limits
    tick_size: float
    point_value: float           # dollars per index point per contract

    @property
    def slippage_points(self) -> float:
        return self.slippage_ticks * self.tick_size

    def round_trip_cost(self, qty: int) -> float:
        return 2.0 * qty * (self.commission_per_side + self.exchange_fees_per_side)

    def trade_pnl(self, side: int, entry_px: float, exit_px: float, qty: int) -> tuple[float, float, float]:
        """Return (gross_pnl, costs, net_pnl) in dollars.

        Slippage is already embedded in the fill prices by the execution layer.
        """
        gross = side * (exit_px - entry_px) * self.point_value * qty
        costs = self.round_trip_cost(qty)
        return gross, costs, gross - costs
