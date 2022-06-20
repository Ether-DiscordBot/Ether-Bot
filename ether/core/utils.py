import math

from discord import Embed, Member

from ether.core.constants import Colors


class LevelsHandler:
    def get_level(level: int, exp):
        return int(math.sqrt(max(LevelsHandler.level_to_exp(level) + exp, 1)) * 0.2)

    def get_next_level(level: int):
        return 50 * pow(level, 2)


class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"


class EtherEmbeds:
    def error(message):
        return Embed(description=message, colour=Colors.ERROR)