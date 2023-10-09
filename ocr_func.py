import concurrent.futures
from paddleocr import PaddleOCR
from io import BytesIO

# def ocr_singlefile(pic):
#     ocr = PaddleOCR(lang="ch")
#     result = ocr.ocr(pic, cls=True)
#     quote_desc = result[-1][-1][0]
#     return quote_desc


# def ocr_multiple_file(pic_list):
#     ocr = PaddleOCR(lang="ch")
#     results = []
#     for pic in pic_list:
#         result = ocr.ocr(pic, cls=True)
#         quote_desc = result[-1][-1][0]
#         results.append(quote_desc)
#     return results

def ocr_single_image(image_data):
    ocr = PaddleOCR(lang="ch")
    with BytesIO(image_data) as image_stream:
        result = ocr.ocr(image_stream, cls=True)
    quote_desc = result[-1][-1][0]
    return quote_desc


def ocr_multiple_file(image_data_list):
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 使用线程池并行处理图像数据
        futures = {executor.submit(ocr_single_image, image_data): image_data for image_data in image_data_list}
        for future in concurrent.futures.as_completed(futures):
            image_data = futures[future]
            try:
                quote_desc = future.result()
                results[image_data] = quote_desc
            except Exception as e:
                results[image_data] = str(e)  # 如果出现异常，将异常信息记录在结果中
    return results
