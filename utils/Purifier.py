from io import BytesIO

from PIL.Image import Image as PImage
from PIL import Image, ImageEnhance
import requests

from exception import ImageError


def check_ratio(image: PImage, ratio):
    from math import floor
    width, height = image.size
    return floor(width * 10 / height) == floor(ratio * 10)


def crop_image(image: PImage) -> PImage:
    yaxis = [7.08, 1.58]
    xaxis = [4.17, 1.36]

    width, height = image.size
    yaxis_grid = [round(height / y, 0) for y in yaxis]
    xaxis_grid = [round(width / x, 0) for x in xaxis]

    title_level_button_image = image.crop((0, 0, xaxis_grid[1], yaxis_grid[0]))
    judge_detail_image = image.crop((0, yaxis_grid[0], xaxis_grid[0], yaxis_grid[1]))
    score_image = image.crop((xaxis_grid[0], yaxis_grid[1], xaxis_grid[1], height))

    enhancer = ImageEnhance.Sharpness(judge_detail_image)
    judge_detail_image = enhancer.enhance(10.0)

    new_width = title_level_button_image.width
    new_height = title_level_button_image.height + judge_detail_image.height

    new_image = Image.new("RGB", (new_width, new_height))
    new_image.paste(title_level_button_image, (0, 0))
    new_image.paste(judge_detail_image, (0, title_level_button_image.height))
    new_image.paste(score_image, (judge_detail_image.width, title_level_button_image.height))
    new_image.save("temp/crop.png")
    return new_image


def convert_base64_image(image: PImage) -> str:
    import base64
    import io

    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode("utf-8")


def purifier(image_url: str) -> str:
    try:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))
    except Exception as e:
        raise ImageError(f"이미지를 불러올 수 없습니다. {e}")
    if check_ratio(image, 16/9) is False:
        raise ImageError("이미지의 비율이 16:9가 아닙니다.")

    return convert_base64_image(crop_image(image))

def convert_thumbnail(image_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(image_bytes))

    # RGB로 변환 (JPG는 RGBA 지원 안 함)
    image = image.convert("RGB")

    # 80x80으로 리사이즈
    image = image.resize((80, 80))

    # 다시 바이트로 변환 (JPG로 저장)
    output_buffer = BytesIO()
    image.save(output_buffer, format="JPEG")
    output_buffer.seek(0)
    resized_bytes = output_buffer.read()
    return resized_bytes
