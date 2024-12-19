import re
from sys import argv

from PIL import Image, ImageDraw, ImageFont


def crop_white_borders(image_path):
    image = Image.open(image_path)
    image_rgb = image.convert("RGB")
    pixels = image_rgb.load()
    width, height = image_rgb.size

    left, top, right, bottom = width, height, 0, 0
    for x in range(width):
        for y in range(height):
            if pixels[x, y] != (255, 255, 255):  # 非白色像素
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)

    if left < right and top < bottom:
        image = image.crop((left, top, right + 1, bottom + 1))
    else:
        print("图片是完全空白的或纯白色")
    return image

def draw_title(title, image, output_path, zh_font="font/宋体粗.ttf", en_font="font/timesb.ttf"):
    if isinstance(image, str):
        image = Image.open(image)

    title_height = 50
    new_width, new_height = image.width, image.height + title_height
    new_image = Image.new("RGB", (new_width, new_height), color="white")
    new_image.paste(image, (0, title_height))

    draw = ImageDraw.Draw(new_image)

    try:
        font_chinese = ImageFont.truetype(zh_font, 36)
        font_english = ImageFont.truetype(en_font, 36)
    except IOError:
        raise IOError("无法加载字体文件，请确保路径正确并安装所需字体！")

    # 分离中文和非中文部分
    zh_pattern = r"[\u4e00-\u9fff\u3000-\u303f\uff01-\uff60\u2010-\u201f]+"
    en_pattern = r"[A-Za-z0-9!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~\s]+"
    segments = re.findall(
        zh_pattern + "|" + en_pattern,
        title
    )

    # 起始位置（居中排版）
    total_width = sum(
        (font_chinese.getbbox(seg)[2] if re.search(zh_pattern, seg) else font_english.getbbox(seg)[2])
        for seg in segments
    )
    x = (new_width - total_width) // 2
    yc = (title_height - font_chinese.size) // 2
    ascent, descent = font_english.getmetrics()
    ye = (title_height - font_english.size - descent) // 2

    # 绘制每段文字
    for seg in segments:
        if re.search(r'[\u4e00-\u9fff]', seg):  # 中文部分
            draw.text((x, yc), seg, font=font_chinese, fill="black")
            x += font_chinese.getbbox(seg)[2]
        else:  # 英文和数字部分
            draw.text((x, ye), seg, font=font_english, fill="black")
            x += font_english.getbbox(seg)[2]

    new_image.save(output_path)


if __name__ == "__main__":
    image_path = argv[1]
    output_path = image_path
    title = argv[2]

    image = crop_white_borders(image_path)
    draw_title(title, image, output_path)