# Ether Bot

![](https://img.shields.io/badge/python-3.9-blue.svg) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Ether is a powerful python Discord bot. And has a very complete music part using [Lavalink](https://github.com/Frederikam/Lavalink) and many other features.

## Installation

Prefer to use **Docker-compose** to make sure the bot works properly

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