#!/usr/bin/env python3
"""
Скрипт для регистрации ассоциаций файлов ModernArchiver в Windows.
Запустите этот скрипт с правами администратора.
"""

import sys
import os

# Добавляем путь к модулю
sys.path.insert(0, os.path.dirname(__file__))

from module.register_associations import register_file_associations, unregister_file_associations

if __name__ == "__main__":
    print("ModernArchiver - Регистрация ассоциаций файлов")
    print("=" * 50)
    print("1 - Зарегистрировать ассоциации файлов и контекстное меню")
    print("2 - Удалить ассоциации файлов и контекстное меню")
    print("0 - Выход")
    
    while True:
        try:
            choice = input("\nВыберите действие: ").strip()
            
            if choice == "1":
                print("\nРегистрация ассоциаций...")
                register_file_associations()
                break
            elif choice == "2":
                print("\nУдаление ассоциаций...")
                unregister_file_associations()
                break
            elif choice == "0":
                print("Выход.")
                break
            else:
                print("Неверный выбор. Попробуйте снова.")
        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            break