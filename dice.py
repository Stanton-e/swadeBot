from discord.ext import commands
import random
import re


def delete_message_after_invoke():
    async def predicate(ctx):
        await ctx.message.delete()
        return True

    return commands.check(predicate)


def dice_roll(dice, sides):
    if dice <= 0:
        raise commands.CommandError("Dice must be greater than 0")
    if sides <= 0:
        raise commands.CommandError("Sides must be greater than 0")

    roll = [random.randint(1, sides) for _ in range(dice)]
    return sum(roll)


def roll_dice(dice_matches):
    rolls = []
    total = 0

    for dice_match in dice_matches:
        num_dice = int(dice_match[0])
        num_faces = int(dice_match[1])
        dice_result = dice_roll(num_dice, num_faces)
        rolls.append(f"{num_dice}d{num_faces} ({dice_result})")
        total += dice_result

    return rolls, total


def format_output(author, rolls, modifier_matches, total):
    output = f"{author.mention}\nRolling: {', '.join(rolls)}"

    if modifier_matches:
        modifiers = [f"{operator}{value}" for operator, value in modifier_matches]
        output += f" {' '.join(modifiers)}"

    output += f"\nTotal Result: {total}"
    return output


def setup(bot):
    @bot.command(aliases=["r"])
    @delete_message_after_invoke()
    async def roll(ctx, *args):
        cmd = " ".join(args)
        dice_matches = re.findall(r"(\d+)d(\d+)", cmd)
        modifier_matches = re.findall(r"([-+])(\d+)", cmd)

        if not dice_matches:
            raise commands.CommandError("No valid dice rolls found.")

        rolls, total = roll_dice(dice_matches)

        if modifier_matches:
            for operator, value in modifier_matches:
                value = int(value)
                if operator == "+":
                    total += value
                elif operator == "-":
                    total -= value

        output = format_output(ctx.author, rolls, modifier_matches, total)
        await ctx.send(output)
