import sys
from random import randint
import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

SPEED = 8

screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
class GameObject:
    """
    Базовый класс для игровых объектов.

    Хранит позицию объекта на игровом поле и его цвет.

    Дает общую логику отрисовки.

    От него наследуются классы Apple и Snake.
    """

    def __init__(self, body_color=(128, 128, 128), position=None):
        self.body_color = body_color
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position

    def draw(self):
        """Отрисовывает игровой объект на экране."""
        pass


class Apple(GameObject):
    """
    Представляет яблоко в игре.
    Занимает одну клетку. Позиция выровнена
    по координатам сетки, кратна GRID_SIZE.

    При поедании змейкой увеличивает
    длину змейки и появляется в случайной клетке.
    """

    def __init__(self):
        """Инициализирует яблоко: задает цвет и случайную позицию"""
        super().__init__(APPLE_COLOR, None)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает позицию яблока в случайной клетке игрового поля.

        Координаты выбираются так, чтобы яблоко было внутри игрового поля и
        занимало ровно одну клетку.
        """
        x = randint(0, GRID_WIDTH - 1)
        y = randint(0, GRID_HEIGHT - 1)
        self.position = (x * GRID_SIZE, y * GRID_SIZE)

    def draw(self, screen):
        """Рисует яблоко на игровом поле в текущей позиции."""
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(screen, self.body_color, rect)


class Snake(GameObject):
    """
    Представляет управляемую змейку в игре.

    Двигается по полю, увеличивается в длине при поедании яблока.
    Голова змейки всегда расположена первым элементом в ее траектории.
    При выходе за границу поля змейка
    появляется с противоположной стороны поля.
    """

    def __init__(
            self, positions=None,
            direction=RIGHT,
            length=1, next_direction=None,
            last=None):
        super().__init__(SNAKE_COLOR, None)
        self.length = length
        self.last = last
        self.direction = direction
        self.next_direction = next_direction
        if positions is None:
            start_x = (SCREEN_WIDTH // 2)
            start_y = (SCREEN_HEIGHT // 2)
            head_position = (start_x, start_y)
            self.positions = [head_position] * length
        else:
            if len(positions) != length:
                raise ValueError(
                    f'Длина змейки {len(positions)} '
                    'не совпадает с ожидаемой {length}!'
                )
            else:
                self.positions = positions

    def draw(self, screen):
        """Отрисовывает змейку на игровом поле"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def handle_keys(self):
        """
        Обрабатывает ввод с клавиатуры и событие закрытия окна.

        Считывает нажатия стрелок и сохраняет запрошенное направление
        в атрибуте self.next_direction (не применяя его сразу).

        Это позволяет методу update_direction
        проверить запрет разворота на 180 градусов.

        При попытке закрыть окно корректно завершает работу программы.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.next_direction = UP
                elif event.key == pygame.K_DOWN:
                    self.next_direction = DOWN
                elif event.key == pygame.K_LEFT:
                    self.next_direction = LEFT
                elif event.key == pygame.K_RIGHT:
                    self.next_direction = RIGHT

    def update_direction(self):
        """
        Применяет запрошенное направление движения,
        если оно не противоположно текущему.

        Блокирует разворот на 180 градусов,
        предотвращая мгновенное столкновение
        змейки с собственным хвостом.
        """
        if self.next_direction is not None:
            is_opposite = (
                self.direction[0] == -self.next_direction[0]
                and self.direction[1] == -self.next_direction[1]
            )

            if not is_opposite:
                self.direction = self.next_direction
            else:
                self.next_direction = None

    def get_head_position(self):
        """Возвращает текущие координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """
        Выполняет один шаг движения змейки в текущем направлении.

        Реализует механику «туннеля»: при выходе за границы поля змейка
        появляется с противоположной стороны.

        Корректирует длину тела: добавляет голову и удаляет хвост,
        если змейка не съела яблоко в этом кадре.
        """
        old_x, old_y = self.get_head_position()

        new_x = old_x + self.direction[0] * GRID_SIZE

        new_y = old_y + self.direction[1] * GRID_SIZE

        new_x = new_x % SCREEN_WIDTH

        new_y = new_y % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def check_collisions(self, apple):
        """
        Проверяет столкновения змейки с
        яблоком и собственным хвостом.
        """
        head_pos = self.get_head_position()

        if head_pos == apple.position:
            self.length += 1
            apple.randomize_position()
            return

        if head_pos in self.positions[1:]:
            self.reset()
            apple.randomize_position()

    def reset(self):
        """
        Сбрасывает состояние змейки к начальному.
        Устанавливает направление вправо, длина в 1 сегмент.

        Змейка возвращается в центр поля.
        """
        self.direction = RIGHT
        self.length = 1
        start_x = (SCREEN_WIDTH // 2)
        start_y = (SCREEN_HEIGHT // 2)
        self.positions = [(start_x, start_y)]


def handle_keys(game_object):
    """Делегирует обработку нажатий клавиш переданному игровому объекту."""
    game_object.handle_keys()


def main():
    """
    Запускает основной игровой цикл приложения.
    Инициализирует игровое окно, создает объекты змейки и яблоко.

    В бесконечном цикле происходит обработка событий и
    обновление состояния игры.
    Отрисовываются кадры с фиксированнной частотой кадров (FPS).
    """
    global screen

    pygame.init()

    # При реальном запуске создаём полноценное окно
    if 'pytest' not in sys.modules:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
        pygame.display.set_caption('Змейка')

    snake = Snake()
    apple = Apple()

    in_test = 'pytest' in sys.modules
    frames = 0
    max_frames = 5 if in_test else None

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)

        handle_keys(snake)

        snake.update_direction()

        snake.move()

        snake.check_collisions(apple)

        snake.draw(screen)
        apple.draw(screen)

        if not in_test:
            pygame.display.update()

        if in_test:
            frames += 1
            if frames >= max_frames:
                break


if __name__ == '__main__':
    main()
