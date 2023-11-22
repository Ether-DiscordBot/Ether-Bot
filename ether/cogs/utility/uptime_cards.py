import io

import discord
import requests
from PIL import Image, ImageDraw2, ImageFont


class UptimeCards():
    def __init__(self):
        self.card: Image

        data = self._get_data()

        cards = []
        for monitor in data['psp']['monitors']:
            cards.append(self._build_card(monitor, data['days']))

        final_card = Image.new("RGB", (1000, 150*len(cards)))
        for idx, card in enumerate(cards):
            final_card.paste(card, (0, 150*idx))


        img_byte_arr = io.BytesIO()
        final_card.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr.seek(0)

        self.card = discord.File(
            fp=img_byte_arr, filename=f"monitors_card.png"
        )

    def _get_data(self, monitor_id: int | None = None):
        uri = "https://stats.uptimerobot.com/api/getMonitorList/yxDgrt60O3"
        if monitor_id:
            uri = "https://stats.uptimerobot.com/api/getMonitor/yxDgrt60O3" + "?m=" + str(monitor_id)

        r = requests.get(uri)

        if not r.ok:
            return None

        return r.json()

    def _build_card(self, monitor, days):
        b_font = ImageFont.truetype("ether/cogs/utility/assets/IBMPlexMono-Bold.ttf", size=14)
        m_font = ImageFont.truetype("ether/cogs/utility/assets/IBMPlexMono-Medium.ttf", size=12)

        im = Image.new("RGBA", size=(1000, 150), color=(255, 255, 255))

        row_length = len(monitor["dailyRatios"]) * 10
        side_margin = (1000-row_length)/2

        for idx, ratio in enumerate(monitor["dailyRatios"]):
            im_to_paste: Image
            match ratio["label"]:
                case "success":
                    im_to_paste = Pills.green()
                case "black":
                    im_to_paste = Pills.null()
                case _:
                    im_to_paste = Pills.red()

            im.alpha_composite(im_to_paste, (
                int(row_length + side_margin - (idx*10 + 8)),
                int(150/2 - 15)
            ))

        draw_im = ImageDraw2.Draw(im)

        ratio_90d = self._get_data(monitor["monitorId"])["monitor"]["90dRatio"]

        # Monitor name
        draw_im.draw.text((side_margin, 35), monitor["name"] + " | ", font=b_font, fill=(0, 0, 0), anchor="lm")

        # Monitor ratio
        name_length = b_font.getlength(monitor["name"] + " | ")
        ratio_color = "#3BD671" if float(ratio_90d["ratio"]) >= 50.0 else "#CE5350"
        draw_im.draw.text((side_margin + name_length, 35), ratio_90d["ratio"] + "%", font=b_font, fill=ratio_color, anchor="lm")

        # Monitor status
        status_color = "#3BD671" if ratio_90d["label"] == "success" else "#CE5350"
        status_text = "Operational" if ratio_90d["label"] == "success" else "Down"
        draw_im.draw.text((1000 - side_margin, 35), status_text, font=b_font, fill=status_color, anchor="rm")

        # Days
        draw_im.draw.text((side_margin, 95), days[len(days)-1], font=m_font, fill=(0, 0, 0), anchor="lt")
        draw_im.draw.text((1000-side_margin, 95), days[0], font=m_font, fill=(0, 0, 0), anchor="rt")

        return im

class Pills:
    NULL_PILL = Image.open("ether/cogs/utility/assets/null_pill.png").convert("RGBA")
    RED_PILL = Image.open("ether/cogs/utility/assets/red_pill.png").convert("RGBA")
    GREEN_PILL = Image.open("ether/cogs/utility/assets/green_pill.png").convert("RGBA")

    @classmethod
    def null(cls):
        return cls.NULL_PILL.copy()

    @classmethod
    def red(cls):
        return cls.RED_PILL.copy()

    @classmethod
    def green(cls):
        return cls.GREEN_PILL.copy()
