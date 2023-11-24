from typing import Optional

import discord
import requests
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands

from ether.core.constants import Emoji
from ether.core.embed import Embed
from ether.core.views import AlphabetSelect


class DnD(commands.GroupCog, name="dnd"):
    DND_API_URL = "https://www.dnd5eapi.co/api/"

    def __init__(self, client) -> None:
        self.help_icon = Emoji.DND
        self.client = client

    _class = app_commands.Group(
        name="class", description="DnD class related commands"
    )

    @app_commands.command(name="spells")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def spells(
        self, interaction: discord.Interaction, spell: Optional[str] = None
    ):    # FIXME
        """Get information about a spell or a list of all spells"""
        if not spell:
            r = requests.get(f"{DnD.DND_API_URL}spells")
            if not r.ok:
                return await interaction.response.send_message(
                    embed=Embed.error(description="Sorry, an error was occurred!")
                )

            spells_data = r.json()
            spells_list = [
                f"[{s['name']}](https://dndbeyond.com/spells{s['index']})"
                for s in spells_data['results']
            ]

            embed = Embed(title="Spells list")
            embed.description = f"List of the 50 first spells: \n\n {', '.join(spells_list[:50])}"

            async def callback(c_interaction: discord.Interaction, select: discord.ui.Select):
                letters = (*select.values[0], )

                c_spells = [
                    f"[{s['name']}](https://dndbeyond.com/spells{s['index']})"
                    for s in filter(lambda s: s['index'].startswith(letters), spells_data['results'])
                ]
                c_embed = Embed(
                    title=f"{letters[0].upper()}-{letters[1].upper()} spells list",
                    description=", ".join(c_spells)
                    )

                return await c_interaction.edit_original_response(
                    embed=c_embed
                )

            view = AlphabetSelect(callback=callback)

            return await interaction.response.send_message(embed=embed, view=view)

        spell = spell.lower().replace(" ", "-")
        r = requests.get(f"{DnD.DND_API_URL}spells/{spell}")

        if r.status_code == 404:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, I don't found your spell!")
            )
        elif not r.ok:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, an error was occurred!")
            )

        spell_data = r.json()

        embed = Embed(
            title=f"{spell_data['name']} spell",
            url=f"https://www.dndbeyond.com/spells/{spell_data['index']}",
        )
        embed.description = f"{spell_data['desc'][0]}\n**Level:** {spell_data['level']}\n**Duration:** {spell_data['duration']}\n **Range/Area:** {spell_data['range']}\n **Casting Time:** {spell_data['casting_time']}"

        classes = [c["name"] for c in spell_data["classes"]]
        embed.add_field(name="🎓 Classes", value=f"{', '.join(classes)}", inline=False)
        sub_classes = [sub["name"] for sub in spell_data["subclasses"]]
        embed.add_field(
            name="🗂️ Sub classes", value=f"{', '.join(sub_classes)}", inline=False
        )

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        return await interaction.response.send_message(embed=embed)

    @_class.command(name="infos")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(_class="Pick a class")
    @app_commands.rename(_class="class")
    @app_commands.choices(
        _class=[
            Choice(name="Barbarian", value="barbarian"),
            Choice(name="Bard", value="bard"),
            Choice(name="Cleric", value="cleric"),
            Choice(name="Druid", value="druid"),
            Choice(name="Fighter", value="fighter"),
            Choice(name="Monk", value="monk"),
            Choice(name="Paladin", value="paladin"),
            Choice(name="Ranger", value="ranger"),
            Choice(name="Rogue", value="rogue"),
            Choice(name="Sorcerer", value="sorcerer"),
            Choice(name="Warlock", value="warlock"),
            Choice(name="Wizard", value="wizard"),
        ]
    )
    async def class_infos(
        self,
        interaction: discord.Interaction,
        _class: Choice[str],
    ):
        """Get information about a class"""
        _class = _class.value

        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}")
        if not r.ok:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, an error was occurred!")
            )

        class_data = r.json()

        embed = Embed(
            title=class_data["name"], url=f"https://www.dndbeyond.com/classes/{_class}"
        )

        embed.description = f"Hit die: {class_data['hit_die']}"

        proficiency_choices_desc = "".join(
            "- " + prof_choice["desc"] + "\n"
            for prof_choice in class_data["proficiency_choices"]
        )
        embed.add_field(
            name="Proficiency choices",
            value=proficiency_choices_desc,
            inline=False,
        )

        proficiencies = [
            proficiency["name"]
            for proficiency in class_data["proficiencies"]
            if not proficiency["index"].startswith("saving-throw")
        ]
        proficiencies_desc = ", ".join(proficiencies)

        embed.add_field(
            name="Proficiencies",
            value=proficiencies_desc,
            inline=False,
        )

        saving_throws = [
            saving_throw["name"] for saving_throw in class_data["saving_throws"]
        ]
        saving_throws_desc = ", ".join(saving_throws)

        embed.add_field(
            name="Saving throws",
            value=saving_throws_desc,
            inline=False,
        )

        # Starting equipment
        if len(class_data["starting_equipment"]) > 0:
            starting_equipment = [
                f"- {equipement['quantity']} x **{equipement['equipment']['name']}**"
                for equipement in class_data["starting_equipment"]
            ]
            starting_equipment_desc = "\n".join(starting_equipment)

            embed.add_field(
                name="Starting equipment",
                value=starting_equipment_desc,
                inline=False,
            )

        # Starting equipment options
        if len(class_data["starting_equipment_options"]) > 0:
            starting_equipment_options = [
                "- " + starting_equipment_option["desc"]
                for starting_equipment_option in class_data[
                    "starting_equipment_options"
                ]
            ]
            starting_equipment_options_desc = "\n".join(starting_equipment_options)

            embed.add_field(
                name="Starting equipment options",
                value=starting_equipment_options_desc,
                inline=False,
            )

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        subclasses = [subclass["name"] for subclass in class_data["subclasses"]]
        subclasses_desc = ", ".join(subclasses)

        embed.add_field(
            name="Subclasses",
            value=subclasses_desc,
            inline=False,
        )

        return await interaction.response.send_message(embed=embed)

    @_class.command(name="levels")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(_class="Pick a class")
    @app_commands.rename(_class="class")
    @app_commands.choices(
        _class=[
            Choice(name="Barbarian", value="barbarian"),
            Choice(name="Bard", value="bard"),
            Choice(name="Cleric", value="cleric"),
            Choice(name="Druid", value="druid"),
            Choice(name="Fighter", value="fighter"),
            Choice(name="Monk", value="monk"),
            Choice(name="Paladin", value="paladin"),
            Choice(name="Ranger", value="ranger"),
            Choice(name="Rogue", value="rogue"),
            Choice(name="Sorcerer", value="sorcerer"),
            Choice(name="Warlock", value="warlock"),
            Choice(name="Wizard", value="wizard"),
        ]
    )
    async def class_levels(
        self,
        interaction: discord.Interaction,
        _class: Choice[str],
        level: Optional[int] = -1,
    ):
        """Get the level table of a class"""
        _class = _class.value

        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}/levels")
        if not r.ok:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, an error was occurred!")
            )

        levels_data = r.json()

        embed = Embed(
            title=f"{_class.capitalize()}'s levels",
            url=f"https://dndbeyond.com/classes/{_class}#The{_class.capitalize()}Table",
        )

        if level >= 0:
            if len(levels_data) < level:
                return await interaction.response.send_message(
                    embed=Embed.error(
                        "Sorry, there is no information about this level!"
                    )
                )
            levels_data = [levels_data[level - 1]]

        for level in levels_data:
            level_desc = ""

            level_desc += f"- Ability score bonuses: {level['ability_score_bonuses']}\n"
            level_desc += f"- Proficiency bonus: {level['prof_bonus']}\n"

            # Features
            if len(level["features"]) > 0:
                features = [feature["name"] for feature in level["features"]]
                features_desc = ", ".join(features)
                level_desc += f"- Features: {features_desc}\n\n"

            # Spellcasting
            if "spellcasting" in level:
                spellcasting = level["spellcasting"]
                level_desc += f"- Spellcasting:\n"

                if "cantrips_known" in spellcasting:
                    level_desc += (
                        f" - *Cantrips known:* {spellcasting['cantrips_known']}\n"
                    )
                if "spells_known" in spellcasting:
                    level_desc += f" - *Spells known:* {spellcasting['spells_known']}\n"
                for i in range(1, 9):
                    if (
                        f"spell_slots_level_{i}" in spellcasting
                        and spellcasting[f"spell_slots_level_{i}"] > 0
                    ):
                        level_desc += f" - *Spell slots level {i}:* {spellcasting[f'spell_slots_level_{i}']}\n"

            embed.add_field(
                name=f"Level {level['level']}",
                value=level_desc,
                inline=False,
            )

        return await interaction.response.send_message(
            embed=embed, ephemeral=len(levels_data) >= 0
        )

    @_class.command(name="spells")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(_class="Pick a class")
    @app_commands.rename(_class="class")
    @app_commands.choices(
        _class=[
            Choice(name="Barbarian", value="barbarian"),
            Choice(name="Bard", value="bard"),
            Choice(name="Cleric", value="cleric"),
            Choice(name="Druid", value="druid"),
            Choice(name="Fighter", value="fighter"),
            Choice(name="Monk", value="monk"),
            Choice(name="Paladin", value="paladin"),
            Choice(name="Ranger", value="ranger"),
            Choice(name="Rogue", value="rogue"),
            Choice(name="Sorcerer", value="sorcerer"),
            Choice(name="Warlock", value="warlock"),
            Choice(name="Wizard", value="wizard"),
        ]
    )
    async def class_spells(
        self,
        interaction: discord.Interaction,
        _class: Choice[str],
    ):
        """Get information about spell from a class"""
        _class = _class.value

        r = requests.get(f"{DnD.DND_API_URL}classes/{_class}/spells")
        if not r.ok:
            return await interaction.response.send_message(
                embed=Embed.error(description="Sorry, an error was occurred!")
            )

        spells_data = r.json()
        spells_list = [
            f"[{s['name']}](https://dndbeyond.com/spells/{s['index']})"
            for s in spells_data["results"]
        ]

        embed = Embed(
            title=f"{_class.capitalize()}' spells",
            url=f"https://dndbeyond.com/spells/class/{_class}",
        )
        embed.description = f"List of all {_class}'s spells: \n\n {', '.join(spells_list[:50])}{'...' if len(spells_list) > 50 else '.'}"
        if not spells_list:
            embed.description = "Not smart enough to use spells :/"

        embed.set_footer(
            text="Powered by D&D",
            icon_url="https://img.icons8.com/color/452/dungeons-and-dragons.png",
        )

        return await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=5.0)

    @commands.is_owner()
    @app_commands.command(name="test")
    async def test(self, interaction: discord.Interaction):
        cls = [
            "barbarian",
            "bard",
            "cleric",
            "druid",
            "fighter",
            "monk",
            "paladin",
            "ranger",
            "rogue",
            "sorcerer",
            "warlock",
            "wizard",
        ]

        for _ in cls:
            # FIXME: Invoke doesn't work with interaction
            # await ctx.invoke(self.class_levels, cl)
            # await ctx.invoke(self.class_spells, cl)
            continue

        self.spells(interaction, "acid-arrow")
