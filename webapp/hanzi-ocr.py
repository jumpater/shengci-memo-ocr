from PIL import Image, JpegImagePlugin
import sys, os
from fastapi import FastAPI, UploadFile, File
from starlette.requests import Request
import io
import pytesseract
import re
import jieba
import json

JpegImagePlugin._getmp = lambda x: None

convert_image = {
    1: lambda img: img,
    2: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),  # 左右反転
    3: lambda img: img.transpose(Image.ROTATE_180),  # 180度回転
    4: lambda img: img.transpose(Image.FLIP_TOP_BOTTOM),  # 上下反転
    5: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT).transpose(
        Image.ROTATE_90),  # 左右反転＆反時計回りに90度回転
    6: lambda img: img.transpose(Image.ROTATE_270),  # 反時計回りに270度回転
    7: lambda img: img.transpose(Image.FLIP_LEFT_RIGHT).transpose(
        Image.ROTATE_270),  # 左右反転＆反時計回りに270度回転
    8: lambda img: img.transpose(Image.ROTATE_90),  # 反時計回りに90度回転
}


def read_img(img):
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    text = pytesseract.image_to_string(img, lang="chi_sim")
    return (text)


app = FastAPI()


@app.get("/")
async def root():
    return "This is api of hanzi-ocr"


@app.post("/hanzi-ocr/")
async def prediction(request: Request, file: bytes = File(...)):
    if request.method == "POST":
        image_stream = io.BytesIO(file)
        image_stream.seek(0)
        img = Image.open(image_stream, formats=["JPEG", "PNG"])
        exif = img._getexif()
        orientation = exif.get(0x112, 1)
        img = convert_image[orientation](img)
        text = read_img(img)
        stopWords = [
            "一",
            "二",
            "三",
            "的",
        ]
        wordsList = []
        for word in jieba.cut_for_search(text):
            if (re.match("^[\u4E00-\u9FFF]+", word) and word not in stopWords):
                wordsList.append(word)
        return json.dumps(wordsList)
    return "No post request found"