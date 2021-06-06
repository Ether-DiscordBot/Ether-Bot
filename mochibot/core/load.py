import os
import importlib

import mochibot.app


class LoaderManager:
    def __init__(self, bot):
        self.bot = bot

    async def find_extension(self):
        path = "mochibot/cogs/commands/"
        banned_dir = ["__pycache__"]
        name = "__init__.py"
        paths = []

        for dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, dir)) and dir not in banned_dir:
                paths.append(os.path.join(path, dir))

        for path in paths:
            listdir = os.listdir(path)
            for file in listdir:
                if file == name:
                    mod = importlib.import_module(path.replace("/", "."))
                    try:
                        print(file)
                        mod.setup(self.bot)
                        print(
                            f"[{paths.index(path)}/{len(paths)-1}] Commands loaded in {mod.__name__}"
                        )
                    except Exception as e:
                        raise e
