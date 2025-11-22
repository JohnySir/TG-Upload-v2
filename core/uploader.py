import os
import asyncio
import re
import logging
import traceback
from time import time
from PIL import Image
from pyrogram.types import InputMediaDocument, InputMediaVideo, InputMediaPhoto, InputMediaAudio
from pyrogram.errors import FloodWait, RPCError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.client import TgClient
from core.config import Config
from utils.file_utils import get_base_name, is_archive, get_path_size
from utils.media_utils import get_media_info, get_document_type, get_video_thumbnail, get_audio_thumbnail, get_image_thumbnail, get_md5_hash
from utils.status_utils import get_readable_file_size, get_readable_time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Uploader:
    def __init__(self, path, chat_id, topic_id=0, progress_callback=None, done_callback=None, log_callback=None):
        self.path = path
        self.chat_id = chat_id
        self.topic_id = int(topic_id) if topic_id else 0
        self.progress_callback = progress_callback
        self.done_callback = done_callback
        self.log_callback = log_callback
        self.client = TgClient.get_client()
        self.total_size = 0
        self.processed_bytes = 0
        self.start_time = time()
        self.is_cancelled = False
        
    def log(self, message, level="info"):
        # Log to console (detailed)
        if level == "error":
            logger.error(message)
        else:
            logger.info(message)
            
        # Log to GUI (simplified) if callback provided
        if self.log_callback:
            self.log_callback(message)

    async def progress(self, current, total):
        if self.is_cancelled:
            self.client.stop_transmission()
            return
        
        if self.progress_callback:
            speed = current / (time() - self.start_time) if time() > self.start_time else 0
            self.progress_callback(current, total, speed)

    async def upload(self):
        self.log(f"Starting upload for: {self.path}")
        if os.path.isfile(self.path):
            await self.upload_file(self.path)
        elif os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    if self.is_cancelled:
                        break
                    file_path = os.path.join(root, file)
                    await self.upload_file(file_path)
        
        if self.done_callback:
            self.done_callback()

    async def prepare_caption(self, file_path):
        filename = os.path.basename(file_path)
        caption = Config.CAPTION or filename
        
        size = get_readable_file_size(os.path.getsize(file_path))
        caption = caption.replace("{filename}", filename)
        caption = caption.replace("{size}", size)
        
        if Config.CAPTION_FONT:
            caption = f"<{Config.CAPTION_FONT}>{caption}</{Config.CAPTION_FONT}>"
            
        return caption

    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=8),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(Exception),
    )
    async def upload_file(self, file_path, force_document=False):
        if self.is_cancelled:
            return

        self.log(f"Uploading file: {os.path.basename(file_path)}")
        try:
            caption = await self.prepare_caption(file_path)
            
            # Thumbnail will be auto-generated based on file type
            thumb = None
            
            is_video, is_audio, is_image = await get_document_type(file_path)
            
            kwargs = {
                "chat_id": self.chat_id,
                "caption": caption,
                "progress": self.progress,
                "message_thread_id": self.topic_id if self.topic_id else None
            }

            if Config.AS_DOCUMENT or force_document or (not is_video and not is_audio and not is_image):
                self.log(f"DEBUG: Uploading as DOCUMENT. AS_DOCUMENT={Config.AS_DOCUMENT}, is_video={is_video}, is_audio={is_audio}, is_image={is_image}")
                
                # Auto-generate thumbnail based on file type
                if not thumb:
                    if is_video:
                        thumb = await get_video_thumbnail(file_path)
                    elif is_image:
                        thumb = await get_image_thumbnail(file_path)
                    if thumb:
                        self.log(f"Generated thumbnail: {thumb}")
                
                self.log(f"DEBUG: About to send_document with thumb={thumb}")
                await self.client.send_document(
                    document=file_path,
                    thumb=thumb,
                    force_document=True,
                    **kwargs
                )
            elif is_video:
                self.log(f"DEBUG: Uploading as VIDEO")
                duration = (await get_media_info(file_path))[0]
                
                # Auto-generate thumbnail if not already present
                if not thumb:
                    thumb = await get_video_thumbnail(file_path, duration)
                
                # Try to get actual video dimensions, fallback to default
                width, height = 1280, 720  # Default HD resolution
                try:
                    import subprocess
                    result = await cmd_exec([
                        "ffprobe",
                        "-v", "error",
                        "-select_streams", "v:0",
                        "-show_entries", "stream=width,height",
                        "-of", "csv=p=0",
                        file_path
                    ])
                    if result[2] == 0 and result[0]:
                        dimensions = result[0].strip().split(',')
                        if len(dimensions) == 2:
                            width, height = int(dimensions[0]), int(dimensions[1])
                except:
                    pass

                self.log(f"DEBUG: About to send_video with thumb={thumb}, dimensions={width}x{height}")
                await self.client.send_video(
                    video=file_path,
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=thumb,
                    supports_streaming=True,
                    **kwargs
                )
            elif is_audio:
                self.log(f"DEBUG: Uploading as AUDIO")
                duration, artist, title = await get_media_info(file_path)
                
                # Auto-generate thumbnail if not already present
                if not thumb:
                    thumb = await get_audio_thumbnail(file_path)
                    
                await self.client.send_audio(
                    audio=file_path,
                    duration=duration,
                    performer=artist,
                    title=title,
                    thumb=thumb,
                    **kwargs
                )
            elif is_image:
                self.log(f"DEBUG: Uploading as PHOTO")
                await self.client.send_photo(
                    photo=file_path,
                    **kwargs
                )
                
            # Cleanup generated thumbnail
            if thumb and os.path.exists(thumb):
                os.remove(thumb)
                
        except Exception as e:
            error_msg = str(e)
            if "PEER_ID_INVALID" in error_msg:
                error_msg += " (Hint: Is the bot added to this chat?)"
            self.log(f"Error uploading {os.path.basename(file_path)}: {error_msg}", level="error")
            logger.error(traceback.format_exc())
            raise e

    def cancel(self):
        self.is_cancelled = True
