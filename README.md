# Mochi DiscordBot

![](https://img.shields.io/badge/python-3.9-blue.svg) ![](https://img.shields.io/badge/discord-py-blue.svg) ![](https://img.shields.io/github/license/holy-tanuki/Mochi-DiscordBot) ![](https://img.shields.io/github/stars/holy-tanuki/Mochi-DiscordBot)

Mochi is a powerful bot for Discord coding in python. It can interact with an online dashboard (feature under development), it has a very complete music part using [Lavalink](https://github.com/Frederikam/Lavalink) and many other features developed or under development.

The bot will be divided into two parts, one opensource and another that will communicate with a database, the latter will be private.

## To-do list

Mochi is in the very early stages of development, many of the features are not there yet but they will come.

For the moment only this feature is available:

### Admin
    Kick ✅, Ban ✅, Mute ❌, Unban ❌, Unmute ❌
### Image
    Meme ✅, Cat ✅, Dog ✅, Aww ✅, Sadcat ✅,
    Fans ✅, axolotl ✅
### Misc
    Help ✅, Ping ✅, Avatar ✅, Flipcoin ✅
### Music
    Join ✅, Leave ✅, Play ✅, Stop ✅, Pause ✅,
    Resume ✅, Loop ✅, Skip ✅, Shuffle ✅, Queue ✅,
    Lavalinkinfo ✅, Search ❌
## Installation

Only **Windows** is supported for now.

[Warning] The bot is still in development, come back later to have all the installation steps.

 - Install [Lavalink](https://github.com/Frederikam/Lavalink) and create an application.yml file in the main directory.
 - Install all the dependencies in the `requirements.txt`
 - And put the key-values in a .env file (follow the .env.example)

To run the bot:

```
$ java -jar Lavalink.jar
```

```
$ python -m mochi
```

## License

Released under [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.
