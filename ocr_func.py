import concurrent.futures
import threading

from paddleocr import PaddleOCR
from io import BytesIO


def process_image(image_data, results):
    try:
        image_byte = image_data[0]
        uuid0 = image_data[1]

        ocr = PaddleOCR(lang="ch")
        with BytesIO(image_byte) as image_stream:
            result = ocr.ocr(image_stream.getvalue(), cls=True)[-1][-1][0]
            results[uuid0] = result
    except Exception as e:
        results[image_data] = str(e)


def ocr_multiple_images(ocr_items):
    results = {}
    threads = []
    max_threads = 5  # 设置最大线程数为5
    image_data_list = ocr_items
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
