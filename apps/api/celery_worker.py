from celery import Celery

celery_app = Celery("worker", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

@celery_app.task
def run_backtest(strategy_id: int, bundle_id: int, start_date: str, end_date: str, capital_base: float):
    # This is a placeholder for the actual back-test execution
    # In a real implementation, this would trigger a Docker container with the back-testing engine
    print(f"Running back-test for strategy {strategy_id} with bundle {bundle_id}")
    return {"status": "completed"}
