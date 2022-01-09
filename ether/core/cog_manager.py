import ether.cogs
from pathlib import Path
import importlib
from typing import List
import os

__all__ = ["CogManager"]

class CogManager:
    """Directory manager for Ether's cogs.
    
    This module allows the bot to load all cogs in ether/cogs/ with the __init__.py files.
    """
    
    COGS_PATH = Path(ether.cogs.__path__[0])
    
    def __init__(self, client):
        self.client = client
    
    async def paths(self) -> List[Path]:
        """Get the paths of the __init__.py files in the cogs directory
        
        Returns
        -------
        List[pathlib.Path]
            A list of paths where a cog packages can be found.
        """
        banned_dir = ["__pycache__"]

        return [
            os.path.join(self.COGS_PATH, d)
            for d in os.listdir(self.COGS_PATH)
            if os.path.isdir(os.path.join(self.COGS_PATH, d)) and d not in banned_dir
        ]
    
    async def load_cogs(self):
        """Load cogs
        """
        
        paths = await self.paths()

        init_file = "__init__.py"

        for path in paths:
            listdir = os.listdir(path)

            for file in listdir:
                if file == init_file:
                    # todo
                    name=f".{os.path.basename(path)}"
                    package = "ether.cogs"
                    mod = importlib.import_module(
                        name, package=package
                    )
                    try:
                        mod.setup(self.client)
                        print(
                            f"\t[{paths.index(path)+1}/{len(paths)}] Commands loaded in {mod.__name__}"
                        )
                    except Exception as e:
                        raise e
            
        