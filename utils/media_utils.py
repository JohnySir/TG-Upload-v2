import os
import json
import asyncio
from PIL import Image
from time import time
from utils.system_utils import cmd_exec, sync_to_async
from utils.file_utils import get_mime_type, is_archive

async def get_media_info(path):
    try:
        result = await cmd_exec(
            [
                "ffprobe",
                "-hide_banner",
                "-loglevel",
                "error",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                path,
            ]
        )
        if result[2] != 0:
            return 0, None, None
            
        ffresult = json.loads(result[0])
        fields = ffresult.get("format")
        if fields is None:
            return 0, None, None
            
        duration = round(float(fields.get("duration", 0)))
        tags = fields.get("tags", {})
        artist = tags.get("artist") or tags.get("ARTIST") or tags.get("Artist")
        title = tags.get("title") or tags.get("TITLE") or tags.get("Title")
        return duration, artist, title
    except Exception as e:
        print(f"Error in get_media_info: {e}")
        return 0, None, None

async def get_document_type(path):
    is_video, is_audio, is_image = False, False, False
    if is_archive(path):
        return is_video, is_audio, is_image
        
    mime_type = get_mime_type(path)
    if mime_type.startswith("image"):
        return False, False, True
    
    if mime_type.startswith("audio"):
        return False, True, False
        
    if mime_type.startswith("video"):
        is_video = True
        
    return is_video, is_audio, is_image

async def get_video_thumbnail(video_file, duration=None):
    output_dir = "thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, f"{time()}.jpg")
    
    if duration is None:
        duration = (await get_media_info(video_file))[0]
    
    if duration == 0:
        duration = 3
    duration = duration // 2
    
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(duration),
        "-i",
        video_file,
        "-vf",
        "scale=640:-1",
        "-q:v",
        "5",
        "-vframes",
        "1",
        "-threads",
        "1",
        output,
    ]
    
    _, _, code = await cmd_exec(cmd)
    if code != 0 or not os.path.exists(output):
        return None
    return output

async def get_audio_thumbnail(audio_file):
    output_dir = "thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, f"{time()}.jpg")
    
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        audio_file,
        "-an",
        "-vcodec",
        "copy",
        output,
    ]
    
    _, _, code = await cmd_exec(cmd)
    if code != 0 or not os.path.exists(output):
        return None
    return output

def _generate_image_thumbnail(image_file, output):
    try:
        img = Image.open(image_file)
        img.thumbnail((320, 320))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output, "JPEG")
        return True
    except Exception as e:
        print(f"Error generating image thumbnail: {e}")
        return False

async def get_image_thumbnail(image_file):
    output_dir = "thumbnails"
    os.makedirs(output_dir, exist_ok=True)
    output = os.path.join(output_dir, f"{time()}.jpg")
    
    success = await sync_to_async(_generate_image_thumbnail, image_file, output)
    if success:
        return output
    return None

def get_md5_hash(path):
    import hashlib
    md5_hash = hashlib.md5()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()
