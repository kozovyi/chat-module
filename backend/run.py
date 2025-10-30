from core.gunicorn.aplication import Aplicatioin
from core.gunicorn.app_startup import get_app_options
from main import app as fastapi_app
from core.config import settings


def main():
    app = Aplicatioin(
        fastapi_app,
        get_app_options(
            settings.run_gunicorn.host,
            settings.run_gunicorn.port,
            settings.run_gunicorn.workers,
            settings.run_gunicorn.timeout,
            settings.logger.log_level
        ),
    )
    app.run()


if __name__ == "__main__":
    main()
