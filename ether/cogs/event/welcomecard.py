import base64
import io
import os

from PIL import Image, ImageDraw, ImageFont
import requests


class WelcomeCard:
    BASE_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 32
    )
    DISC_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Medium.ttf"), 24
    )
    WELCOME_FONT = ImageFont.truetype(
        os.path.abspath("ether/assets/fonts/Inter-Bold.ttf"), 48
    )
    MASK = Image.open("ether/assets/mask.png", "r").convert("L").resize((200, 200))

    @classmethod
    def create_card(cls, user, guild):
        img = Image.new("RGBA", (920, 500), (231, 228, 220))

        # Profile Picture
        r = requests.get(user.display_avatar.with_size(256).url)
        pp = Image.open(io.BytesIO(r.content))
        pp = pp.resize((200, 200))

        img.paste(pp, (380, 83), cls.MASK)

        draw = ImageDraw.Draw(img)

        # Welcome Text
        draw.text(
            xy=(460, 300),
            text="Welcome!",
            fill=(64, 64, 64),
            font=cls.WELCOME_FONT,
            anchor="ma",
        )

        name_size = (
            cls.BASE_FONT.getsize(user.name[:20])[0]
            + cls.DISC_FONT.getsize(f"#{user.discriminator}")[0]
        ) / 2

        # Pseudo
        # Name
        draw.text(
            xy=(460 - name_size, 380),
            text=f"{user.name[:20]}",
            fill=(64, 64, 64),
            font=cls.BASE_FONT,
        )

        # Discriminator
        draw.text(
            xy=(460 - name_size + cls.BASE_FONT.getsize(user.name[:20])[0], 388),
            text=f"#{user.discriminator}",
            fill=(125, 125, 125),
            font=cls.DISC_FONT,
        )

        # Convert to Base64
        with io.BytesIO() as buffer:
            img.save(buffer, format="PNG", quality=75)
            buffer.seek(0)
            result = base64.b64encode(buffer.getvalue()).decode()
            return io.BytesIO(base64.b64decode(result))
