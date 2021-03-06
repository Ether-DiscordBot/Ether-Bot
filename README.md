# Ether Bot

![made with python](https://forthebadge.com/images/badges/made-with-python.svg) ![build with love](https://forthebadge.com/images/badges/built-with-love.svg)

Ether is a powerful and easy to use Discord bot written in python. Ether include features like: **Moderation, Fun, Leveling, Music, Reddit** and more!

# Hosting

You have 3 ways to host Ether:

1. <a href="#using-python">Using Python</a>
2. <a href="#using-a-virtual-environment">Using a Virtual Environment</a>
3. <a href="#using-docker-compose">Using Docker Compose</a>

## Installing Ether

 1. Rename `.env.example` by `.env` and set a value to all variables.

 2. Update/install submodule with this command
    ```shell
    > git submodule update --remote
    ```

**Skip next steps if you are using docker.**

 3. If you want to use the music cog, install [Lavalink](https://github.com/freyacodes/Lavalink) and put the `Lavalink.jar` file in the lavalink folder.

 4. Install all requirements
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
    * On Windows:    
        ```bat
        > call ./etherenv/Scripts/activate.bat
        ```
    * On Linux/MacOS:
        ```shell
        > source ./etherenv/Scripts/activate.bat
        ```
 3. *(Optional)* If you have install [Lavalink](https://github.com/freyacodes/Lavalink), start the lavalink server (you must have Java 13 installed)
    ```shell
    (etherenv)> java -jar Lavalink.jar
    ```
 4. Run Ether in the virtual environment with this command
    ```shell
    (etherenv)> py -m ether
    ```

## Using Docker Compose

 1. Build the container with this command
    ```shell
    > docker-compose build
    ```
 2. And start the container with this command
    ```shell
    > docker-compose up
    ```

You can execute these two commands in one with this command
```shell
> docker-compose up --build
```

For more commands go check the [docker-compose documentation]().

on Linux add `sudo` before the command.

# License

Released under [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.
