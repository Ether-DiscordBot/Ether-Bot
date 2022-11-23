import math

from discord import Embed, Member

from ether.core.constants import Colors


class LevelsHandler:
    def get_level(self, exp):
        return int(math.sqrt(max(LevelsHandler.level_to_exp(self) + exp, 1)) * 0.2)

    def get_next_level(self):
        return 50 * pow(self, 2)


class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"


class EtherEmbeds:
    def error(description: str):
        return Embed(description=description, colour=Colors.ERROR)

    def success(description: str):
        return Embed(description=description, colour=Colors.SUCCESS)


class NerglishTranslator:
    """
    Translated in Python from https://github.com/salindersidhu/Mgrler
    """

    DICTIONARY = {
        "aunt": "mmmrrggllm",
        "uncle": "mmmrrgglm",
        "friend": "mmmrrglllm",
        "move": "flllurlog",
        "fisherman": "flllurlokkr",
        "feral": "furl",
        "good": "mmmm",
        "magic": "mrrrggk",
        "right": "mmmml",
        "thirsty": "mllgggrrrr",
        "and": "n",
        "no": "nk",
        "sing": "shng",
        "honor": "uuua",
        "scar": "skr",
        "ogre": "rrrgrrr",
        "ringworm": "murguhlum",
        "murloc": "gmmmlmrmrgmg",
        "sorry": "mrrrgll",
        "yes": "mrgle",
        "spring": "srng",
        "clan": "klun",
    }

    CHAR_MAP = {
        "a": "mr",
        "b": "gl",
        "c": "ll",
        "d": "br",
        "e": "mg",
        "f": "gr",
        "g": "lb",
        "h": "rb",
        "i": "ml",
        "j": "br",
        "k": "gr",
        "l": "rl",
        "m": "mr",
        "n": "bl",
        "o": "lr",
        "p": "gr",
        "q": "gl",
        "r": "mr",
        "s": "mrll",
        "t": "gr",
        "u": "ml",
        "v": "ba",
        "w": "mm",
        "x": "mr",
        "y": "rl",
        "z": "lr",
    }

    def translate(self) -> str:
        result = ""

        for word in self.split(" "):
            if word.startswith(("<", ":")) and word.endswith((">", ":")):
                continue

            if t_word := NerglishTranslator.DICTIONARY.get(word.lower()):
                result += f"{t_word} "
            else:
                for c in word:
                    t_c = NerglishTranslator.CHAR_MAP.get(c.lower()) or c
                    result += t_c.upper() if c == c.upper() else t_c

            result += " "
        return result
