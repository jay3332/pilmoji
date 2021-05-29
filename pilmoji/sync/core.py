import typing
from gc import collect
from requests import Session
from .http import Requester
from ..classes import BasePilmoji
from ..helpers import get_nodes
from PIL import ImageFont, Image, ImageDraw


__all__ = [
    'Pilmoji'
]


class Pilmoji(BasePilmoji):
    """
    The synchronous emoji renderer.
    """
    def __init__(
            self,
            image: Image.Image,
            *,
            session: typing.Optional[Session] = None,
            use_microsoft_emoji: bool = False,
            render_discord_emoji: bool = True
    ):
        if not isinstance(image, Image.Image):
            raise TypeError(f'Image must be of type Image, got {type(image).__name__!r} instead.')

        self.render_discord_emoji: bool = render_discord_emoji
        self.http: Requester = Requester(session=session, _microsoft=use_microsoft_emoji)
        self.image: Image.Image = image
        self.draw = ImageDraw.Draw(image)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """
        Closes the requester and collects garbage.
        """
        self.http.close()
        collect()
        del self

    def text(self,
             xy: typing.Tuple[int, int],
             text: str,
             fill=None,
             font=None,
             anchor=None,
             spacing=4,
             align="left",
             direction=None,
             features=None,
             language=None,
             stroke_width=0,
             stroke_fill=None,
             embedded_color=False,
             emoji_size_factor=1,
             emoji_position_offset=(0, 0),
             *args, **kwargs) -> None:
        """
        Draws text with emoji rendering.
        Multiline text is supported.

        This function's signature is the exact same as PIL's, with a little bit of type-hinting.
        """
        if not font:
            font = ImageFont.load_default()

        args = (fill, font, anchor, spacing, align, direction,
                features, language, stroke_width, stroke_fill, embedded_color, *args)

        x, y = xy
        original_x = x
        lines = text.split('\n')
        nodes = get_nodes(lines)

        for line in nodes:
            x = original_x
            for node in line:
                content = node['content']
                width, height = font.getsize(content)
                if node['type'] == 'text':
                    self.draw.text((x, y), content, *args, **kwargs)
                else:
                    if node['type'] == 'twemoji':
                        stream = self.http.get_twemoji(content)
                    else:
                        stream = (
                            self.http.get_discord_emoji(content)
                            if self.render_discord_emoji else None
                        )

                    if not stream:
                        self.draw.text((x, y), content, *args, **kwargs)
                    else:
                        with Image.open(stream).convert("RGBA") as asset:
                            asset = asset.resize((width := int(emoji_size_factor * font.size), width), Image.ANTIALIAS)
                            box = x + emoji_position_offset[0], y + emoji_position_offset[1]
                            self.image.paste(asset, box, asset)

                x += width
            y += spacing + font.size
