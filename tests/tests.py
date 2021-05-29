from pilmoji import Pilmoji
from PIL import Image, ImageFont


my_string = '😎😎😎😎😎😎'

with Image.new('RGB', (550, 80), (255, 255, 255)) as image:
    font = ImageFont.truetype('arial.ttf', 24)

    with Pilmoji(image, use_microsoft_emoji=True) as pilmoji:
        w, h = Pilmoji.getsize(my_string, font)
        pilmoji.text((10, 10), my_string, (0, 0, 0), font)
        pilmoji.text((10+w, 10), 'hi', (0, 0, 0), font)

    image.show()
