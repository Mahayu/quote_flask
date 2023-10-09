import concurrent.futures
import threading

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


def ocr_multiple_images(image_data_list):
    results = {}
    threads = []
    max_threads = 5  # 设置最大线程数为5

    for image_data in image_data_list:
        if len(threads) >= max_threads:
            # 如果已经有最大线程数的线程在运行，等待一个线程结束
            threads[0].join()
            threads.pop(0)

        thread = threading.Thread(target=process_image, args=(image_data, results))
        thread.start()
        threads.append(thread)

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    return results


def process_image(image_data, results):
    try:
        quote_desc = ocr_single_image(image_data)
        results[image_data] = quote_desc
    except Exception as e:
        results[image_data] = str(e)
