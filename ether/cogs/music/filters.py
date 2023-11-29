from typing import Optional

import discord
import wavelink
from discord import app_commands
from discord.ext import commands

from ether.core.embed import Embed


class Filters(app_commands.Group):
    def __init__(self, parent):
        super().__init__(
            name="filter",
            description="Music filters related commands",
            parent=parent
        )

    async def interaction_check(self, interaction: discord.Interaction):
        """This check if the bot and command author are in the same voicechannel."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                embed=Embed.error(description="Join a voicechannel first."),
                ephemeral=True,
                delete_after=5,
            )
            return False

        player = interaction.guild.voice_client
        if player and player.channel != interaction.user.voice.channel:
            await interaction.response.send_message(
                embed=Embed.error(description="You need to be in my voicechannel."),
                ephemeral=True,
                delete_after=5,
            )
            return False

        return True

    @app_commands.command(name="equalizer")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(sub_bass="16 - 60Hz(must be between -0.25 and 1.0)")
    @app_commands.describe(bass="60 - 250Hz (must be between -0.25 and 1.0)")
    @app_commands.describe(low_mids="250 - 500Hz (must be between -0.25 and 1.0)")
    @app_commands.describe(mids="500 - 2kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(high_mids="2 - 4kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(presence="4 - 6kHz (must be between -0.25 and 1.0)")
    @app_commands.describe(brillance="6 - 16kHz (must be between -0.25 and 1.0)")
    async def equalizer(
        self,
        interaction: discord.Interaction,
        sub_bass: float = None,
        bass: float = None,
        low_mids: float = None,
        mids: float = None,
        high_mids: float = None,
        presence: float = None,
        brillance: float = None,
        reset: bool = False,
    ):
        """An equalizer with 6 bands for adjusting the volume of different frequency."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters: wavelink.Filters = player.filters
        if reset:
            filters.equalizer.reset()
        else:
            bands_value = {
                0: sub_bass,
                2: bass,
                4: low_mids,
                6: mids,
                8: high_mids,
                10: brillance,
                12: presence,
            }
            filters: wavelink.Filters = player.filters
            equalizer = filters.equalizer

            for band, gain in bands_value.items():
                if not gain or gain < -0.25 or gain > 1.0:
                    return await interaction.response.send_message(
                        embed=Embed.error(description="Values must be between `-0.25` and `1.0`."),
                        ephemeral=True,
                        delete_after=5.0,
                    )

                equalizer.payload[band] = gain

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="karaoke")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(level="The level of the effect (between 0.0 and 1.0).")
    @app_commands.describe(
        mono_level="The level of the mono effect (between 0.0 and 1.0)."
    )
    @app_commands.describe(
        filter_band="The frequency of the filter band in Hz (this defaults to 220.0)."
    )
    @app_commands.describe(
        filter_width="The width of the filter band (this defaults to 100.0)."
    )
    async def karaoke(
        self,
        interaction: discord.Interaction,
        level: float = None,
        mono_level: float = None,
        filter_band: float = None,
        filter_width: float = None,
    ):
        """Configure a Karaoke filter. This usually targets vocals, to sound like karaoke music."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if (
            level
            and (level > 1.0 or level < 0.0)
            or mono_level
            and (mono_level > 1.0 or mono_level < 0.0)
        ):
            return await interaction.response.send_message(
                embed=Embed.error(
                    "The level and mono_level values must be between `0.0` and `1.0`."
                ),
                ephemeral=True,
                delete_after=5.0,
            )

        filters = player.filters
        filters.karaoke.set(level, mono_level, filter_band, filter_width)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="timescale")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(speed="The speed of the audio (must be at least 0.0).")
    @app_commands.describe(pitch="The pitch of the audio (must be at least 0.0).")
    @app_commands.describe(rate="The rate of the audio (must be at least 0.0).")
    async def timescale(
        self,
        interaction: discord.Interaction,
        speed: float = None,
        pitch: float = None,
        rate: float = None,
    ):
        """Change the speed, pitch and rate of audio."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if (
            speed
            and (speed > 1.0 or speed < 0.0)
            or pitch
            and (pitch > 1.0 or pitch < 0.0)
            or rate
            and (rate > 1.0 or rate < 0.0)
        ):
            return await interaction.response.send_message(
                embed=Embed.error(description="Values must be between`0.0` and `1.0`."),
                ephemeral=True,
                delete_after=5.0,
            )

        filters = player.filters
        filters.timescale.set(speed, pitch, rate)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="tremolo")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        frequency="The frequency of the tremolo effect (must be at least 0.0)."
    )
    @app_commands.describe(
        depth="The depth of the tremolo effect (between 0.0 and 1.0)."
    )
    async def tremolo(
        self,
        interaction: discord.Interaction,
        frequency: float = None,
        depth: float = None,
    ):
        """Tremolo oscillates the volume of the audio."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if frequency and (frequency < 0.0 or frequency > 2.0):
            return await interaction.response.send_message(
                embed=Embed.error(
                    "Frequency value must be between`0.0` and `2.0`."
                ),
                ephemeral=True,
                delete_after=5.0,
            )

        if depth and (depth < 0.0 or depth > 1.0):
            return await interaction.response.send_message(
                embed=Embed.error(
                    "Frequency value must be between`0.0` and `1.0` (this defaults to 0.5)."
                ),
                ephemeral=True,
                delete_after=5.0,
            )

        filters = player.filters
        filters.tremolo.set(frequency, depth)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="vibrato")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        frequency="The frequency of the tremolo effect (must be at least 0.0)."
    )
    @app_commands.describe(
        depth="The depth of the tremolo effect (between 0.0 and 1.0)."
    )
    async def vibrato(
        self,
        interaction: discord.Interaction,
        frequency: float = None,
        depth: float = None,
    ):
        """Vibrato oscillates the pitch of the audio."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if frequency and (frequency < 0.0 or frequency > 2.0):
            return await interaction.response.send_message(
                embed=Embed.error(
                    "Frequency value must be between`0.0` and `2.0`."
                ),
                ephemeral=True,
                delete_after=5.0,
            )

        if depth and (depth < 0.0 or depth > 1.0):
            return await interaction.response.send_message(
                embed=Embed.error(
                    "Frequency value must be between`0.0` and `1.0` (this defaults to 0.5)."
                ),
                ephemeral=True,
                delete_after=5.0,
            )

        filters = player.filters
        filters.vibrato.set(frequency, depth)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="distortion")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def distortion(
        self,
        interaction: discord.Interaction,
        sin_offset: Optional[float] = None,
        sin_scale: Optional[float] = None,
        cos_offset: Optional[float] = None,
        cos_scale: Optional[float] = None,
        tan_offset: Optional[float] = None,
        tan_scale: Optional[float] = None,
        offset: Optional[float] = None,
        scale: Optional[float] = None,
    ):
        """This applies sine, cosine and tangent distortion to the audio. Pretty hard to use."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters = player.filters
        filters.distortion.set(
            sin_offset,
            sin_scale,
            cos_offset,
            cos_scale,
            tan_offset,
            tan_scale,
            offset,
            scale,
        )

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="channel_mix")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        left_to_left="The amount of the left channel to mix into the left channel."
    )
    @app_commands.describe(
        left_to_right="The amount of the left channel to mix into the right channel."
    )
    @app_commands.describe(
        right_to_left="The amount of the right channel to mix into the left channel."
    )
    @app_commands.describe(
        right_to_right="The amount of the right channel to mix into the right channel."
    )
    async def channel_mix(
        self,
        interaction: discord.Interaction,
        left_to_left: float = None,
        left_to_right: float = None,
        right_to_left: float = None,
        right_to_right: float = None,
    ):
        """Channel mix filter (all at 0.5 => mono, ll=1.0 and rr=1.0 => stereo)."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters = player.filters
        filters.channel_mix.set(
            left_to_left, left_to_right, right_to_left, right_to_right
        )

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="low_pass")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def low_pass(self, interaction: discord.Interaction, smoothing: float):
        """High frequencies are suppressed, while low frequencies are passed through. (this defaults is 0.0)"""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters = player.filters
        filters.low_pass.set(smoothing)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="rotation")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(rotation_hz="The rotation speed in Hz. (1.0 is fast)")
    async def rotation(
        self,
        interaction: discord.Interaction,
        rotation_hz: float = None,
    ):
        """Add a filter which can be used to add a rotating effect to audio."""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        if rotation_hz < 0.0:
            return await interaction.response.send_message(
                embed=Embed.error(description="The rotation_hz value must be at least 0.0."),
                ephemeral=True,
                delete_after=5.0,
            )

        filters = player.filters
        filters.low_pass.set(rotation_hz)

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="The filter will be applied in a few seconds!"),
            delete_after=5.0,
        )

    @app_commands.command(name="volume")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        volume="This defaults to 100 on creation. If the volume is outside 0 to 1000 it will be clamped."
    )
    async def volume(self, interaction: discord.Interaction, volume: int = 100):
        """Change the volume of the audio. (this apply to all users)"""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        await player.set_volume(volume)

        await interaction.response.send_message(
            embed=Embed(description="Volume updated!"), delete_after=5.0
        )

    @app_commands.command(name="clear")
    @commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def volume(self, interaction: discord.Interaction):
        """Clear the filters"""
        player: wavelink.Player = interaction.guild.voice_client

        if not player:
            return

        filters = player.filters
        filters.reset()

        await player.set_filters(filters)

        await interaction.response.send_message(
            embed=Embed(description="Filters clear!"), delete_after=5.0
        )
