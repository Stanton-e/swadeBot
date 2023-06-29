from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import yt_dlp
import asyncio

load_dotenv()

MAIN_CHANNEL_ID = int(os.getenv("MAIN_CHANNEL_ID"))


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = None
        self.song_queue = []
        self.current_player = None

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

    async def join_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not currently in a voice channel")
            return False

        self.voice_channel = await ctx.author.voice.channel.connect()
        await ctx.send(f"Joined {ctx.author.voice.channel.name}")
        return True

    async def play_song(self, ctx, song):
        ydl_opts = {"format": "bestaudio/best"}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(song, download=False)
                video_title = info_dict.get("title", None)
                video_url = info_dict.get("url", None)
                source = discord.FFmpegPCMAudio(executable="ffmpeg", source=video_url)
                self.current_player = self.voice_channel.play(
                    source, after=lambda e: self.play_next_song(ctx)
                )
                await ctx.send(f"Now playing: {video_title}")
        except Exception as e:
            await ctx.send(f"An error occurred while processing your request: {str(e)}")

    def play_next_song(self, ctx):
        if len(self.song_queue) > 0:
            next_song = self.song_queue.pop(0)
            asyncio.run_coroutine_threadsafe(
                self.play_song(ctx, next_song), self.bot.loop
            )

    @commands.command()
    async def leave(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not currently in a voice channel")
            return
        if self.voice_channel is None:
            await ctx.send("I am not currently in a voice channel")
            return
        await self.voice_channel.disconnect()
        await ctx.send("Left the voice channel")

    @commands.command()
    async def play(
        self, ctx, *, url=commands.parameter(description="URL of music source.")
    ):
        """
        Description: Play music.

        Params:
        !play URL

        Example:
        !play http://example.com
        """

        if self.voice_channel is None or not self.voice_channel.is_connected():
            joined = await self.join_channel(ctx)
            if not joined:
                return

        if self.voice_channel.is_playing():
            self.song_queue.append(url)
            await ctx.send("Song added to queue")
        else:
            await self.play_song(ctx, url)

    @commands.command()
    async def pause(self, ctx):
        """
        Description: Pause music.

        Params:
        N/A

        Example:
        !pause
        """

        if self.voice_channel.is_playing():
            self.voice_channel.pause()
            await ctx.send("Paused the song")

    @commands.command()
    async def resume(self, ctx):
        """
        Description: Resume music.

        Params:
        N/A

        Example:
        !resume
        """

        if self.voice_channel.is_paused():
            self.voice_channel.resume()
            await ctx.send("Resumed the song")

    @commands.command()
    async def skip(self, ctx):
        """
        Description: Skip to next song.

        Params:
        N/A

        Example:
        !skip
        """

        if self.voice_channel.is_playing():
            self.voice_channel.stop()
            await ctx.send("Skipped the song")

    @commands.command()
    async def next(self, ctx):
        """
        Description: Play next song.

        Params:
        N/A

        Example:
        !next
        """

        self.play_next_song(ctx)

    @commands.command()
    async def stop(self, ctx):
        """
        Description: Stop music.

        Params:
        N/A

        Example:
        !stop
        """

        self.song_queue.clear()
        self.voice_channel.stop()

    @commands.command()
    async def volume(
        self,
        ctx,
        volume: int = commands.parameter(
            description="Amount to lower/raise the volume.", default=25
        ),
    ):
        """
        Description: Set volume of the music.

        Params:
        !volume Amount

        Example:
        !volume 50
        """

        if self.voice_channel is None:
            return await ctx.send("I am not in a voice channel.")

        if self.voice_channel.source:
            self.voice_channel.source.volume = volume / 100
            await ctx.send(f"Set the volume to {volume}%")


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
