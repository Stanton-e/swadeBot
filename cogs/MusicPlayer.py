from discord.ext import commands
import discord
import yt_dlp
import asyncio


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channel = None
        self.song_queue = []
        self.current_player = None

    async def join_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not currently in a voice channel")
            return False

        self.voice_channel = await ctx.author.voice.channel.connect()
        await ctx.send(f"Joined {ctx.author.voice.channel.name}")
        await ctx.message.delete()
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
                    source, after=self.play_next_song
                )
                await ctx.send(f"Now playing: {video_title}")
        except Exception as e:
            await ctx.send(f"An error occurred while processing your request: {str(e)}")
        await ctx.message.delete()

    def play_next_song(self, error=None):
        if len(self.song_queue) > 0:
            next_song = self.song_queue.pop(0)
            asyncio.run_coroutine_threadsafe(self.play_song(next_song), self.bot.loop)

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def leave(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not currently in a voice channel")
            return
        if self.voice_channel is None:
            await ctx.send("I am not currently in a voice channel")
            return
        await self.voice_channel.disconnect()
        await ctx.send("Left the voice channel")
        await ctx.message.delete()

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def play(self, ctx, *, url):
        if self.voice_channel is None or not self.voice_channel.is_connected():
            joined = await self.join_channel(ctx)
            if not joined:
                return

        if self.voice_channel.is_playing():
            self.song_queue.append(url)
            await ctx.send("Song added to queue")
        else:
            await self.play_song(ctx, url)
        await ctx.message.delete()

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def pause(self, ctx):
        if self.voice_channel.is_playing():
            self.voice_channel.pause()
            await ctx.send("Paused the song")
            await ctx.message.delete()

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def resume(self, ctx):
        if self.voice_channel.is_paused():
            self.voice_channel.resume()
            await ctx.send("Resumed the song")
            await ctx.message.delete()

    @commands.command()
    @commands.bot_has_permissions(manage_messages=True)
    async def skip(self, ctx):
        if self.voice_channel.is_playing():
            self.voice_channel.stop()
            await ctx.send("Skipped the song")
            await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
