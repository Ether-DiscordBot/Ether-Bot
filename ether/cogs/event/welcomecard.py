import base64
import io
import os

import requests
from PIL import Image, ImageDraw, ImageFont


class WelcomeCard:
    BASE_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 16
    )
    WELCOME_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Bold.ttf"), 24
    )
    MASK = Image.open("ether/assets/mask.png", "r").convert("L").resize((100, 100))

    @classmethod
    def create_card(cls, user, guild):
        img = Image.new("RGBA", (400, 200), (231, 228, 220))

        # Profile Picture
        r = requests.get(user.display_avatar.with_size(256).url)
        pp = Image.open(io.BytesIO(r.content))
        pp = pp.resize((100, 100))

        img.paste(pp, (150, 25), cls.MASK)

        draw = ImageDraw.Draw(img)

        # Welcome Text
        draw.text(
            xy=(200, 140),
            text="Welcome!",
            fill=(64, 64, 64),
            font=cls.WELCOME_FONT,
            anchor="ma",
        )

        # Name
        draw.text(
            xy=(200, 170),
            text=f"{user.display_name[:20]}",
            fill=(64, 64, 64),
            font=cls.BASE_FONT,
            anchor="ma",
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            result = base64.b64encode(buffer.getvalue()).decode()
            return io.BytesIO(base64.b64decode(result))
