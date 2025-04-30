import os
import shutil
import json

def ensure_directory_exists(path):
    """Создает директорию, если она не существует"""
    os.makedirs(path, exist_ok=True)

def copy_directory(src, dst):
    """Копирует директорию"""
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def save_json(data, filepath):
    """Сохраняет данные в JSON файл"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json(filepath):
    """Загружает данные из JSON файла"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f) 