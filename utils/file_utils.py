import os
import re
from aiofiles.os import path as aiopath
from aioshutil import rmtree
import mimetypes

ARCH_EXT = [
    ".tar.bz2", ".tar.gz", ".bz2", ".gz", ".tar.xz", ".tar", ".tbz2", ".tgz", ".lzma2",
    ".zip", ".7z", ".z", ".rar", ".iso", ".wim", ".cab", ".apm", ".arj", ".chm", ".cpio",
    ".cramfs", ".deb", ".dmg", ".fat", ".hfs", ".lzh", ".lzma", ".mbr", ".msi", ".mslz",
    ".nsis", ".ntfs", ".rpm", ".squashfs", ".udf", ".vhd", ".xar", ".zst", ".zstd", ".cbz",
    ".apfs", ".ar", ".qcow", ".macho", ".exe", ".dll", ".sys", ".pmd", ".swf", ".swfc",
    ".simg", ".vdi", ".vhdx", ".vmdk", ".gzip", ".lzma86"
]

def is_archive(file):
    return file.strip().lower().endswith(tuple(ARCH_EXT))

def get_base_name(orig_path):
    extension = next(
        (ext for ext in ARCH_EXT if orig_path.strip().lower().endswith(ext)), ""
    )
    if extension != "":
        return re.split(f"{extension}$", orig_path, maxsplit=1, flags=re.I)[0]
    else:
        return os.path.splitext(orig_path)[0]

async def get_path_size(opath):
    total_size = 0
    if await aiopath.isfile(opath):
        return await aiopath.getsize(opath)
    for root, _, files in os.walk(opath):
        for f in files:
            abs_path = os.path.join(root, f)
            total_size += await aiopath.getsize(abs_path)
    return total_size

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "text/plain"
