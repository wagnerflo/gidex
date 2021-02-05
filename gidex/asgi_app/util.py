from asyncio import get_running_loop

async def stream_file(func, *args):
    loop = get_running_loop()
    fp = await loop.run_in_executor(None, func, *args)
    while data := await loop.run_in_executor(None, fp.read, 16384):
        yield data
    await loop.run_in_executor(None, fp.close)
