from discord.ext import commands
import discord


def delete_message_after_invoke():
    async def predicate(ctx):
        await ctx.message.delete()
        return True

    return commands.check(predicate)


# In-memory dictionary to store bennies for the bank and users
bennies = {
    "bank": 8,  # Starting bennies for the bank
}


def setup(bot):
    @bot.command(aliases=["bal"])
    @delete_message_after_invoke()
    async def balance(ctx):
        # Get user's bennies count
        user_bennies = bennies.get(str(ctx.author.id), 0)

        embed = discord.Embed(
            title="Current Benny Balance",
            color=discord.Color.green(),
            description=f"**Bank bennies:** {bennies['bank']}\n**Your bennies:** {user_bennies}",
        )
        await ctx.send(embed=embed)

    @bot.command(aliases=["gb"])
    @delete_message_after_invoke()
    async def givebenny(ctx, amount: int, recipient: discord.User):
        if amount <= 0:
            await ctx.send("Amount must be greater than 0.")
            return

        if bennies["bank"] < amount:
            await ctx.send("Insufficient bennies in the bank.")
            return

        bennies["bank"] -= amount

        user_bennies = bennies.get(str(recipient.id), 0)
        bennies[str(recipient.id)] = user_bennies + amount

        embed = discord.Embed(
            title=f"Give {'Bennies' if amount > 1 else 'Benny'}",
            color=discord.Color.green(),
            description=f"{ctx.author.mention} has distributed {amount} {'bennies' if amount > 1 else 'benny'} to {recipient.mention}",
        )
        await ctx.send(embed=embed)

    @bot.command(aliases=["ub"])
    @delete_message_after_invoke()
    async def usebenny(ctx):
        user_bennies = bennies.get(str(ctx.author.id), 0)

        if user_bennies <= 0:
            await ctx.send("You don't have any bennies to use.")
            return

        bennies["bank"] += 1
        bennies[str(ctx.author.id)] = user_bennies - 1

        embed = discord.Embed(
            title="Use Benny",
            description=f"{ctx.author.mention} has used a bennie. It goes back to the bank.",
        )
        await ctx.send(embed=embed)
