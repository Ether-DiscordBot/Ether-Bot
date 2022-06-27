import os

from pathlib import Path
import importlib
from typing import List

import ether.cogs
from ether.core.logging import log

__all__ = ["CogManager"]


class CogManager:
    """Directory manager for Ether's cogs.

    This module allows the bot to load all cogs in ether/cogs/ with the __init__.py files.
    """

    COGS_PATH = Path(ether.cogs.__path__[0])

    async def paths() -> List[str]:
        """Get the paths of the __init__.py files in the cogs directory

        Returns
        -------
        List[pathlib.Path]
            A list of paths where a cog packages can be found.
        """
        banned_dir = ["__pycache__"]

        return [
            os.path.join(CogManager.COGS_PATH, d)
            for d in os.listdir(CogManager.COGS_PATH)
            if os.path.isdir(os.path.join(CogManager.COGS_PATH, d))
            and d not in banned_dir
        ]

    async def load_cogs(self):
        """Load cogs

        This function goes to all folders in the ether/cogs/ folder and loads all cogs.
        A file is folder is composed of at least one __init__.py file and the cog file.
        """

        paths = await CogManager.paths()

        init_file = "__init__.py"

        for path in paths:
            listdir = os.listdir(path)

            for file in listdir:
                if file == init_file:
                    name = f".{os.path.basename(path)}"
                    package = "ether.cogs"
                    mod = importlib.import_module(name, package=package)
                    try:
                        mod.setup(self)
                        log.info(
                            f"[{paths.index(path) + 1}/{len(paths)}] Commands loaded in {mod.__name__}"
                        )
                    except Exception as e:
                        raise e
