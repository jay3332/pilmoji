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
