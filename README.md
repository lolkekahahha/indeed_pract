# Автоматизированное тестирование сайта secby.ru

## Настройка окружения

1. Создайте виртуальное окружение и активируйте его:
```
python -m venv .venv
.venv\Scripts\activate
```

2. Установите зависимости:
```
pip install -r requirements.txt
```

3. Скопируйте шаблон конфигурации и заполните данные:
```
cp .env.example .env
```

## Запуск тестов

```
# Запуск всех тестов
pytest tests/ -v

# Запуск конкретного модуля
pytest tests/test_auth.py -v

# Запуск с подробным выводом (включая print)
pytest tests/ -v -s
```
