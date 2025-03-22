# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
import requests  # To shorten URLs
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

# TNLinks API
TNLINKS_API_KEY = "51926d8145e17454111c91391eb3f431e205fd91"
SHORTENER_API_URL = "https://tnlinks.in/api"

def shorten_url(long_url):
    """Shortens a given URL using TNLinks API"""
    try:
        params = {
            "api": TNLINKS_API_KEY,
            "url": long_url
        }
        response = requests.get(SHORTENER_API_URL, params=params)
        data = response.json()
        if data.get("shortenedUrl"):
            return data["shortenedUrl"]  # Return the shortened URL
    except Exception as e:
        logger.error(f"URL Shortening Failed: {e}")
    return long_url  # Fallback to original link

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
    chat_id = await active_connection(str(query.from_user.id))
    
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='🔔 Subscribe to use the bot!',
            switch_pm_parameter="subscribe"
        )
        return

    results = []
    query_text = query.query.strip()
    offset = int(query.offset or 0)
    files, next_offset, total = await get_search_results(chat_id, query_text, file_type=None, max_results=10, offset=offset)

    for file in files:
        file_name = file['file_name']
        file_size = get_size(file['file_size'])
        file_id = file['file_id']

        # Generate a fake direct URL (Replace with your real file URL logic)
        direct_url = f"https://t.me/{bot.username}?start=file_{file_id}"

        # Shorten the direct URL
        short_url = shorten_url(direct_url)

        caption = f"🎬 **{file_name}**\n📁 Size: {file_size}\n🔗 [Download Here]({short_url})"

        results.append(
            InlineQueryResultArticle(
                title=file_name,
                description=f"Size: {file_size}",
                input_message_content=InputTextMessageContent(
                    message_text=caption,
                    disable_web_page_preview=True
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Download", url=short_url)]
                ])
            )
        )

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
        if query_text:
            switch_pm_text += f" for {query_text}"
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
        except QueryIdInvalid:
            pass
        except Exception as e:
            logger.exception(str(e))
    else:
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=f'{emoji.CROSS_MARK} No results for "{query_text}"',
            switch_pm_parameter="okay"
        )
