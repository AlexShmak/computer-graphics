[![Code style & tests](https://github.com/AlexShmak/computer-graphics/actions/workflows/run_tests.yml/badge.svg)](https://github.com/AlexShmak/computer-graphics/actions/workflows/run_tests.yml)
---
# Котики
Приложение для симуляции и визуализации перемещения котов и их взаимодействия.

## Правила взаимодействия

Коты могут находиться в одном из следующих состояний:
> - WALK (гуляет, базовое состояние)
> - HISS (шипит на кота поблизости)
> - FIGHT (дерется с котом)
> - EAT (ест хлеб)
> - HIT (ударился об препятствие)
> - SLEEP (спит)

Коты передвигаются по полю хаотично, двигаясь по определенному направлению и за каждую итерацию отклоняясь на определенный угол. (Они находятся в состоянии WALK)

Взаимодействие котов осуществляется по следующим правилам:
- Если два кота находятся на расстоянии не превышающем R0, то они начинают драку. (Состоние FIGHT)
- Если два кота находятся на расстоянии R1, таком, что R1 > R0, они начинают шипеть с вероятностью обратно пропорциональной квадрату расстояния между ними. (Состоние HISS)
- На поле спавнится еда, если кот оказывается рядом с ней, он начинает есть и на время переходит в состояние EAT.
- Если кот сталкивается с преградой, то он на время застывает в состояни HISS.
- Иногда коты ложаться поспать и переходят в состояние SLEEP.

## Фичи

### Лабораторная работа 1

1. На карте могут быть препятствия, в которые врезаются коты.
2. Возможность произвольно рисовать эти препятствия перед началом симуляции.
3. Новые состояния для котов (кот может кушать, спать, врезаться в стенку и сидеть с больной головой после этого).
4. Охота за едой (на карте спавнится еда, которую могут кушать коты).
5. Интересное перемещение. Котики ходят по определенному направлению, отворачивая на небольшой угол.
6. При выходе за границы коты спавнятся с другой стороны карты (как в змейке).
7. Возможность ставить на паузу и продолжать симуляцию.

### Лабораторная работа 2

1. Поддержка трёх разных функций для рассчёта расстояния
    * Евклидово
    * Манхэттенское
    * Чебышёва

2. Плавная отрисовка перемещения котов
3. Возможность переключаться между режимами отображения котов (картинки и более производительный -- точки)
4. Приложение работает на 500к котов


## Демо-видео
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

## Docs
[Ссылка](https://github.com/AlexShmak/computer-graphics/blob/To_perfect/DOCS.md) на документацию

## License

This project is licensed under the [MIT License](LICENSE).
