import fastapi
from gunicorn.app.base import BaseApplication


class Aplicatioin(BaseApplication):

    def __init__(self, app: fastapi.FastAPI, options: dict):
        self.optioins = options or {}
        self.aplication = app
        super().__init__()

    def load(self):
        return self.aplication

    @property
    def config_options(self) -> dict:
        return {
            k: v for k, v in self.optioins.items() if k in self.cfg.settings and v is not None  # type: ignore
        }

    def load_config(self):
        for key, val in self.config_options.items():
            if key in self.cfg.settings:  # type: ignore
                self.cfg.set(key.lower(), val)  # type: ignore
