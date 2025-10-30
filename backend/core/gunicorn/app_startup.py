from core.gunicorn.logger import GunicornLogger

def get_app_options(host: str, port: int, workers: int, timeout: int, loglevel: str) -> dict:
    return {
        "bind": f"{host}:{port}",
        "workers": workers,
        "worker_class": "uvicorn.workers.UvicornWorker",
        "timeout": timeout,
        "accesslog": "-",
        "errorlog": "-",
        "logger_class": GunicornLogger,
        "loglevel": loglevel,
    }
