[![Code style & tests](https://github.com/AlexShmak/computer-graphics/actions/workflows/run_tests.yml/badge.svg)](https://github.com/AlexShmak/computer-graphics/actions/workflows/run_tests.yml)
---
# Котики
Приложение для симуляции и визуализации перемещения котов и их состояний в зависимости от расстояния относительно друг друга.

Коты могут находиться в одном из следующих состояний:
> - WALK (гуляет, базовое состояние)
> - HISS (шипит на кота поблизости)
> - FIGHT (дерется с котом)
> - EAT (ест хлеб)
> - HIT (ударился об препятствие)
> - SLEEP (спит)

https://github.com/user-attachments/assets/7a09dd64-757d-4bec-91a4-7f198757d872

## Использование

### Установка зависимостей

```
pip install -r requirements.txt
```

### Запуск

```
python main.py
```

### Запуск тестов 

```
pytest .
```

## License

This project is licensed under the [MIT License](LICENSE).