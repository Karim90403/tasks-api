import uvicorn

from cmd.base.base_command import BaseCommand
from core.environment_config import settings


class Command(BaseCommand):
    help: str = "Run app"

    def add_arguments(self):
        self.parser.add_argument("--host", default=settings.project.api_host)
        self.parser.add_argument("--port", default=settings.project.api_port)

    def execute(self):
        uvicorn.run("main:app", port=self.args.port, host=self.args.host, reload=True)
