from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Optional, SupportsInt, TYPE_CHECKING, Tuple, Type, TypeVar, Union

from .helpers import NodeType, getsize, to_nodes
from .source import BaseSource, HTTPBasedSource, Twemoji, _has_requests

if TYPE_CHECKING:
    from io import BytesIO

    FontT = Union[ImageFont.ImageFont, ImageFont.FreeTypeFont, ImageFont.TransposedFont]
    ColorT = Union[int, Tuple[int, int, int], Tuple[int, int, int, int], str]


P = TypeVar('P', bound='Pilmoji')

__all__ = (
    'Pilmoji',
)


class Pilmoji:
    """The main emoji rendering interface.

    .. note::
        This should be used in a context manager.

    Parameters
    ----------
    image: :class:`PIL.Image.Image`
        The Pillow image to render on.
    source: Union[:class:`~.BaseSource`, Type[:class:`~.BaseSource`]]
        The emoji image source to use.
        This defaults to :class:`~.TwitterEmojiSource`.
    cache: bool
        Whether or not to cache emojis given from source.
        Enabling this is recommended and by default.
    draw: :class:`PIL.ImageDraw.ImageDraw`
        The drawing instance to use. If left unfilled,
        a new drawing instance will be created.
    render_discord_emoji: bool
        Whether or not to render Discord emoji. Defaults to `True`
    emoji_scale_factor: float
        The default rescaling factor for emojis. Defaults to `1`
    emoji_position_offset: Tuple[int, int]
        A 2-tuple representing the x and y offset for emojis when rendering,
        respectively. Defaults to `(0, 0)`
    """

    def __init__(
        self,
        image: Image.Image,
        *,
        source: Union[BaseSource, Type[BaseSource]] = Twemoji,
        cache: bool = True,
        draw: Optional[ImageDraw.ImageDraw] = None,
        render_discord_emoji: bool = True,
        emoji_scale_factor: float = 1.0,
        emoji_position_offset: Tuple[int, int] = (0, 0)
    ) -> None:
        self.image: Image.Image = image
        self.draw: ImageDraw.ImageDraw = draw

        if isinstance(source, type):
            if not issubclass(source, BaseSource):
                raise TypeError(f'source must inherit from BaseSource, not {source}.')

            source = source()

        elif not isinstance(source, BaseSource):
            raise TypeError(f'source must inherit from BaseSource, not {source.__class__}.')

        self.source: BaseSource = source

        self._cache: bool = bool(cache)
        self._closed: bool = False
        self._new_draw: bool = False

        self._render_discord_emoji: bool = bool(render_discord_emoji)
        self._default_emoji_scale_factor: float = emoji_scale_factor
        self._default_emoji_position_offset: Tuple[int, int] = emoji_position_offset

        self._emoji_cache: Dict[str, BytesIO] = {}
        self._discord_emoji_cache: Dict[int, BytesIO] = {}

        self._create_draw()

    def open(self) -> None:
        """Re-opens this renderer if it has been closed.
        This should rarely be called.

        Raises
        ------
        ValueError
            The renderer is already open.
        """
        if not self._closed:
            raise ValueError('Renderer is already open.')

        if _has_requests and isinstance(self.source, HTTPBasedSource):
            from requests import Session
            self.source._requests_session = Session()

        self._create_draw()
        self._closed = False

    def close(self) -> None:
        """Safely closes this renderer.

        .. note::
            If you are using a context manager, this should not be called.

        Raises
        ------
        ValueError
            The renderer has already been closed.
        """
        if self._closed:
            raise ValueError('Renderer has already been closed.')

        if self._new_draw:
            del self.draw
            self.draw = None

        if _has_requests and isinstance(self.source, HTTPBasedSource):
            self.source._requests_session.close()

        if self._cache:
            for stream in self._emoji_cache.values():
                stream.close()

            for stream in self._discord_emoji_cache.values():
                stream.close()

            self._emoji_cache = {}
            self._discord_emoji_cache = {}

        self._closed = True

    def _create_draw(self) -> None:
        if self.draw is None:
            self._new_draw = True
            self.draw = ImageDraw.Draw(self.image)

    def _get_emoji(self, emoji: str, /) -> Optional[BytesIO]:
        if self._cache and emoji in self._emoji_cache:
            entry = self._emoji_cache[emoji]
            entry.seek(0)
            return entry

        if stream := self.source.get_emoji(emoji):
            if self._cache:
                self._emoji_cache[emoji] = stream

            stream.seek(0)
            return stream

    def _get_discord_emoji(self, id: SupportsInt, /) -> Optional[BytesIO]:
        id = int(id)

        if self._cache and id in self._discord_emoji_cache:
            entry = self._discord_emoji_cache[id]
            entry.seek(0)
            return entry

        if stream := self.source.get_discord_emoji(id):
            if self._cache:
                self._discord_emoji_cache[id] = stream

            stream.seek(0)
            return stream

    def getsize(
        self,
        text: str,
        font: FontT = None,
        *,
        spacing: int = 4,
        emoji_scale_factor: float = None
    ) -> Tuple[int, int]:
        """Return the width and height of the text when rendered.
        This method supports multiline text.

        Parameters
        ----------
        text: str
            The text to use.
        font
            The font of the text.
        spacing: int
            The spacing between lines, in pixels.
            Defaults to `4`.
        emoji_scalee_factor: float
            The rescaling factor for emojis.
            Defaults to the factor given in the class constructor, or `1`.
        """
        if emoji_scale_factor is None:
            emoji_scale_factor = self._default_emoji_scale_factor

        return getsize(text, font, spacing=spacing, emoji_scale_factor=emoji_scale_factor)

    def text(
        self,
        xy: Tuple[int, int],
        text: str,
        fill: ColorT = None,
        font: FontT = None,
        anchor: str = None,
        spacing: int = 4,
        align: str = "left",
        direction: str = None,
        features: str = None,
        language: str = None,
        stroke_width: int = 0,
        stroke_fill: ColorT = None,
        embedded_color: bool = False,
        *args,
        emoji_scale_factor: float = None,
        emoji_position_offset: Tuple[int, int] = None,
        **kwargs
    ) -> None:
        """Draws the string at the given position, with emoji rendering support.
        This method supports multiline text.

        .. note::
            Some parameters have not been implemented yet.

        .. note::
            The signature of this function is a superset of the signature of Pillow's `ImageDraw.text`.

        .. note::
            Not all parameters are listed here.

        Parameters
        ----------
        xy: Tuple[int, int]
            The position to render the text at.
        text: str
            The text to render.
        fill
            The fill color of the text.
        font
            The font to render the text with.
        spacing: int
            How many pixels there should be between lines. Defaults to `4`
        emoji_scale_factor: float
            The rescaling factor for emojis. This can be used for fine adjustments.
            Defaults to the factor given in the class constructor, or `1`.
        emoji_position_offset: Tuple[int, int]
            The emoji position offset for emojis. The can be used for fine adjustments.
            Defaults to the offset given in the class constructor, or `(0, 0)`.
        """

        if emoji_scale_factor is None:
            emoji_scale_factor = self._default_emoji_scale_factor

        if emoji_position_offset is None:
            emoji_position_offset = self._default_emoji_position_offset

        if font is None:
            font = ImageFont.load_default()

        args = (
            fill,
            font,
            anchor,
            spacing,
            align,
            direction,
            features,
            language,
            stroke_width,
            stroke_fill,
            embedded_color,
            *args
        )

        x, y = xy
        original_x = x
        nodes = to_nodes(text)

        for line in nodes:
            x = original_x

            for node in line:
                content = node.content
                width, height = font.getsize(content)

                if node.type is NodeType.text:
                    self.draw.text((x, y), content, *args, **kwargs)
                    x += width
                    continue

                stream = None
                if node.type is NodeType.emoji:
                    stream = self._get_emoji(content)

                elif self._render_discord_emoji and node.type is NodeType.discord_emoji:
                    stream = self._get_discord_emoji(content)

                if not stream:
                    self.draw.text((x, y), content, *args, **kwargs)
                    x += width
                    continue

                with Image.open(stream).convert('RGBA') as asset:
                    width = int(emoji_scale_factor * font.size)
                    size = width, math.ceil(asset.height / asset.width * width)
                    asset = asset.resize(size, Image.ANTIALIAS)

                    ox, oy = emoji_position_offset
                    self.image.paste(asset, (x + ox, y + oy), asset)

                x += width
            y += spacing + font.size

    def __enter__(self: P) -> P:
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def __repr__(self) -> str:
        return f'<Pilmoji source={self.source} cache={self._cache}>'
