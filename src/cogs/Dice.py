from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import random
import re

load_dotenv()

MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))
DICE_RE = re.compile(r"(\d+)d(\d+)")
MODIFIER_RE = re.compile(r"([-+])(\d+)")


class InvalidDiceRoll(commands.CommandError):
    pass


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return (
            ctx.channel.id == MAIN_CHANNEL_ID
            and ctx.guild.me.guild_permissions.manage_messages
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            await ctx.message.delete()
        except discord.errors.NotFound:
            pass  # The message is already deleted.
        except discord.errors.Forbidden:
            pass  # Bot doesn't have the required permission to delete the message.

    def dice_roll(self, dice: int, sides: int) -> int:
        if dice <= 0:
            raise InvalidDiceRoll("Dice must be greater than 0")
        if sides <= 0:
            raise InvalidDiceRoll("Sides must be greater than 0")
        if dice > 10:
            raise InvalidDiceRoll("Cannot roll more than 10 dice at once")
        if sides > 100:
            raise InvalidDiceRoll("Dice faces cannot exceed 100")

        roll = [random.randint(1, sides) for _ in range(dice)]
        return sum(roll)

    def roll_dice(self, dice_matches: re.Match) -> tuple:
        rolls = []
        total = 0

        for dice_match in dice_matches:
            num_dice = int(dice_match[0])
            num_faces = int(dice_match[1])
            dice_result = self.dice_roll(num_dice, num_faces)
            rolls.append(f"{num_dice}d{num_faces} ({dice_result})")
            total += dice_result

        return rolls, total

    def calculate_total_with_modifiers(
        self, total: int, modifier_matches: re.Match
    ) -> int:
        for operator, value in modifier_matches:
            value = int(value)
            if operator == "+":
                total += value
            elif operator == "-":
                total -= value
            else:
                raise InvalidDiceRoll(f"Invalid operator: {operator}")

        return total

    def format_output(self, author, rolls, modifier_matches, total):
        output = f"{author.mention}\nRolling: {', '.join(rolls)}"

        if modifier_matches:
            modifiers = [f"{operator}{value}" for operator, value in modifier_matches]
            output += f" {' '.join(modifiers)}"

        output += f"\nTotal Result: {total}"
        return output

    @commands.command(aliases=["r"])
    async def roll(self, ctx, *args):
        """
        Description: Roll dice.

        Params:
        !r *args

        Example:
        !roll 1d20
        !roll 2d6+3
        !roll 2d6-1
        !roll 2d6 1d6-1
        """

        cmd = " ".join(args)
        dice_matches = DICE_RE.findall(cmd)
        modifier_matches = MODIFIER_RE.findall(cmd)

        if not dice_matches:
            raise InvalidDiceRoll("No valid dice rolls found.")

        rolls, total = self.roll_dice(dice_matches)
        total = self.calculate_total_with_modifiers(total, modifier_matches)

        output = self.format_output(ctx.author, rolls, modifier_matches, total)
        await ctx.send(output)

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, InvalidDiceRoll):
            await ctx.send(error)


async def setup(bot):
    await bot.add_cog(Dice(bot))
