import asyncio
from typing import Optional

from config import CLIENT_REQUEST_TIMEOUT, ENCODING, READ_BLOCK_SIZE, REQUEST_END
from exceptions import ReadTimeoutError


async def _read_data(reader: asyncio.StreamReader, block_size: int, separator: str) -> str:
    """Reads data from the stream until separator or eof"""
    request = b''
    separator_bytes = separator.encode(encoding=ENCODING)
    while True:
        next_block = await reader.read(block_size)
        request += next_block
        if not next_block or next_block.endswith(separator_bytes):
            return request.decode(encoding=ENCODING)


async def read_data_with_timeout(
        reader: asyncio.StreamReader,
        block_size: Optional[int] = READ_BLOCK_SIZE,
        separator: Optional[str] = REQUEST_END,
        timeout: Optional[int] = CLIENT_REQUEST_TIMEOUT,
) -> str:
    """Reads data from the stream assuming timeout"""
    try:
        request = await asyncio.wait_for(
            _read_data(reader=reader, block_size=block_size, separator=separator),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise ReadTimeoutError(f'Timeout exceeded while reading! Current {timeout=} seconds')

    return request
