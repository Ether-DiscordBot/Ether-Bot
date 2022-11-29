import json
from os import path
from functools import wraps

from typing import Any, Callable, Optional
from pycord18n.i18n import InvalidTranslationKeyError
from pycord18n.extension import I18nExtension, _
from pycord18n.language import Language
from discord.ext.commands import Context

from ether.core.logging import log

default_locale = "en"
locale_dir = path.join(path.dirname(path.realpath(__file__)), "locales")

i18n: I18nExtension = I18nExtension(
    [
        Language(
            "French",
            "fr",
            json.load(open(f"{locale_dir}/fr_FR.json", "r", encoding="UTF-8")),
        ),
        Language(
            "English",
            "en",
            json.load(open(f"{locale_dir}/en_US.json", "r", encoding="UTF-8")),
        ),
        Language(
            "Spanish",
            "es",
            json.load(open(f"{locale_dir}/es_ES.json", "r", encoding="UTF-8")),
        ),
        Language(
            "Japanese",
            "ja",
            json.load(open(f"{locale_dir}/ja_JP.json", "r", encoding="UTF-8")),
        ),
        Language(
            "German",
            "de",
            json.load(open(f"{locale_dir}/de_DE.json", "r", encoding="UTF-8")),
        ),
        Language(
            "Korean",
            "ko",
            json.load(open(f"{locale_dir}/ko_KO.json", "r", encoding="UTF-8")),
        ),
        Language(
            "Turkish",
            "tr",
            json.load(open(f"{locale_dir}/tr_TR.json", "r", encoding="UTF-8")),
        ),
        Language(
            "Russian",
            "ru",
            json.load(open(f"{locale_dir}/ru_RU.json", "r", encoding="UTF-8")),
        ),
    ],
    fallback="en",
)


def translate(string: str, locale: Optional[str] = None, **kwargs) -> str:
    """Translate a string.

    This function is used to translate a string to the current locale.
    """

    try:
        return i18n.contextual_get_text(string, should_fallback=False, **kwargs)
    except InvalidTranslationKeyError:
        log.warn(
            f"Translation of '{string}' not found for locale `{i18n.get_current_locale()}`!"
        )
        return string


def get_locale(ctx: Context) -> str:
    locale = ctx.locale.split("-")[0]
    return locale if locale in i18n._languages else default_locale


def init_i18n(client):
    i18n.init_bot(client, get_locale)


_ = translate
