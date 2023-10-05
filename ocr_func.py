from paddleocr import PaddleOCR, draw_ocr


def ocr_singlefile():
    pic = "imgs/(1).png"
    ocr = PaddleOCR(lang="ch")
    result = ocr.ocr(pic, cls=True)
    quote_desc = result[-1][-1][0]
    return quote_desc


ocr_singlefile()
