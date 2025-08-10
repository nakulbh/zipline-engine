from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Abstract base class for Zipline strategies.
    Only defines structure — no execution or analysis.
    """

    @abstractmethod
    def initialize(self, context):
        """Setup: define symbols, commissions, slippage, etc."""
        pass

    def handle_data(self, context, data):
        """Run logic every bar. Override if needed."""
        pass

    def before_trading_start(self, context, data):
        """
        Called daily before market open.
        """
        pass
