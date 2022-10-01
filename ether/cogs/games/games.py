import random
from typing import Optional
from discord import ApplicationContext, Member, Option, SlashCommandGroup
import discord
from discord.ext import commands

from ether.core.utils import EtherEmbeds


class TicTacToeButton(discord.ui.Button):
    def __init__(self, index, row, callback):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=row)
        self.index = index
        self._callback = callback
    
    async def callback(self, interaction):
        return await self._callback(self, interaction)
    
    @classmethod   
    def getButtonStyle(cls, value):
        if value == 'X':
            return discord.ButtonStyle.blue
        elif value == 'O':
            return discord.ButtonStyle.red
        else:
            return discord.ButtonStyle.gray
        

class Games(commands.Cog, name="games"):
    def __init__(self, client,) -> None:
        self.fancy_name="Games"
        self.client=client
        
    games = SlashCommandGroup("games", "Games commands!")
    
    @games.command(name="tic-tac-toe")
    async def tictactoe(self, ctx: ApplicationContext, opponent: Optional[Member] = None, difficulty: Option(int, "Difficulty level", min_value=1, max_value=3, default=1) = 1):        
        vs_ai = True if (opponent and opponent.id == self.client.user.id) or not opponent else False
        opponent = opponent if opponent else self.client.user
        
        if not vs_ai and opponent.bot:
            return await ctx.respond(embed=EtherEmbeds.error("You can't play with this person!"), delete_after=5)
        
        board = [" " for _ in range(9)]
        
        ps = [ctx.author, opponent]
        random.shuffle(ps)
        
        players  = {
            'X': ps[0],
            'O': ps[1]
        }
        
        author_sign = None
        opponent_sign = None
        
        for sign, player in players.items():
            if player.id == opponent.id:
                opponent_sign = sign
            elif player.id == ctx.author.id:
                author_sign = sign
                
        global turn 
        turn = 'X'
        
        async def callback(button, interaction):
            global turn
            if players[turn].id != self.client.user.id and (
                interaction.user.id != players[turn].id or button.label in ['X', 'O']
            ):
                await interaction.response.defer()
                return

            board[button.index] = turn

            button.label = turn
            button.style = discord.ButtonStyle.green if turn == 'X' else discord.ButtonStyle.red

            if win := check_win(board, turn):
                content = f"<@{players[turn].id}> won!"
                button.view.disable_all_items()
                button.view.stop()
            elif not empty_indexies(board):
                print(board)
                content = "Tie!"
                button.view.disable_all_items()
                button.view.stop()
            else:
                turn = 'O' if turn == 'X' else 'X'
                content = f"<@{ctx.author.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*"

            if interaction.response.is_done():
                await interaction.edit_original_message(content=content, view=button.view)
            else:
                await interaction.response.edit_message(content=content, view=button.view)
                if players[turn].id == self.client.user.id:
                    await ai_play(interaction)
        
        view = discord.ui.View()
        for i in range(9):
            btn = TicTacToeButton(row=int(i/3), index=i, callback=callback)
            view.add_item(btn)
        
        view.timeout = 30.0
        
        async def timeout():
            view.disable_all_items()
            await ctx.edit(content="Too late...", view=view)
            view.stop()
        
        view.on_timeout = timeout
        
        def check_win(board, player: str) -> bool:
            b = board

            # Check rows
            rows = [[b[i], b[i+1], b[i+2]] for i in range(0, 8, 3)]
            for row in rows:
                if all(i==player for i in row): return True

            # Check columns
            cols = [[b[i], b[i+3], b[i+6]] for i in range(3)]
            for col in cols:
                if all(i==player for i in col): return True

            # Check diagonals
            diags = [
                [b[0], b[4], b[8]],
                [b[2], b[4], b[6]],
            ]
            return any(all(i==player for i in diag) for diag in diags)
        
        def empty_indexies(board) -> list:
            return [i for i, x in enumerate(board) if x == " "]
        
        def minimax(board, ai_player, other_player):
            if check_win(board, other_player):
                return {"score": -10}
            elif check_win(board, ai_player):
                return {"score": 10}
            else:
                return {"score": 0}
        
        async def ai_play(interaction):
            possibilities = empty_indexies(board)            

            if len(possibilities) <= 1:
                button = view.children[possibilities[0]]
                return await callback(button, interaction)

            good_pos = []
            for p in possibilities:                
                new_board = board.copy()
                new_board[p] = players[turn]

                proba = minimax(new_board, players[turn], players[author_sign])["score"]

                if proba == 10:
                    good_pos.append(p)

            if good_pos:
                button = view.children[possibilities[random.choice(good_pos)]]
            if neutral_pos := []:
                button = view.children[possibilities[random.choice(neutral_pos)]]
            else:
                button = view.children[random.choice(possibilities)]

            await callback(button, interaction)
                
        await ctx.respond(f"<@{ctx.author.id}> VS <@{self.client.user.id if vs_ai else opponent.id}>\nIt's the turn of {players[turn]}! *(you have 30 sec)*", view=view)

        if players[turn].id == self.client.user.id:
            await ai_play(ctx.interaction)
    
    @games.command(name="rps")
    async def rps(self, ctx, opponent: Member):
        # TODO Rock/Paper/Scissors
        pass