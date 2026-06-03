import os

workers = 1
threads = 2
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
accesslog = "-"
errorlog = "-"
loglevel = "info"


def on_starting(server):
    """Start the scheduler in the master process before forking workers."""
    from server import start_scheduler
    start_scheduler()
