from dynaconf import Dynaconf, Validator

config = Dynaconf(
    settings_files=["./config.toml", "./.secrets.toml"],
    load_dotenv=True,
    dotenv_override=True,
    envvar_prefix="ETHER",
)

config.validators.register(
    Validator("logLevel", must_exist=None, default="WARN"),
    Validator("bot.token", must_exist=True),
    Validator("bot.debugGuilds", "bot.global", must_exist=None),
    Validator("database.mongodb.uri", must_exist=None),
    Validator(
        "lavalink.host",
        "lavalink.port",
        "lavalink.pass",
        "lavalink.https",
        must_exist=None,
    ),
    Validator("reddit.client.id", "reddit.client.secret", must_exist=None),
    Validator(
        "api.giphy.key",
        "api.youtube.key",
        must_exist=None,
    ),
)

config.validators.validate()
