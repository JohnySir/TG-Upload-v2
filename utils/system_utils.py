import asyncio
from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from functools import partial, wraps

async def cmd_exec(cmd, shell=False):
    if shell:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=PIPE, stderr=PIPE
        )
    else:
        proc = await create_subprocess_exec(
            *cmd, stdout=PIPE, stderr=PIPE
        )
    stdout, stderr = await proc.communicate()
    return stdout.decode().strip(), stderr.decode().strip(), proc.returncode

def sync_to_async(func, *args, wait=True, **kwargs):
    pfunc = partial(func, *args, **kwargs)
    future = asyncio.get_event_loop().run_in_executor(None, pfunc)
    return future if wait else None
