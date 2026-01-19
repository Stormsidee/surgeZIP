from PIL import Image
import os

# Путь к вашему PNG с прозрачностью
png_path = "icon.png"

if not os.path.exists(png_path):
    print("Поместите ваш PNG с прозрачностью в файл 'icon.png' в корне проекта и запустите скрипт снова.")
    exit()

# Открываем PNG (с прозрачностью)
img = Image.open(png_path)

# Проверяем, есть ли альфа-канал
if img.mode != 'RGBA':
    print("PNG не имеет прозрачности. Сохраните в Photoshop как PNG-24 с прозрачностью.")
    exit()

# Конвертируем в ICO с несколькими размерами, сохраняя прозрачность
ico_path = "favicon.ico"
img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (256,256)])

print(f"Иконка создана: {ico_path} с сохранением прозрачности.")
size = os.path.getsize(ico_path)
print(f"Размер: {size} байт")