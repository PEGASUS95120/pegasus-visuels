import sys, json, os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS = sys.argv[1]
OUT = sys.argv[2]
W, H = 1080, 1350
BG = (12, 12, 14)
GOLD = (201, 162, 75)
WHITE = (255, 255, 255)
GREY = (170, 182, 204)

def pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise SystemExit("Police introuvable")

BOLD = pick("/usr/share/fonts/opentype/inter/Inter-Bold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
REG = pick("/usr/share/fonts/opentype/inter/Inter-Regular.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
SEMI = pick("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

M = 80
MW = W - 2 * M


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(draw, text, fnt, x, y, max_w, fill, gap):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * gap)
    return y


def make(name, tag, headline, sub, cta, note):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 14], fill=GOLD)

    # Logo en haut à droite
    logo = Image.open(os.path.join(HERE, "logo.png")).convert("RGB")
    lh = 210
    lw = int(logo.width * lh / logo.height)
    logo = logo.resize((lw, lh), Image.LANCZOS)
    mask = Image.new("L", (lw, lh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, lw, lh], radius=24, fill=255)
    top_y = 64
    img.paste(logo, (W - M - lw, top_y), mask)

    # Étiquette de la cible, en haut à gauche, centrée sur le logo
    tf = font(SEMI, 38)
    tw = d.textlength(tag, font=tf)
    pad_x, pad_y = 30, 18
    pill_h = tf.size + 2 * pad_y + 6
    pill_y = top_y + (lh - pill_h) // 2
    d.rounded_rectangle([M, pill_y, M + tw + 2 * pad_x, pill_y + pill_h],
                        radius=pill_h // 2, outline=GOLD, width=3)
    d.text((M + pad_x, pill_y + pad_y - 2), tag, font=tf, fill=GOLD)

    # Titre
    hf = font(BOLD, 80)
    y = 360
    y = block(d, headline, hf, M, y, MW, WHITE, 1.12)
    y += 30
    d.rectangle([M, y, M + 140, y + 8], fill=GOLD)
    y += 48

    # Sous-titre
    sf = font(REG, 46)
    y = block(d, sub, sf, M, y, MW, WHITE, 1.3)

    # Encadré d'appel à l'action
    cf = font(BOLD, 48)
    box_h = 250
    box_top = H - 150 - box_h
    d.rounded_rectangle([M, box_top, W - M, box_top + box_h], radius=26, fill=GOLD)
    d.text((M + 44, box_top + 36), cta, font=cf, fill=BG)
    line_y = box_top + 135
    d.rectangle([M + 44, line_y, W - M - 44, line_y + 3], fill=BG)
    infof = font(BOLD, 42)
    d.text((M + 44, line_y + 32), "pegasus-groupe.fr", font=infof, fill=BG)
    phone = "01 84 80 87 66"
    pw = d.textlength(phone, font=infof)
    d.text((W - M - 44 - pw, line_y + 32), phone, font=infof, fill=BG)

    # Mention légale en bas
    d.text((M, H - 100), note, font=font(REG, 26), fill=GREY)
    img.save(f"{OUT}/{name}", "PNG", optimize=True)



for p in json.load(open(POSTS, encoding="utf-8")):
    make(p["file"], p["tag"], p["headline"].replace(" ?", "\u00a0?"), p["sub"], p["cta"], p["note"])
print("ok")
