from paddleocr import PaddleOCR


def ocr_singlefile(pic):
    ocr = PaddleOCR(lang="ch")
    result = ocr.ocr(pic, cls=True)
    quote_desc = result[-1][-1][0]
    return quote_desc


def ocr_multiple_file(pic_list):
    ocr = PaddleOCR(lang="ch")
    results = []
    for pic in pic_list:
        result = ocr.ocr(pic, cls=True)
        quote_desc = result[-1][-1][0]
        results.append(quote_desc)
    return results
