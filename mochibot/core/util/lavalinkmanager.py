from abc import abstractmethod

import lavalink
from discord import Embed


class LavalinkManager:
    def __init__(self, client, lavalink_logs):
        self.client = client
        self.logs = lavalink_logs
        self.lavalink_event_handler = None

    async def initialize_lavalink(self):
        await lavalink.close()
        await lavalink.initialize(
            self.client, host=self.logs.host, password=self.logs.password,
            rest_port=self.logs.port, ws_port=self.logs.ws
        )

        lavalink.register_event_listener(
            self.lavalink_event_handler
        )

    @abstractmethod
    async def lavalink_event_handler(self, player: lavalink.Player, event_type: lavalink.LavalinkEvents, extra):

        if event_type == lavalink.LavalinkEvents.TRACK_START:
            track = player.current
            if track:
                embed = Embed(description="▶️ **Now playing** [{0.title}]({0.uri}) !".format(track))
                message = await track.channel.send(embed=embed)
                track.start_message = message
                if not len(player.queue) > 1:
                    player.store("m_msg", message)

        if event_type == lavalink.LavalinkEvents.TRACK_END:
            msg = player.fetch("m_msg")
            if extra == lavalink.TrackEndReason.FINISHED or extra == lavalink.TrackEndReason.REPLACED:
                if msg:
                    await msg.delete()

            if len(player.queue):
                await player.stop()


class LavalinkLogs:
    def __init__(self, **kwargs):
        self.password = kwargs.get("password")
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.ws = kwargs.get("ws") or kwargs.get("port")