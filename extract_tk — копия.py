import sys
import re
import pdfplumber
from pathlib import Path

# ---------- ТРАНСЛИТЕРАЦИЯ ----------
def transliterate_russian(text):
    mapping = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    return ''.join(mapping.get(ch, ch) for ch in text)

# ---------- ПАРСИНГ ----------
def extract_data_from_pdf(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    data = {}

    # 1. Номер заказа
    match = re.search(r'Neo\)\s*(\d+)', full_text) or re.search(r'[З3]АКАЗ.*?(\d+)', full_text)
    data['order'] = f"zak_{int(match.group(1)):04d}" if match else "zak_0000"

    # 2. Заказчик
    match = re.search(r'Заказчик\s+([А-Яа-яЁёA-Za-z]+(?:\s+[А-Яа-яЁёA-Za-z]+)*)', full_text)
    if match:
        raw = match.group(1).strip()
        translit = transliterate_russian(raw)
        words = translit.split()
        data['customer'] = ' '.join(word.capitalize() for word in words)
    else:
        data['customer'] = "Unknown"

    # 3. Номенклатура
    lines = full_text.split('\n')
    nomenklatura = []
    capture = False
    for line in lines:
        if 'НОМЕНКЛАТУРА' in line.upper() or 'Буклет' in line:
            capture = True
        if capture:
            if line.strip() == '' or 'Форм' in line:
                break
            nomenklatura.append(line.strip())
    data['nomenclature'] = '\n'.join(nomenklatura) if nomenklatura else "Не найдено"

    # 4. Формы
    match = re.search(r'Форм\s*(\d+)\s*ШТ', full_text, re.IGNORECASE)
    data['forms'] = f"{match.group(1)}pl" if match else "0pl"

    # 5. Формат листа (в мм)
    match = re.search(r'Формат\s*(\d+)\s*[хx]\s*(\d+)', full_text)
    if match:
        data['format_mm'] = f"{int(match.group(1)) * 10}х{int(match.group(2)) * 10}"
    else:
        match = re.search(r'(\d{3,})\s*[хx]\s*(\d{3,})', full_text)
        data['format_mm'] = f"{match.group(1)}х{match.group(2)}" if match else "Не найден"

    # 6. Потребность листов
    match = re.search(r'Потребность по рекламе\s*(\d+)', full_text, re.IGNORECASE) or \
            re.search(r'Потребность на тираж\s*(\d+)', full_text, re.IGNORECASE)
    if match:
        num = int(match.group(1))
        data['sheets'] = f"{num:,}".replace(',', ' ')
    else:
        data['sheets'] = "0"

    return data

# ---------- ЗАПИСЬ ОТЧЕТА ----------
def write_report(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Номер заказа: {data.get('order', '')}\n")
        f.write(f"Заказчик: {data.get('customer', '')}\n")
        f.write(f"Номенклатура продукции:\n{data.get('nomenclature', '')}\n")
        f.write(f"Количество форм: {data.get('forms', '')}\n")
        f.write(f"Формат листа (мм): {data.get('format_mm', '')}\n")
        f.write(f"Потребность листов в тираже: {data.get('sheets', '')}\n")

# ---------- ЗАПУСК ----------
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
    data = extract_data_from_pdf(pdf_path)

    order = data.get('order', 'zak_0000')
    customer = data.get('customer', 'Unknown').replace(' ', '_')
    forms = data.get('forms', '0pl')
    out_filename = f"{order}_{customer}_{forms}_.txt"

    output_dir = Path(pdf_path).parent
    out_path = output_dir / out_filename

    write_report(data, out_path)
    print(f"✅ Готово! Отчёт создан:\n{out_path}")
    input("Нажмите Enter для выхода...")