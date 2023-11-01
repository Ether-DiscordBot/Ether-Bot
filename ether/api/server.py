from functools import wraps
import os
import signal
import sys
import threading
import discord
import requests

from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


class ServerThread(threading.Thread):
    def __init__(self, port, bot):
        super(ServerThread, self).__init__()

        self.port = port
        self.bot = bot

    def run(self):
        app.run(port=self.port)

    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            access_token = request.args.get("access_token")
            r = requests.get(
                "https://discord.com/api/oauth2/@me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if not r.ok:
                make_response(jsonify({"error": "Could not identify the user"}), 401)
            setattr(f, "user", r.json())

            return f(*args, **kwargs)

        return wrap

    @app.route("/api/music/ensure", methods=["GET"])
    def ensure(self):
        guild_id = request.args.get("guild_id")

        # Check if the guild exists
        if not app.bot.get_guild(int(guild_id)):
            return make_response(jsonify({"error": "Could not find the guild"}), 404)

        # Identify the user
        return make_response(jsonify({"ensure": True}), 200)

    @app.route("/api/music/current", methods=["GET"])
    @login_required
    def get_current(self):
        guild_id = request.args.get("guild_id")

        # Check if the guild exists
        guild = app.bot.get_guild(int(guild_id))
        if not guild:
            return make_response(jsonify({"error": "Could not find the guild"}), 404)

        return make_response(jsonify({"current": guild.voice_client.is_playing()}), 200)

    @app.route("/api/music/play", methods=["POST"])
    @login_required
    def play(self):
        guild_id = request.args.get("guild_id")
        channel_id = request.args.get("channel_id")
        track = request.args.get("track")
        source = request.args.get("source")  # ytsearch, ytmsearch, scsearch

        # Check if the guild exists
        guild = app.bot.get_guild(int(guild_id))
        if not guild:
            return make_response(jsonify({"error": "Could not find the guild"}), 404)

        # Check if the channel exists
        channel = guild.get_channel(int(channel_id))
        if not channel and channel.type != discord.ChannelType.voice:
            return make_response(
                jsonify(
                    {"error": "Could not find the channel or it's not a voice channel"}
                ),
                404,
            )

        print(track, source)

    @app.route("/api/music/pause", methods=["POST"])
    @login_required
    def pause(self):
        guild_id = request.args.get("guild_id")
        channel_id = request.args.get("channel_id")

        # Check if the guild exists
        guild = app.bot.get_guild(int(guild_id))
        if not guild:
            return make_response(jsonify({"error": "Could not find the guild"}), 404)

        # Check if the channel exists
        channel = guild.get_channel(int(channel_id))
        if not channel and channel.type != discord.ChannelType.voice:
            return make_response(
                jsonify(
                    {"error": "Could not find the channel or it's not a voice channel"}
                ),
                404,
            )

    @app.route("/api/music/skip", methods=["POST"])
    @login_required
    def skip(self):
        guild_id = request.args.get("guild_id")
        channel_id = request.args.get("channel_id")

        # Check if the guild exists
        guild = app.bot.get_guild(int(guild_id))
        if not guild:
            return make_response(jsonify({"error": "Could not find the guild"}), 404)

        # Check if the channel exists
        channel = guild.get_channel(int(channel_id))
        if not channel and channel.type != discord.ChannelType.voice:
            return make_response(
                jsonify(
                    {"error": "Could not find the channel or it's not a voice channel"}
                ),
                404,
            )

    def kill(self):
        os.kill(os.getpid(), signal.SIGINT)
