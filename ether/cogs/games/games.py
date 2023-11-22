import random
from typing import Literal, Optional

import discord
from discord import Member, app_commands
from discord.ext import commands
from discord.ext.commands import Context

from ether.core.constants import Emoji
from ether.core.embed import Embed
from ether.core.i18n import _


class TicTacToe:
    class Button(discord.ui.Button):
        def __init__(self, index, row, callback) -> None:
            super().__init__(
                style=discord.ButtonStyle.secondary, label="\u200b", row=row
            )
            self.index = index
            self._callback = callback

        async def callback(self, interaction):
            return await self._callback(self, interaction)

    @classmethod
    def check_win(cls, board, player: str) -> bool:
        b = board

        # Check rows
        for row in [[b[i], b[i + 1], b[i + 2]] for i in range(0, 8, 3)]:
            if all(i == player for i in row):
                return True

        # Check columns
        for col in [[b[i], b[i + 3], b[i + 6]] for i in range(3)]:
            if all(i == player for i in col):
                return True

        # Check diagonals
        return any(
            all(i == player for i in diag)
            for diag in [
                [b[0], b[4], b[8]],
                [b[2], b[4], b[6]],
            ]
        )

    @classmethod
    def empty_indexies(cls, board) -> list:
        return [i for i, x in enumerate(board) if x == 0]

    @classmethod
    def minimax(cls, board, ai_player, other_player) -> Literal[-10, 10, 0]:
        if cls.check_win(board, other_player):
            return -10
        elif cls.check_win(board, ai_player):
            return 10
        else:
            return 0


class Games(commands.GroupCog, name="games"):
    def __init__(
        self,
        client,
    ) -> None:
        self.help_icon = Emoji.GAMES
        self.client = client

    @app_commands.command(name="tictactoe")
    @app_commands.checks.cooldown(1, 60.0, key=lambda i: (i.guild_id, i.user.id))
    async def tictactoe(
        self, interaction: discord.Interaction, opponent: Optional[Member] = None
    ):
        """Play a game of Tic-Tac-Toe with a friend or the bot!"""
        vs_ai: bool = (
            True
            if (opponent and opponent.id == self.client.user.id) or not opponent
            else False
        )
        opponent = opponent if opponent else self.client.user

        if not vs_ai and opponent.bot:
            return await interaction.response.send_message(
                embed=Embed.error(description="You can't play with this person!"),
                delete_after=5,
            )

        board: list[int] = [0 for _ in range(9)]

        players = {1: opponent, 2: interaction.user}
        # 1 => "X", 2 => "O"

        for sign, player in players.items():
            if player.id == opponent.id:
                opponent_sign = sign
            elif player.id == interaction.user.id:
                author_sign = sign

        global turn
        turn = 1 if random.randint(0, 1) == 0 else 2

        async def callback(button, interaction) -> None:
            global turn
            if players[turn].id != self.client.user.id and (
                interaction.user.id != players[turn].id or button.label in ["X", "O"]
            ):
                await interaction.response.defer()
                return

            board[button.index] = turn

            button.label = "X" if turn == 1 else "O"
            button.style = (
                discord.ButtonStyle.green if turn == 1 else discord.ButtonStyle.red
            )

            def finish():
                for item in view.children:
                    item.disabled = True
                button.view.stop()

            if TicTacToe.check_win(board, turn):
                content = f"<@{players[turn].id}> won!"
                finish()
            elif not TicTacToe.empty_indexies(board):
                content = "Tie!"
                finish()
            else:
                turn = 2 if turn == 1 else 1
                content = f"<@{interaction.user.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*"

            if interaction.response.is_done():
                await interaction.edit_original_response(
                    content=content, view=button.view
                )
            else:
                await interaction.response.edit_message(
                    content=content, view=button.view
                )
                if players[turn].id == self.client.user.id:
                    await ai_play(interaction)

        view = discord.ui.View()
        for i in range(9):
            view.add_item(TicTacToe.Button(row=int(i / 3), index=i, callback=callback))

        view.timeout = 30.0

        async def timeout() -> None:
            view.disable_all_items()
            await interaction.message.edit(content="Too late...", view=view)
            view.stop()

        view.on_timeout = timeout

        async def ai_play(interaction) -> None:
            possibilities = TicTacToe.empty_indexies(board)

            if len(possibilities) <= 1:
                button = view.children[possibilities[0]]
                return await callback(button, interaction)

            for p in possibilities:
                # Probability of win for the bot (opponent)
                new_o_board = board.copy()
                new_o_board[p] = opponent_sign

                o_proba = TicTacToe.minimax(new_o_board, opponent_sign, author_sign)
                if o_proba == 10:
                    button = view.children[p]
                    break

                # Probability of win for the opponent (author)

                new_a_board = board.copy()
                new_a_board[p] = author_sign

                a_proba = TicTacToe.minimax(new_a_board, opponent_sign, author_sign)

                if a_proba == -10:
                    button = view.children[p]
                    break
            else:
                button = view.children[random.choice(possibilities)]

            await callback(button, interaction)

        await interaction.response.send_message(
            f"<@{interaction.user.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*",
            view=view,
        )

        if players[turn].id == self.client.user.id:
            await ai_play(interaction)
