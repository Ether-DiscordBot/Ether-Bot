import requests

from discord import ApplicationCommand, Embed, SlashCommandGroup
from discord.ext import commands, tasks
from ether.core.i18n import _

from ether.core.logging import log
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class Steam(commands.Cog, name="steam"):
    def __init__(self, client) -> None:
        self.help_icon = Emoji.STEAM
        self.client = client
        self.fetch_app_list.start()

    steam = SlashCommandGroup("steam", "Steam commands!")

    def search(self, game: str):
        """Search a game in the steam store"""

        def filter(g, prompt):
            if g["name"].lower() == prompt.lower():
                return True

        for g in self.steam_app_list:
            if filter(g, game):
                return g
        return False

    @tasks.loop(hours=24)
    async def fetch_app_list(self):
        log.info("Fetching the steam app list...")
        r = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
        if not r.ok:
            log.error("Failed to fetch steam app list")
        r = r.json()

        self.steam_app_list = r["applist"]["apps"]

    @steam.command(name="game")
    @locale_doc
    async def get_game(self, ctx: ApplicationCommand, query: str):
        """Get infos about a game"""
        app = self.search(query)
        if not app:
            await ctx.respond(
                "Could not find any game with that query, please provide the exact game name."
            )

        appid = app["appid"]

        r = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={appid}",
            timeout=30.0,
        )
        data = r.json()
        if not r.ok or not data[str(appid)]["success"]:
            await ctx.respond("Sorry, we could not find any data with this game.")
        data = data[str(appid)]["data"]

        embed = Embed(title=data["name"])
        embed.set_image(
            url=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg"
        )

        if data.get("website"):
            embed.url = data["website"]
        else:
            embed.url = f"https://store.steampowered.com/app/{appid}"

        description = f"{data['short_description']}\n\n**App ID:** [{appid}](https://store.steampowered.com/app/{appid})\n**App Type:** {data['type'].capitalize()}\n"

        supported_platforms = [
            p.capitalize() for p in data["platforms"].keys() if data["platforms"][p]
        ]

        description += f"**Platforms:** {', '.join(supported_platforms)}\n\n"

        if data.get("price_overview"):
            price_data = data["price_overview"]
            if price_data["discount_percent"] > 0:
                description += f"**Price:** ~~{price_data['initial_formatted']}~~ {price_data['final_formatted']} **-{price_data['discount_percent']}%**\n"
            else:
                description += f"**Price:** {price_data['initial_formatted']}\n"
        elif data.get("release_date") and data["release_date"]["coming_soon"]:
            description += f"**Release Date:** {data['release_date']['date']}\n"

        categories = [g["description"] for g in data["categories"]]
        description += f"**Categories:** {', '.join(categories)}\n"

        genres = [g["description"] for g in data["genres"]]
        description += f"**Genres:** {', '.join(genres)}\n\n"

        description += f"**Developers:** {', '.join(data['developers'])}\n"
        description += f"**Publishers:** {', '.join(data['publishers'])}\n\n"

        if data.get("metacritic"):
            description += f"**Metacritic Score:** [{data['metacritic']['score']}]({data['metacritic']['url']})"

        embed.description = description

        await ctx.respond(embed=embed)

    @steam.command(name="specials")
    @locale_doc
    async def specials(self, ctx: ApplicationCommand):
        """Get the current steam specials"""
        r = requests.get("https://store.steampowered.com/api/featuredcategories")
        if not r.ok:
            await ctx.respond("Sorry, an error was occured!")

        r = r.json()
        data = r["specials"]

        embed = Embed(title=data["name"])
        description = "".join(
            f"**[{i['name']}](https://store.steampowered.com/app/{i['id']}) (-{i['discount_percent']}%):**\n ~~{i['original_price']/100}~~ {i['final_price']/100}{i['currency']}\n"
            for i in data["items"][:10]
        )

        embed.description = description

        await ctx.respond(embed=embed)

    @steam.command(name="top")
    @locale_doc
    async def top(self, ctx: ApplicationCommand):
        """Get the current steam top sellers"""
        r = requests.get("https://store.steampowered.com/api/featuredcategories")
        if not r.ok:
            await ctx.respond("Sorry, an error was occured!")

        r = r.json()
        data = r["top_sellers"]

        embed = Embed(title=data["name"][:10])
        description = "".join(
            f"**[{i['name']}](https://store.steampowered.com/app/{i['id']}) (-{i['discount_percent']}%):**\n ~~{i['original_price']/100}~~ {i['final_price']/100}{i['currency']}\n"
            if i["discounted"]
            else f"**[{i['name']}](https://store.steampowered.com/app/{i['id']}):**\n {i['final_price']/100}{i['currency']}\n"
            for i in data["items"]
        )

        embed.description = description

        await ctx.respond(embed=embed)

    @steam.command(name="new")
    @locale_doc
    async def new(self, ctx: ApplicationCommand):
        """Get the current steam new releases"""
        r = requests.get("https://store.steampowered.com/api/featuredcategories")
        if not r.ok:
            await ctx.respond("Sorry, an error was occured!")

        r = r.json()
        data = r["new_releases"]

        embed = Embed(title=data["name"])
        description = "".join(
            f"**[{i['name']}](https://store.steampowered.com/app/{i['id']}) (-{i['discount_percent']}%):**\n ~~{i['original_price']/100}~~ {i['final_price']/100}{i['currency']}\n"
            if i["discounted"]
            else f"**[{i['name']}](https://store.steampowered.com/app/{i['id']}):**\n {i['final_price']/100}{i['currency']}\n"
            for i in data["items"][:10]
        )

        embed.description = description

        await ctx.respond(embed=embed)
