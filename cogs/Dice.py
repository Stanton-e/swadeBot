from discord.ext import commands
import random
import re

DICE_RE = re.compile(r"(\d+)d(\d+)")
MODIFIER_RE = re.compile(r"([-+])(\d+)")


class InvalidDiceRoll(commands.CommandError):
    pass


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def dice_roll(self, dice: int, sides: int) -> int:
        if dice <= 0:
            raise InvalidDiceRoll("Dice must be greater than 0")
        if sides <= 0:
            raise InvalidDiceRoll("Sides must be greater than 0")

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
    @commands.bot_has_permissions(manage_messages=True)
    async def roll(self, ctx, *args):
        """Roll dice.

        Usage:
            !roll 1d20
            !roll 2d6+3
            !roll 2d6-1
            !roll 2d6 1d6-1
        """
        await ctx.message.delete()
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
