from discord import command


class Nasa(command.Cog, name="nasa"):
    def __init__(self, client) -> None:
        self.fancy_name = "Nasa"
        self.client = client