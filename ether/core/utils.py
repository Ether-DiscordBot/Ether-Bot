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
