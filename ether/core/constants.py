# COLORS
from enum import IntEnum
import random
from typing import Optional, List


class Colors:

    DEFAULT = 0x5865F2
    ERROR = 0xED4245
    SUCCESS = 0x57F287
    BAN = 0xED4245
    KICK = 0xFEE75C
    WARN = 0xFEE75C
    MUTE = 0xFEE75C
    UNBAN = 0x57F287
    UNMUTE = 0x57F287
    PRUNE = 0x5865F2


# LINKS
class Links:

    BOT_SOURCE_CODE_URL = "https://github.com/Ether-DiscordBot/Ether-Bot"
    BOT_INVITE_URL = "https://discord.com/oauth2/authorize?client_id=985100792270819389&permissions=1514461785206&scope=bot%20applications.commands"

    SUPPORT_SERVER_URL = "https://discord.gg/PzE35PWXmE"

    VINYL_GIF_URL = "https://media1.giphy.com/media/ZHa75MzN09LtS7ruKD/giphy.gif"


# EMOJIS
class Emoji:

    DISCORD = "<:discord:1028255623252553748>"
    GITHUB = "<:github:1154183382515859466>"
    ETHER = "<:ether:1154186165642072104>"
    ETHER_ROUND = "<:ether_round:1154185920447270912>"

    # MUSIC
    BACK = "<:back:990260521355862036>"
    PLAY = "<:play:990260523692064798>"
    NEXT = "<:next:990260522999941130>"
    SHUFFLE = "<:shuffle:990260524686139432>"
    VINYL = "<a:vinyl:1128026008080101502>"

    # CATEGORIES
    ADMIN = "<:admin:1154183389906214985>"
    DND = "<:dnd:1154183377134563328>"
    FUN = "<:fun:1154183379537895424>"
    GAMES = "<:games:1154183380766838834>"
    IMAGE = "<:image:1154183384730439710>"
    INFORMATION = "<:information:1154183386416554085>"
    LEVELS = "<:levels:1154183388652118136>"
    MUSIC = "<:music:1154183391974002688>"
    REACTIONS = "<:reaction:1154183394473807923>"
    REDDIT = "<:reddit:1154183395899867216>"
    STEAM = "<:steam:1154183398068330506>"
    UTILITY = "<:utility:1154183505245384754>"
    BIRTHDAY = "<:birthday:1154182335944724560>"
    OWNER = "<:owner:1154175475321667654>"


class Other:

    AUTHOR_ID = 398763512052056064
    MAIN_CLIENT_ID = 985100792270819389


class ExitCodes(IntEnum):
    #: Clean shutdown (through signals, keyboard interrupt, [p]shutdown, etc.).
    SHUTDOWN = 0
    #: An unrecoverable error occurred during application's runtime.
    CRITICAL = 1
    #: The CLI command was used incorrectly, such as when the wrong number of arguments are given.
    INVALID_CLI_USAGE = 2
    #: Restart was requested by the bot owner (probably through [p]restart command).
    RESTART = 26
    #: Some kind of configuration error occurred.
    CONFIGURATION_ERROR = 78  # Exit code borrowed from os.EX_CONFIG.


class NODE_CODE_NAME:
    CODES = [
        "AWESOME",
        "BEAST",
        "COBRA",
        "DARKNESS",
        "ELITE",
        "FEARLESS",
        "GHOST",
        "HUNTER",
        "ICE",
        "INCREDIBLE",
        "JACKPOT",
        "KILLER",
        "LEGEND",
        "MASTER",
        "NOVA",
        "OMEGA",
        "PIERCING",
        "QUAKE",
        "REVOLUTION",
        "SENTINEL",
        "TITAN",
        "ULTIMATE",
        "VICTORY",
        "WARRIOR",
        "X-RAY",
    ]

    @classmethod
    def get_random(cls, excepts: Optional[List[str]] = []):
        codes = cls.CODES.copy()

        for e in excepts:
            codes.remove(e)

        return random.choice(codes)
