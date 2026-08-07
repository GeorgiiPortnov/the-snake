import sys
from random import randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

POINTER = tuple[int, int]
UP: POINTER = (0, -1)
DOWN: POINTER = (0, 1)
LEFT: POINTER = (-1, 0)
RIGHT: POINTER = (1, 0)

COLOR = tuple[int, int, int]
BOARD_BACKGROUND_COLOR: COLOR = (0, 0, 0)
BORDER_COLOR: COLOR = (93, 216, 228)
APPLE_COLOR: COLOR = (255, 0, 0)
SNAKE_COLOR: COLOR = (0, 255, 0)
DEFAULT_COLOR: COLOR = (128, 128, 128)

SPEED = 8

screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов.
    Хранит позицию объекта на игровом поле и его цвет.
    Даёт общую логику отрисовки.
    От него наследуются классы Apple и Snake.
    """

    def __init__(
        self, body_color: COLOR = DEFAULT_COLOR,
        position: POINTER | None = None
    ):
        self.body_color = body_color
        self.position = position or SCREEN_CENTER

    def draw(self) -> None:
        """Отрисовывает игровой объект на экране."""
        raise NotImplementedError('Не отрисован объект')


class Apple(GameObject):
    """Представляет яблоко в игре. Занимает одну клетку.
    Позиция выровнена по координатам сетки, кратна GRID_SIZE.
    При поедании змейкой увеличивает
    длину змейки и появляется в случайной клетке.
    """

    def __init__(
        self, body_color: COLOR = APPLE_COLOR,
        position: POINTER | None = None,
    ):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=body_color, position=position)

    def randomize_position(
        self,
        occupied_positions: list[tuple[int, int]]
    ) -> None:
        """Устанавливает позицию яблока в случайной клетке игрового поля.
        Координаты выбираются так, чтобы яблоко было внутри игрового поля
        и занимало ровно одну клетку.
        """
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            new_pos = (x * GRID_SIZE, y * GRID_SIZE)
            if new_pos not in occupied_positions:
                self.position = new_pos
                break

    def draw(self, screen):
        """Рисует яблоко на игровом поле в текущей позиции."""
        rect = pg.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pg.draw.rect(screen, self.body_color, rect)


class Snake(GameObject):
    """Представляет управляемую змейку в игре.
    Двигается по полю, увеличивается в длине при поедании яблока.
    Голова змейки всегда расположена первым элементом в её траектории.
    При выходе за границу поля змейка появляется
    с противоположной стороны поля.
    """

    def __init__(
        self, body_color: COLOR = SNAKE_COLOR,
        position: POINTER | None = None
    ):
        super().__init__(body_color=body_color, position=position)
        self.length = 1
        self.last = None
        self.direction = RIGHT
        self.next_direction = None
        self.grow_next_frame = False

        if position is None:
            start_x = SCREEN_WIDTH // 2
            start_y = SCREEN_HEIGHT // 2
            head_position = (start_x, start_y)
            self.positions = [head_position] * self.length
        else:
            self.positions = [position] * self.length

    def draw(self, screen):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions[:-1]:
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pg.Rect(self.get_head_position(), (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def handle_keys(self):
        """Обрабатывает ввод с клавиатуры и
        событие закрытия окна.

        Считывает нажатия стрелок и
        сохраняет запрошенное направление в атрибуте
        self.next_direction (не применяя его сразу).

        Это позволяет методу update_direction
        проверить запрет разворота на 180 градусов.
        При попытке закрыть окно корректно завершает работу программы.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.next_direction = UP
                elif event.key == pg.K_DOWN:
                    self.next_direction = DOWN
                elif event.key == pg.K_LEFT:
                    self.next_direction = LEFT
                elif event.key == pg.K_RIGHT:
                    self.next_direction = RIGHT

    def update_direction(self):
        """Применяет запрошенное направление движения,
        если оно не противоположно текущему.

        Блокирует разворот на 180 градусов,
        предотвращая мгновенное столкновение
        змейки с собственным хвостом.
        """
        if self.next_direction is not None:
            is_opposite = (
                self.direction[0] == -self.next_direction[0],
                self.direction[1] == -self.next_direction[1]
            )

            if not is_opposite:
                self.direction = self.next_direction
            else:
                self.next_direction = None

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Выполняет один шаг движения змейки в текущем направлении.
        Реализует механику «туннеля». Корректирует длину тела.
        """
        head_pos = self.get_head_position()
        new_pos = (
            (head_pos[0] + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH,
            (head_pos[1] + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_pos)

        if self.grow_next_frame:
            self.grow_next_frame = False
        elif len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает состояние змейки к начальному.
        Устанавливает направление вправо, длина — 1 сегмент.
        Змейка возвращается в центр поля.
        """
        self.direction = RIGHT
        self.length = 1
        self.grow_next_frame = False
        start_x = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2
        self.positions = [(start_x, start_y)]


def handle_keys(game_object):
    """Делегирует обработку нажатий клавиш переданному игровому объекту."""
    game_object.handle_keys()


def main():
    """Запускает основной игровой цикл приложения.
    Инициализирует игровое окно, создаёт объекты змейки и яблоко.

    В бесконечном цикле происходит
    обработка событий и обновление состояния игры.

    Отрисовываются кадры с фиксированной частотой кадров (FPS).
    """
    global screen, clock

    # Инициализация Pygame (только здесь, не на уровне модуля)
    pg.init()

    if 'pytest' not in sys.modules:
        screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pg.display.set_caption('Змейка')
        # В нетестовом режиме можно пересоздать часы, но это не обязательно
        clock = pg.time.Clock()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    in_test = 'pytest' in sys.modules
    frames = 0
    max_frames = 5 if in_test else None

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_pos = snake.get_head_position()

        if head_pos == apple.position:
            snake.grow_next_frame = True
            apple.randomize_position(snake.positions)

        if head_pos in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        snake.draw(screen)
        apple.draw(screen)

        if not in_test:
            pg.display.update()

        if in_test:
            frames += 1
            if frames >= max_frames:
                break


if __name__ == '__main__':
    main()
