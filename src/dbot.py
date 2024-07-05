import discord
import random
import json
import pandas as pd
from discord.ext import commands
from dataload import Player, players
from rules import Rules
from draft_process import DraftProcess
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    print('Bot is ready and commands are loaded.')

class DraftBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.draft_process = None
        self.pick_count = 0
        self.how_many_person = 0
        self.current_person_index = 0
        self.person_names = []

    @commands.command()
    async def start_draft(self, ctx, how_many: int, how_many_person: int, rounds: int):
        print(f'Starting draft with {how_many} players, {how_many_person} persons, {rounds} rounds.')
        self.draft_process = DraftProcess(how_many, how_many_person, rounds)
        self.how_many_person = how_many_person
        self.current_person_index = 0
        self.person_names = []
        await ctx.send(f'Draft started with {how_many} players, {how_many_person} persons, {rounds} rounds.')
        await self.ask_for_person_name(ctx)

    async def ask_for_person_name(self, ctx):
        if self.current_person_index < self.how_many_person:
            await ctx.send(f"Enter name for person {self.current_person_index + 1}:")
            try:
                name = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
                self.person_names.append(name.content)
                self.current_person_index += 1
                await self.ask_for_person_name(ctx)
            except asyncio.TimeoutError:
                await ctx.send("Name input timed out. Please restart the draft process.")
        else:
            self.draft_process.set_team_names({f"person{i+1}": name for i, name in enumerate(self.person_names)})
            self.draft_process.generate_draft_order()
            await ctx.send("All names entered. Starting the draft automatically.")
            await self.run_draft(ctx)

    async def run_draft(self, ctx):
        total_picks = self.draft_process.rounds * len(self.draft_process.draft_order)
        snake_order = []

        for i in range(self.draft_process.rounds):
            if i % 2 == 0:
                snake_order.extend(self.draft_process.draft_order)
            else:
                snake_order.extend(reversed(self.draft_process.draft_order))

        self.pick_count = 0

        while self.pick_count < total_picks:
            current_team = snake_order[self.pick_count]
            if current_team.startswith("AI"):
                pick = self.draft_process.ai_draft(current_team)
                await ctx.send(f"{current_team} picked {pick.name}.")
            else:
                await ctx.send(f"{self.draft_process.team_names[current_team]}'s turn. Available players:")
                valid_players = self.draft_process.filter_available_players(current_team)
                player_list = "\n".join([f"{player.name}, {player.position}, {player.team}, {player.ranking}" for player in valid_players[:10]])
                await ctx.send(player_list)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                while True:
                    try:
                        pick_name = await self.bot.wait_for('message', check=check, timeout=60)
                        pick_name = pick_name.content.strip().lower()

                        if pick_name == 'show status':
                            await self.show_status(ctx)
                            continue

                        status, result = self.draft_process.user_draft(current_team, pick_name)

                        if status == "success":
                            await ctx.send(f"{self.draft_process.team_names[current_team]} picked {result.name}.")
                            break
                        elif status == "multiple":
                            await ctx.send("Multiple players found:")
                            multiple_players_msg = "\n".join([f"{player.name}, {player.position}, {player.team}, {player.ranking}" for player in result])
                            await ctx.send(multiple_players_msg)
                            await ctx.send("Enter the ranking of the player to choose (or type 'back' to go back):")
                            try:
                                pick_ranking = await self.bot.wait_for('message', check=check, timeout=60)
                                if pick_ranking.content.lower() == 'back':
                                    await ctx.send("Pick another player or type 'show status' to see current draft status.")
                                    continue  # Back to selecting player
                                pick = self.draft_process.handle_multiple_matches(result, pick_ranking.content.strip())
                                if pick and self.draft_process.rules.is_valid_player(current_team, pick):
                                    self.draft_process.finalize_pick(current_team, pick)
                                    await ctx.send(f"{self.draft_process.team_names[current_team]} picked {pick.name}.")
                                    break
                                else:
                                    await ctx.send("Invalid pick. Try again:")
                            except asyncio.TimeoutError:
                                await ctx.send("Ranking input timed out. Selecting the top available player automatically.")
                                pick = valid_players[0]
                                self.draft_process.finalize_pick(current_team, pick)
                                await ctx.send(f"{self.draft_process.team_names[current_team]} automatically picked {pick.name}.")
                                break
                        elif status == "none":
                            await ctx.send("No matches found. Enter part of the player's name again:")
                        elif status == "invalid":
                            if not self.draft_process.rules.max2(current_team, result):
                                await ctx.send("You cannot pick more than 2 players from the same team.")
                            elif not self.draft_process.rules.quota(current_team, result):
                                await ctx.send(f"You cannot exceed the quota for {result.position}.")
                            else:
                                await ctx.send("Invalid pick. Try again:")
                    except asyncio.TimeoutError:
                        await ctx.send(f"{self.draft_process.team_names[current_team]} took too long to pick. Selecting the top available player automatically.")
                        pick = valid_players[0]
                        self.draft_process.finalize_pick(current_team, pick)
                        await ctx.send(f"{self.draft_process.team_names[current_team]} automatically picked {pick.name}.")
                        break

            self.pick_count += 1
            if self.pick_count >= total_picks:
                await ctx.send("Draft completed!")
                self.draft_process.save_draft_results("draft_results.json")
                await self.show_status(ctx)
                break

    @commands.command()
    async def show_status(self, ctx):
        if self.draft_process is None:
            await ctx.send('Draft not started. Use !start_draft to start the draft.')
            return

        rounds = max(len(players) for players in self.draft_process.teams.values())
        df_data = {}
        for team in self.draft_process.teams:
            team_name = self.draft_process.team_names.get(team, team)
            picks = [player.name for player in self.draft_process.teams[team]]
            df_data[team_name] = picks + [""] * (rounds - len(picks))
        df = pd.DataFrame(df_data)
        await ctx.send(f"\nCurrent Draft Status:\n{df}")

    @commands.command()
    async def reset_draft(self, ctx):
        self.draft_process = None
        self.pick_count = 0
        self.how_many_person = 0
        self.current_person_index = 0
        self.person_names = []
        await ctx.send("Draft reset. Please start a new draft with !start_draft command.")

async def main():
    async with bot:
        await bot.add_cog(DraftBot(bot))
        await bot.start(token)

import asyncio
asyncio.run(main())
