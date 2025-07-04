
import logging
from config import (
    TimeFrame,
    PositionType,
    SignalType,
    TradingConfig,
    RiskMetrics,
    PositionInfo,
)
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskManager:
    """Advanced risk management utilities"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.risk_metrics = RiskMetrics()
        self.position_history = []
        
    def calculate_position_size(self, signal_strength: float, volatility: float, 
                              current_price: float, portfolio_value: float) -> float:
        """Calculate position size based on various methods"""
        
        if self.config.position_sizing_method == "equal_weight":
            return self.config.max_position_size
        
        elif self.config.position_sizing_method == "volatility_target":
            # Target volatility position sizing
            target_vol = self.config.volatility_target
            position_vol = volatility
            if position_vol > 0:
                size = min(target_vol / position_vol, self.config.max_position_size)
                return size * signal_strength
            else:
                return self.config.max_position_size * signal_strength
        
        elif self.config.position_sizing_method == "kelly":
            # Kelly criterion (simplified)
            win_rate = 0.55  # Default assumption
            avg_win = 0.02
            avg_loss = 0.01
            kelly_fraction = win_rate - ((1 - win_rate) * avg_loss / avg_win)
            kelly_fraction = max(0, min(kelly_fraction, self.config.max_position_size))
            return kelly_fraction * signal_strength
        
        else:
            return self.config.max_position_size * signal_strength
    
    def check_risk_limits(self, context, data) -> bool:
        """Check if current portfolio is within risk limits"""
        portfolio_value = context.portfolio.portfolio_value
        
        # Check drawdown limit
        if self.risk_metrics.peak_value == 0:
            self.risk_metrics.peak_value = portfolio_value
        else:
            self.risk_metrics.peak_value = max(self.risk_metrics.peak_value, portfolio_value)
        
        current_drawdown = (self.risk_metrics.peak_value - portfolio_value) / self.risk_metrics.peak_value
        self.risk_metrics.current_drawdown = current_drawdown
        self.risk_metrics.max_drawdown = max(self.risk_metrics.max_drawdown, current_drawdown)
        
        if current_drawdown > self.config.max_drawdown_limit:
            logger.warning(f"Drawdown limit exceeded: {current_drawdown:.2%}")
            return False
        
        # Check leverage limit
        if abs(context.account.leverage) > self.config.max_leverage:
            logger.warning(f"Leverage limit exceeded: {context.account.leverage:.2f}")
            return False
        
        return True
    
    def calculate_stop_loss(self, entry_price: float, position_type: PositionType) -> float:
        """Calculate stop loss level"""
        if position_type == PositionType.LONG:
            return entry_price * (1 - self.config.stop_loss_pct)
        else:  # SHORT
            return entry_price * (1 + self.config.stop_loss_pct)
    
    def calculate_take_profit(self, entry_price: float, position_type: PositionType) -> float:
        """Calculate take profit level"""
        if position_type == PositionType.LONG:
            return entry_price * (1 + self.config.take_profit_pct)
        else:  # SHORT
            return entry_price * (1 - self.config.take_profit_pct)
