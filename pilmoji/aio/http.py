import aiohttp
import asyncio
import typing
import unicodedata
from io import BytesIO
from ..classes import BaseRequester
import emoji

__all__ = [
    'AsyncRequester'
]


class AsyncRequester(BaseRequester):
    """
    Makes requests to fetch images using aiohttp.
    Use `Requester` for non-asynchronous requests.
    """
    def __init__(self, *, session: typing.Optional[aiohttp.ClientSession] = None, loop: typing.Optional[asyncio.AbstractEventLoop] = None, _microsoft=False):
        self.session: aiohttp.ClientSession = session or aiohttp.ClientSession(loop=loop)
        self.cache: typing.Dict[str, bytes] = {}
        self.loop: asyncio.AbstractEventLoop = loop
        self._microsoft = _microsoft

    async def _request(self, url) -> typing.Optional[BytesIO]:
        if url in self.cache:
            return BytesIO(self.cache[url])

        async with self.session.get(url) as response:
            if response.status == 200:
                stream = BytesIO(content := await response.read())
                self.cache[url] = content
                return stream

    async def get_twemoji(self, unicode: str) -> typing.Optional[BytesIO]:
        """
        Returns a stream of the given unicode emoji.
        :param unicode: The unicode emoji.
        :return: The bytes stream of that emoji.
        """
        hex_code = '-'.join(format(ord(ch), 'x') for ch in unicode)
        if not self._microsoft:
            url = self.BASE_URL + hex_code + '.png'
        else:
            name = emoji.demojize(unicode)[1:-1]
            name = name.lower().replace('_', '-')
            url = self.BASE_MICROSOFT_URL + name + f'_{hex_code}.png'
        return await self._request(url)

    async def get_discord_emoji(self, emoji_id: typing.Union[int, str]) -> typing.Optional[BytesIO]:
        """
        Returns a stream of the given Discord emoji.
        :param emoji_id: The emoji's ID.
        :return: A bytes stream of the emoji.
        """
        url = self.BASE_DISCORD_URL + str(emoji_id) + '.png?v=1'
        return await self._request(url)

    async def close(self):
        """
        Closes the aiohttp session.
        This will also delete the cache as it will become pointless.
        """
        await self.session.close()
        del self.session
        del self.cache

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
