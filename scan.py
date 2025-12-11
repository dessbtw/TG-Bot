def ObrabotkaPhoto(downloaded_image):
    import cv2
    import requests
    from pyzbar.pyzbar import decode
    import numpy
    
    tgimage = numpy.frombuffer(downloaded_image, numpy.uint8)
    img = cv2.imdecode(tgimage, cv2.IMREAD_COLOR)

    if img is None:
        return "Ошибка: не удалось декодировать изображение"

    barcodes = decode(img)

    if not barcodes:
        return "Штрих-код не найден"

    code = barcodes[0].data.decode('utf-8')

    if not code.isdigit():
        return "Найден код, но он не числовой: " + code

    url = f'https://world.openfoodfacts.net/api/v2/product/{code}.json'
    response = requests.get(url)
    data = response.json()

    if data.get("status") != 1:
        return f"Код: {code}\nПродукт не найден в базе"

    product = data["product"]

    text = f"Штрих-код: {code}\n"
    text += f"Название: {product.get('product_name')}\n"
    text += f"Бренд: {product.get('brands')}\n"
    text += f"Белки: {product.get('nutriments', {}).get('proteins_100g')}\n"
    text += f"Жиры: {product.get('nutriments', {}).get('fat_100g')}\n"
    text += f"Углеводы: {product.get('nutriments', {}).get('carbohydrates_100g')}\n"

    return text
