# Pilmoji
Pilmoji is an emoji renderer for Pillow, Python's imaging library.  
It supports not only unicode emojis, but also Discord emojis.

Pilmoji uses [twemoji](https://github.com/twitter/twemoji) for unicode emojis.  
For Discord emojis, Pilmoji will send a request to Discord's CDN.  
Everything is cached, to ensure fast results.  

You can also use Microsoft's emojis instead of Twemoji, if that's what you prefer.

## Features
- Asynchronous support
- Multi-line support
- Discord emoji support
- Emoji position and size adjusting
- Twemoji __and__ Microsoft emoji support
- Caching

## Asynchronous Support
Pilmoji has both synchronous ([requests](https://pypi.org/project/requests/))
and asynchrounous ([aiohttp](https://pypi.org/project/aiohttp/)) support.  

## Installation
Pilmoji should be installed using `pip`:
``` 
pip install pilmoji
```
Installing from Github will most likely fail.

## Examples
### Basic usage
```py 
from pilmoji import Pilmoji
from PIL import Image, ImageFont


my_string = '''
Hello, world! 👋 Here are some emojis: 🎨 🌊 😎
I also support Discord emoji: <:rooThink:596576798351949847>
'''

with Image.new('RGB', (550, 80), (255, 255, 255)) as image:
    font = ImageFont.truetype('arial.ttf', 24)

    with Pilmoji(image) as pilmoji:
        pilmoji.text((10, 10), my_string.strip(), (0, 0, 0), font)

    image.show()
```
#### Result
![Example result](https://jay.has-no-bra.in/f/j4iEcc.png)
### Async usage
```py
import asyncio
from pilmoji import AsyncPilmoji
from PIL import Image, ImageFont

my_string = '''
Hello, world! 👋 Here are some emojis: 🎨 🌊 😎
I also support Discord emoji: <:rooThink:596576798351949847>
'''


async def main():
    with Image.new('RGB', (550, 80), (255, 255, 255)) as image:
        font = ImageFont.truetype('arial.ttf', 24)

        async with AsyncPilmoji(image) as pilmoji:
            await pilmoji.text((10, 10), my_string.strip(), (0, 0, 0), font)

        image.show()


asyncio.run(main())
```
Results are the exact same.
### Size/position adjustments
Is an emoji too low, or too small for a given font?  
You can also render emojis with offsets:
```py 
pilmoji.text((10, 10), my_string.strip(), (0, 0, 0), font,
             emoji_size_factor=1.15, emoji_position_offset=(0, -2))
```
### Using Microsoft emojis
Pilmoji also supports Microsoft emojis.  
Simply set the `use_microsoft_emoji` kwarg to True, as such:
```py 
with Pilmoji(image, use_microsoft_emoji=True) as pilmoji:
    ...
```
![results](https://jay.has-no-bra.in/f/suPfj0.png)
## Notes
- [async] If you're running PIL in an executor, use the **sync** version of Pilmoji instead.
- [async] It is not recommended to run PIL in asynchronous conditions (PIL is blocking.)
    - If you really have to, run the manipulation in an executor.
