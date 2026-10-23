"""Fractional Kelly sizing. Only meaningful if p is demonstrably calibrated."""


def kelly_fraction(p_win: float, win_loss_ratio: float) -> float:
    """Full Kelly for a binary bet: f = p - (1-p)/b, floored at 0."""
    if not 0.0 <= p_win <= 1.0 or win_loss_ratio <= 0:
        raise ValueError("p_win in [0,1] and win_loss_ratio > 0 required")
    return max(0.0, p_win - (1.0 - p_win) / win_loss_ratio)


def position_fraction(p_win: float, win_loss_ratio: float,
                      kelly_mult: float = 0.25, cap: float = 0.10) -> float:
    """Quarter Kelly, capped. The risk engine still applies its own hard limits."""
    return min(cap, kelly_mult * kelly_fraction(p_win, win_loss_ratio))
