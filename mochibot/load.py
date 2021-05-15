import os
from importlib import util
from importlib.abc import Loader
from importlib.machinery import ModuleSpec
import importlib


class LoaderManager:
    def __init__(self, bot):
        self.bot = bot

    def find_extension(self):
        path = "cogs/commands/"
        banned_dir = ['__pycache__']
        name = '__init__.py'
        paths = []

        for dir in os.listdir(path):
            if os.path.isdir(os.path.join(path, dir)) and dir not in banned_dir:
                paths.append(os.path.join(path, dir))

        for path in paths:
            for file in os.listdir(path):
                if file == name:
                    temp = importlib.import_module(path.replace('/', '.'))
                    self.load_extension(temp)

    def load_extension(self, ext):
        try:
            ext.setup(self.bot)
            print(f"--- Commands loaded in {ext.__name__}")
        except Exception as e:
            raise e
