import os
import importlib

import app


class LoaderManager:
    def __init__(self, bot):
        self.bot = bot

    async def find_extension(self):
        path = "commands/"
        banned_dir = ["__pycache__"]
        name = "__init__.py"
        paths = []

        for _dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, _dir)) and _dir not in banned_dir:
                paths.append(os.path.join(path, _dir))

        for path in paths:
            listdir = os.listdir(path)
            for file in listdir:
                if file == name:
                    mod = importlib.import_module(
                        path.replace("/", "."), package=__package__
                    )
                    try:
                        mod.setup(self.bot)
                        print(
                            f"\t[{paths.index(path)+1}/{len(paths)}] Commands loaded in {mod.__name__}"
                        )
                    except Exception as e:
                        raise e
