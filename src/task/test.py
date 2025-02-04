try:
    from src.task.portfolio.portfolio import individualReport
except ImportError:
    from dev.portfolio.portfolio import individualReport



individualReport()