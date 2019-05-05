import discord, config, youtube_dl
from sys import path

client = discord.Client()

stream_url = config.straem_url if (config.straem_url) else 'https://youtu.be/PRlAY486hVg'

class Song:
	def __init__(self, data):
		self.filename=data.get("filename")
		self.author=data.get("author")
		self.title=data.get("title")

	@classmethod
	async def create(cls, url, author, loop):
		ytdl = youtube_dl.YoutubeDL({"format": "bestaudio/best", "outtmpl": "audios/%(id)s.%(ext)s", "restrictfilenames": True, "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": True, "logtostderr": False, "quiet": True, "no_warnings": True, "default_search": "auto"})
		is_live = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
		is_live = is_live.get("is_live")
		data=await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not is_live))
		data["filename"] = data["url"] if is_live else ytdl.prepare_filename(data)
		data["author"] = author
		return cls(data)

@client.event
async def on_ready():
  song = await Song.create(stream_url, client.get_user(int(config.owner_id)), client.loop)
  await client.get_channel(int(config.voice_id)).connect()
  client.get_guild(int(config.guild_id)).voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.filename, executable=path[0]+'\\ffmpeg.exe', options='-vn')))
  await client.change_presence(activity=discord.Activity(name=song.title, type=discord.ActivityType.listening))

client.run(config.token, bot=config.is_bot)