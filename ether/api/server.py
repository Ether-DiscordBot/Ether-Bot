from flask import Flask, jsonify, make_response, request

app = Flask(__name__)


@app.route("/api/music/ensure", methods=["GET"])
def ensure():
    guild_id = request.args.get("guild_id")
    # Check if the guild exists
    if not app.bot.get_guild(int(guild_id)):
        return make_response(jsonify({"error": "Could not find the guild"}), 404)

    return make_response(jsonify({"ensure": True}), 200)


@app.route("/api/music/play", methods=["POST"])
def play():
    pass


@app.route("/api/music/pause", methods=["POST"])
def pause():
    pass


@app.route("/api/music/skip", methods=["POST"])
def skip():
    pass


def start(port, bot):
    app.bot = bot
    app.run(port=port)
