from abc import abstractmethod

import lavalink
from discord import Embed


class LavalinkManager:
    __keys__ = ["pass", "host", "ws", "port"]

    def __init__(self, client, **kwargs):
        self.client = client
        for name, value in kwargs.items():
            setattr(self, name, value)

    async def initialize_lavalink(self):
        await lavalink.close()
        await lavalink.initialize(
            self.client,
            host=self.host,
            password=self.password,
            rest_port=self.rest_port,
            ws_port=self.ws_port,
        )

        lavalink.register_event_listener(self.lavalink_event_handler)

    @abstractmethod
    async def lavalink_event_handler(
        self, player: lavalink.Player, event_type: lavalink.LavalinkEvents, extra
    ):

        if event_type == lavalink.LavalinkEvents.TRACK_START:
            track = player.current
            if track:
                embed = Embed(
                    description="▶️ **Now playing** [{0.title}]({0.uri}) !".format(
                        track
                    )
                )
                message = await track.channel.send(embed=embed)
                track.start_message = message
                if not len(player.queue) > 1:
                    player.store("m_msg", message)

        if event_type == lavalink.LavalinkEvents.TRACK_END:
            msg = player.fetch("m_msg")
            if (
                extra == lavalink.TrackEndReason.FINISHED
                or extra == lavalink.TrackEndReason.REPLACED
            ):
                if msg:
                    await msg.delete()

            if len(player.queue):
                await player.stop()
