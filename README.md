# Ether Bot

![made with python](https://forthebadge.com/images/badges/made-with-python.svg) ![build with love](https://forthebadge.com/images/badges/built-with-love.svg)

Ether is a powerful and easy to use Discord bot written in python. Ether include features like: **Moderation, Fun, Leveling, Music, Reddit** and more!

# Hosting

You have 3 ways to host Ether:

1. <a href="#using-python">Using Python</a>
2. <a href="#using-a-virtual-environment">Using a Virtual Environment</a>
3. <a href="#using-docker-compose">Using Docker Compose</a>

## Installing Ether

**Skip these steps if you are using docker.**

1. If you want to use the music cog, install [Lavalink](https://github.com/freyacodes/Lavalink) and put the `Lavalink.jar` file in the lavalink folder.

2. Install all requirements
    ```shell
    > pip install -r requirements.txt
    ``` 

## Using Python

This is not the best way to run ether but probably the fastest.

 1. *(Optional)* If you have install [Lavalink](https://github.com/freyacodes/Lavalink), start the lavalink server (you must have Java 13 installed)
    ```shell
    > java -jar Lavalink.jar
    ```
 2. Run Ether
    ```shell
    > py -m ether
    ```

## Using a Virtual Environment

**Warning:** Using a virtual environment may not work.

 1. Create a virtual environment with this command
    ```shell
    > py -m venv etherenv
    ```
 2. And activate it with this command
    ```shell
    > [call|source] ./etherenv/Scripts/activate.bat
    ```


Prefer to use **Docker-compose** to make sure the bot works properly

 - Install [Lavalink](https://github.com/freyacodes/Lavalink) and create an application.yml file in the main directory.
 - Install all the dependencies in the `requirements.txt`
 - And put the key-values in a .env file (follow the .env.example)


## Using Docker Compose

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

# License

Released under [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.
