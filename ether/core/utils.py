import math


class MathsLevels:
    def get_level(level: int, exp):
        return int(math.sqrt(max(MathsLevels.level_to_exp(level) + exp, 1)) * 0.2)

    def level_to_exp(level: int):
        return 50 * pow(level - 1, 2)


class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"


class Color:
    ERROR = 0xED4245
    SUCCESS = 0x57F287
    DEFAULT = 0x5865F2
    BAN = 0xED4245
    KICK = 0xFEE75C
    WARN = 0xFEE75C
    MUTE = 0xFEE75C
    UNBAN = 0x57F287
    UNMUTE = 0x57F287
    PRUNE = 0x5865F2
