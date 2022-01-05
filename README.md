# Ether Bot

![](https://img.shields.io/badge/python-3.10-blue.svg)

Ether is a powerful bot for Discord coding in python. It can interact with an online dashboard (feature under development), it has a very complete music part using [Lavalink](https://github.com/Frederikam/Lavalink) and many other features developed or under development.

The bot will be divided into two parts, one opensource and another that will communicate with a database, the latter will be private.

## Installation

Only **Windows** is supported for now.

[Warning] The bot is still in development, come back later to have all the installation steps.

 - Install [Lavalink](https://github.com/Frederikam/Lavalink) and create an application.yml file in the main directory.
 - Install all the dependencies in the `requirements.txt`
 - And put the key-values in a .env file (follow the .env.example)

To build the container:

```
$ docker-compose build
```

To run the container:

```
$ docker-compose up
```

To build and run the container:

```
$ docker-compose up --build
```

To stop/remove the container:

```
$ docker-compose kill
$ docker-compose rm
```

on Linux add `sudo `.

## License

Released under [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.
