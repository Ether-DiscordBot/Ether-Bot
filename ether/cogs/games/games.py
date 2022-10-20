import random
from typing import Optional

import discord
from discord import ApplicationContext, Member, SlashCommandGroup
from discord.ext import commands
from ether.core.i18n import _

from ether.core.utils import EtherEmbeds
from ether.core.i18n import locale_doc
from ether.core.constants import Emoji


class TicTacToe:
    class Button(discord.ui.Button):
        def __init__(self, index, row, callback):
            super().__init__(
                style=discord.ButtonStyle.secondary, label="\u200b", row=row
            )
            self.index = index
            self._callback = callback

        async def callback(self, interaction):
            return await self._callback(self, interaction)

        @classmethod
        def getButtonStyle(cls, value):
            if value == "X":
                return discord.ButtonStyle.blue
            elif value == "O":
                return discord.ButtonStyle.red
            else:
                return discord.ButtonStyle.gray

    @classmethod
    def check_win(cls, board, player: str) -> bool:
        b = board

        # Check rows
        rows = [[b[i], b[i + 1], b[i + 2]] for i in range(0, 8, 3)]
        for row in rows:
            if all(i == player for i in row):
                return True

        # Check columns
        cols = [[b[i], b[i + 3], b[i + 6]] for i in range(3)]
        for col in cols:
            if all(i == player for i in col):
                return True

        # Check diagonals
        diags = [
            [b[0], b[4], b[8]],
            [b[2], b[4], b[6]],
        ]
        return any(all(i == player for i in diag) for diag in diags)

    @classmethod
    def empty_indexies(cls, board) -> list:
        return [i for i, x in enumerate(board) if x == " "]

    @classmethod
    def minimax(cls, board, ai_player, other_player):
        if cls.check_win(board, other_player):
            return -10
        elif cls.check_win(board, ai_player):
            return 10
        else:
            return 0


class Games(commands.Cog, name="games"):
    def __init__(
        self,
        client,
    ) -> None:
        self.help_icon = Emoji.GAMES
        self.client = client

    games = SlashCommandGroup("games", "Games commands!")

    @games.command(name="tictactoe")
    @locale_doc
    async def tictactoe(
        self, ctx: ApplicationContext, opponent: Optional[Member] = None
    ):
        """Play a game of Tic-Tac-Toe with a friend or the bot!"""
        vs_ai = (
            True
            if (opponent and opponent.id == self.client.user.id) or not opponent
            else False
        )
        opponent = opponent if opponent else self.client.user

        if not vs_ai and opponent.bot:
            return await ctx.respond(
                embed=EtherEmbeds.error("You can't play with this person!"),
                delete_after=5,
            )

        board = [" " for _ in range(9)]

        ps = [ctx.author, opponent]
        random.shuffle(ps)

        players = {"X": ps[0], "O": ps[1]}

        author_sign = None

        for sign, player in players.items():
            if player.id == opponent.id:
                opponent_sign = sign
            elif player.id == ctx.author.id:
                author_sign = sign

        global turn
        turn = "X"

        async def callback(button, interaction):
            global turn
            if players[turn].id != self.client.user.id and (
                interaction.user.id != players[turn].id or button.label in ["X", "O"]
            ):
                await interaction.response.defer()
                return

            board[button.index] = turn

            button.label = turn
            button.style = (
                discord.ButtonStyle.green if turn == "X" else discord.ButtonStyle.red
            )

            if TicTacToe.check_win(board, turn):
                content = f"<@{players[turn].id}> won!"
                button.view.disable_all_items()
                button.view.stop()
            elif not TicTacToe.empty_indexies(board):
                print(board)
                content = "Tie!"
                button.view.disable_all_items()
                button.view.stop()
            else:
                turn = "O" if turn == "X" else "X"
                content = f"<@{ctx.author.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*"

            if interaction.response.is_done():
                await interaction.edit_original_message(
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
            btn = TicTacToe.Button(row=int(i / 3), index=i, callback=callback)
            view.add_item(btn)

        view.timeout = 30.0

        async def timeout():
            view.disable_all_items()
            await ctx.edit(content="Too late...", view=view)
            view.stop()

        view.on_timeout = timeout

        async def ai_play(interaction):
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

        await ctx.respond(
            f"<@{ctx.author.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*",
            view=view,
        )

        if players[turn].id == self.client.user.id:
            await ai_play(ctx.interaction)

    @games.command(name="rps")
    @locale_doc
    async def rps(self, ctx, opponent: Member):
        """Play a game of Rock-Paper-Scissors with a friend!"""
        # TODO Rock/Paper/Scissors
        pass
