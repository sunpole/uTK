import sys
import re
from pathlib import Path
import easyocr
import fitz  # pymupdf

# ---------- ТРАНСЛИТЕРАЦИЯ ----------
def transliterate_russian(text):
    mapping = {
        'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'Yo',
        'Ж':'Zh','З':'Z','И':'I','Й':'Y','К':'K','Л':'L','М':'M',
        'Н':'N','О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U',
        'Ф':'F','Х':'Kh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Shch',
        'Ъ':'','Ы':'Y','Ь':'','Э':'E','Ю':'Yu','Я':'Ya',
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'yo',
        'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
        'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
        'ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya'
    }
    return ''.join(mapping.get(ch, ch) for ch in text)

# ---------- ИЗВЛЕЧЕНИЕ ТЕКСТА ЧЕРЕЗ OCR ----------
def extract_text_from_pdf_ocr(pdf_path):
    print("⏳ Запускается OCR (может занять 10–30 секунд)...")
    reader = easyocr.Reader(['ru', 'en'], gpu=False)
    doc = fitz.open(pdf_path)
    full_text = ""
    for i, page in enumerate(doc):
        print(f"   Распознавание страницы {i+1}...")
        pix = page.get_pixmap(dpi=200)
        img = pix.tobytes("png")
        result = reader.readtext(img, detail=0, paragraph=True)
        full_text += " ".join(result) + "\n"
    return full_text

# ---------- ПАРСИНГ ----------
def extract_data_from_text(full_text):
    data = {}

    # 1. Номер заказа – ищем "Ng", "№", "N" или просто "ЗАКАЗ" / "Техническое задание" + цифры
    match = re.search(r'(?:Техническое задание|ЗАКАЗ|Заказ)\s*[Nn]?[gг]?\s*(\d+)', full_text, re.IGNORECASE)
    if not match:
        match = re.search(r'Neo\)\s*(\d+)', full_text)
    if match:
        num = int(match.group(1))
        data['order'] = f"zak_{num:04d}"
    else:
        data['order'] = "zak_0000"

    # 2. Заказчик – ищем первое слово после "Заказчик" (оно должно быть "Полесье")
    match = re.search(r'Заказчик\s+([А-Яа-яЁёA-Za-z]+)', full_text)
    if match:
        raw = match.group(1).strip()
        # транслитерируем и делаем первую букву заглавной
        translit = transliterate_russian(raw)
        data['customer'] = translit.capitalize()
    else:
        # если не нашлось, ищем просто "Полесье" в любом месте
        if 'Полесье' in full_text:
            data['customer'] = 'Polesie'
        else:
            data['customer'] = "Unknown"

    # 3. Номенклатура – строки с "Буклет" и далее до "Процессы" или "РАСЧЕТ"
    lines = full_text.split('\n')
    nomenklatura = []
    capture = False
    for line in lines:
        if 'Буклет' in line:
            capture = True
        if capture:
            if 'Процессы' in line or 'РАСЧЕТ' in line or line.strip() == '':
                break
            nomenklatura.append(line.strip())
    data['nomenclature'] = '\n'.join(nomenklatura) if nomenklatura else "Не найдено"

    # 4. Количество форм
    match = re.search(r'Форм\s*(\d+)\s*ШТ', full_text, re.IGNORECASE)
    if match:
        data['forms'] = f"{match.group(1)}pl"
    else:
        data['forms'] = "0pl"

    # 5. Формат листа (в мм)
    match = re.search(r'(\d+)\s*[хx]\s*(\d+)', full_text)
    if match:
        w = int(match.group(1))
        h = int(match.group(2))
        # если числа меньше 100, считаем что это см → переводим в мм
        if w < 100 and h < 100:
            w *= 10
            h *= 10
        data['format_mm'] = f"{w}х{h}"
    else:
        data['format_mm'] = "Не найден"

    # 6. Потребность листов
    match = re.search(r'Потребность на тираж\s*(\d+)', full_text, re.IGNORECASE)
    if not match:
        match = re.search(r'Потребность по рекламе\s*(\d+)', full_text, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        data['sheets'] = f"{num:,}".replace(',', ' ')
    else:
        # запасной вариант: ищем четырёхзначные числа (исключаем тираж 10000)
        nums = re.findall(r'\b(\d{4,})\b', full_text)
        for n in nums:
            if n not in ['10000', '1000']:
                data['sheets'] = f"{int(n):,}".replace(',', ' ')
                break
        else:
            data['sheets'] = "0"

    return data

# ---------- ЗАПИСЬ ОТЧЁТА ----------
def write_report(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Номер заказа: {data.get('order', '')}\n")
        f.write(f"Заказчик: {data.get('customer', '')}\n")
        f.write(f"Номенклатура продукции:\n{data.get('nomenclature', '')}\n")
        f.write(f"Количество форм: {data.get('forms', '')}\n")
        f.write(f"Формат листа (мм): {data.get('format_mm', '')}\n")
        f.write(f"Потребность листов в тираже: {data.get('sheets', '')}\n")

# ---------- ТОЧКА ВХОДА ----------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Ошибка: перетащите PDF-файл на этот скрипт.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"❌ Файл не найден: {pdf_path}")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    print(f"⏳ Обработка: {Path(pdf_path).name} ...")
    full_text = extract_text_from_pdf_ocr(pdf_path)

    debug_path = Path(pdf_path).parent / "debug_ocr_text.txt"
    with open(debug_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f"🔍 Распознанный текст сохранён в: {debug_path}")

    data = extract_data_from_text(full_text)

    order = data.get('order', 'zak_0000')
    customer = data.get('customer', 'Unknown').replace(' ', '_')
    forms = data.get('forms', '0pl')
    out_filename = f"{order}_{customer}_{forms}_.txt"
    output_dir = Path(pdf_path).parent
    out_path = output_dir / out_filename

    write_report(data, out_path)
    print(f"✅ Готово! Отчёт создан:\n{out_path}")
    input("Нажмите Enter для выхода...")