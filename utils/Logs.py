from datetime import datetime

from utils import get_topic_channel


async def send_log(bot, log_text):
    bot_log_channel = get_topic_channel(bot, f"{bot.user.name}콘솔")

    if not bot_log_channel:
        print("Log channel is not set.")
        return

    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    for guild_channels in bot_log_channel.values():
        for channel in guild_channels:
            await channel.send(f"`{formatted_time}`│{log_text}")
