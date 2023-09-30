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
    Validator("lavalink.default_node", must_exist=True),
    Validator(
        "lavalink.nodes",
        must_exist=None,
        condition=lambda x: len(x) > 0,
    ),
    Validator(
        "api.giphy.key",
        "api.youtube.key",
        must_exist=None,
    ),
    Validator("server.port", must_exist=None, default=5000),
)

config.validators.validate()
