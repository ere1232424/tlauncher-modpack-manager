import json
import os
from utils.resource_utils import resource_path

class Translator:
    def __init__(self):
        self.current_language = self._load_language_preference()
        self.translations = {}
        self._load_translations()

    def _load_language_preference(self):
        """Загружает сохраненный выбор языка"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get('language', 'ru')
        except Exception as e:
            print(f"Ошибка при загрузке настроек языка: {e}")
        return 'ru'  # По умолчанию русский

    def _save_language_preference(self):
        """Сохраняет выбранный язык в настройки"""
        try:
            settings = {}
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            settings['language'] = self.current_language
            
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении настроек языка: {e}")

    def _load_translations(self):
        """Загружает переводы для всех языков"""
        languages = ['ru', 'en']
        for lang in languages:
            try:
                with open(resource_path(f'translations/{lang}.json'), 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке переводов для языка {lang}: {e}")
                self.translations[lang] = {}

    def set_language(self, language):
        """Устанавливает язык и сохраняет выбор"""
        self.current_language = language
        self._save_language_preference()

    def translate(self, key):
        """Возвращает перевод для ключа на текущем языке"""
        try:
            # Разбиваем ключ на части для поддержки вложенных переводов
            parts = key.split('.')
            translation = self.translations.get(self.current_language, {})
            
            for part in parts:
                translation = translation.get(part, '')
                
            if not translation:
                # Если перевод не найден, возвращаем ключ
                return key
                
            return translation
        except Exception as e:
            print(f"Ошибка при получении перевода для ключа {key}: {e}")
            return key 