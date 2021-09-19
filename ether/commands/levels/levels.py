from discord.ext import commands

class Levels(commands.Cog, name="music"):
    def __init__(self, client):
        self.client = client
        self.fancy_name = "Music"