from engine.base_strategy import BaseStrategy
from zipline.pipeline import Pipeline
from zipline.pipeline.factors import SimpleMovingAverage, RSI
from zipline.pipeline.data import USEquityPricing

class MyCustomStrategy(BaseStrategy):
    """
    Example custom strategy using RSI and moving averages
    """
    
    def __init__(self, config, rsi_window=14, sma_window=50):
        super().__init__(config)
        self.rsi_window = rsi_window
        self.sma_window = sma_window
    
    def create_pipeline(self):
        """Create pipeline with RSI and SMA factors"""
        
        # RSI factor
        rsi = RSI(window_length=self.rsi_window)
        
        # Simple moving average
        sma_20 = SimpleMovingAverage(
            inputs=[USEquityPricing.close],
            window_length=20
        )
        sma_50 = SimpleMovingAverage(
            inputs=[USEquityPricing.close],
            window_length=50
        )
        
        # Current price
        current_price = USEquityPricing.close.latest
        
        # Volume filter
        dollar_volume = AverageDollarVolume(window_length=30)
        
        return Pipeline(
            columns={
                'rsi': rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'current_price': current_price,
                'dollar_volume': dollar_volume,
            },
            screen=(
                dollar_volume.top(self.config.universe_size) &
                rsi.notnull() &
                sma_20.notnull() &
                sma_50.notnull()
            )
        )
    
    def select_universe(self, context, data):
        """Select universe from pipeline output"""
        return list(context.pipeline_data.index)
    
    def generate_signals(self, context, data):
        """Generate signals based on RSI and moving average crossover"""
        pipeline_data = context.pipeline_data
        signals = {}
        
        for asset in pipeline_data.index:
            if not data.can_trade(asset):
                continue
            
            row = pipeline_data.loc[asset]
            
            # RSI oversold/overbought conditions
            rsi_oversold = row['rsi'] < 30
            rsi_overbought = row['rsi'] > 70
            
            # Moving average crossover
            price_above_sma20 = row['current_price'] > row['sma_20']
            sma20_above_sma50 = row['sma_20'] > row['sma_50']
            
            # Generate signals
            if rsi_oversold and price_above_sma20 and sma20_above_sma50:
                # Buy signal
                signals[asset] = self.config.max_position_size
            elif rsi_overbought:
                # Sell signal
                signals[asset] = 0  # Close position
        
        return signals

# Usage
config = TradingConfig(
    start_date="2020-01-01",
    end_date="2023-12-31",
    capital_base=100000.0,
)

strategy = MyCustomStrategy(config, rsi_window=14, sma_window=50)
engine = TradingEngine(config)
results = engine.run_backtest(strategy)