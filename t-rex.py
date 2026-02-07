import pygame
import random
import time
import sys
import os


def resource_path(relative_path):

    try:
        # PyInstaller создает временную папку в sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # В обычном режиме используем текущую директорию
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


pygame.init()

# Константы игры
DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
BACKGROUND_SPEED = 5
BASE_ENEMY_SPEED = -5  # Отрицательное значение - движение влево
BASE_ENEMY_SPAWN_DELAY = 2.0  # Базовая задержка появления врагов
SCORE_THRESHOLD = 10  # Порог счета для увеличения скорости
MAX_SPEED_MULTIPLIER = 3.0  # Максимальный множитель скорости
FPS = 60  # Частота кадров в секунду

# Настройка экрана
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption("Rex")

# Инициализация часов ДО использования
clock = pygame.time.Clock()

# Загрузка фона
background = pygame.image.load(resource_path("background.png"))
background = pygame.transform.scale(background, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
background_width = background.get_width()

# Позиции фона
background_x1_float = 0.0  # Первое изображение фона
background_x2_float = background_width  # Второе изображение фона
background_speed = BACKGROUND_SPEED

# Загрузка экрана окончания игры
game_over = pygame.image.load(resource_path("game_over.png"))
game_over = pygame.transform.scale(game_over, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

# Глобальные переменные для настроек
sound_enable = True  # Включен ли звук
difficulty = "easy"  # Текущий уровень сложности
difficulty_multipliers = {"easy": 1.0, "normal": 1.5, "hard": 2.0}

# ИНИЦИАЛИЗАЦИЯ ЗВУКОВ
# Настройка музыки
pygame.mixer.music.load(resource_path("Subway_Surfers.mp3"))
pygame.mixer.music.set_volume(0.05)

game_over_sound = pygame.mixer.Sound(resource_path("dark-souls.mp3"))
game_over_sound.set_volume(0.05)

jump_sound = pygame.mixer.Sound(resource_path("jump.mp3"))
jump_sound.set_volume(0.05)

coin_sound = pygame.mixer.Sound(resource_path("coin.mp3"))
coin_sound.set_volume(0.5)

speed_sound = pygame.mixer.Sound(resource_path("speed.mp3"))
speed_sound.set_volume(0.05)

# Загрузка анимаций динозавра
dino_anim = [
    pygame.image.load(resource_path("dino-0.png")),
    pygame.image.load(resource_path("dino-1.png")),
    pygame.image.load(resource_path("dino-2.png")),
]

# Загрузка анимаций птицы
bird_anim = [
    pygame.image.load(resource_path("bird1.png")),
    pygame.image.load(resource_path("bird2.png")),
    pygame.image.load(resource_path("bird3.png")),
    pygame.image.load(resource_path("bird4.png")),
]

# Загрузка изображений кактусов
kaktus_images = [
    pygame.image.load(resource_path("kaktus.png")),
    pygame.image.load(resource_path("kaktus2.png")),
    pygame.image.load(resource_path("kaktus3.png")),
]

# Масштабирование кактусов
kaktus_transform = []
for img in kaktus_images:
    scaled_kaktus = pygame.transform.scale(img, (100, 100))
    kaktus_transform.append(scaled_kaktus)

# Масштабирование динозавра
dino_transform = []
for img in dino_anim:
    scaled_dino = pygame.transform.scale(img, (100, 100))
    dino_transform.append(scaled_dino)

# Масштабирование птицы
bird_transform = []
for img in bird_anim:
    scaled_bird = pygame.transform.scale(img, (100, 100))
    bird_transform.append(scaled_bird)


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color=(100, 100, 100),
        hover_color=(150, 150, 255),
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False

    def draw(self, screen):
        """
        Отрисовывает кнопку на экране.
        """
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3, border_radius=10)

        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        """
        Проверяет, находится ли курсор мыши над кнопкой.
        """
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered

    def is_clicked(self, pos, event):
        """
        Проверяет, была ли кнопка нажата.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Dino:
    def __init__(self, animation_frames, position):
        self.animation_frames = animation_frames
        self.rect = self.animation_frames[0].get_rect()
        self.rect.center = position
        self.anim_count = 0  # Текущий кадр анимации
        self.base_anim_speed = 0.2  # Базовая скорость анимации
        self.anim_speed = self.base_anim_speed  # Текущая скорость анимации
        self.is_jumping = False  # Прыгает ли динозавр
        self.jump_height = 15  # Высота прыжка
        self.gravity = 0.6  # Гравитация для прыжка
        self.velocity_y = 0  # Вертикальная скорость

        # Хитбокс динозавра
        self.hitbox = pygame.Rect(0, 0, 50, 80)
        self.update_hitbox()

    def update(self, speed_multiplier=1.0):
        """
        Обновляет состояние динозавра.
        """
        self.anim_speed = self.base_anim_speed * speed_multiplier
        self.anim_count += self.anim_speed

        # Циклическая анимация
        if self.anim_count >= len(self.animation_frames):
            self.anim_count = 0

        # Физика прыжка
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

            # Приземление
            if self.rect.bottom >= 500:
                self.rect.bottom = 500
                self.is_jumping = False
                self.velocity_y = 0

        self.update_hitbox()

    def update_hitbox(self):
        """Обновляет положение хитбокса в соответствии со спрайтом."""
        self.hitbox.center = self.rect.center
        self.hitbox.x += 10  # Смещение для лучшего визуального соответствия
        self.hitbox.y += 10

    def draw(self, screen):
        """
        Отрисовывает динозавра на экране.
        """
        current_frame = self.animation_frames[int(self.anim_count)]
        screen.blit(current_frame, self.rect)

    def jump(self):
        """
        Запускает прыжок динозавра.
        Воспроизводит звук прыжка, если включен звук.
        """
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = -self.jump_height
            jump_sound.play()


class Enemy:
    def __init__(
        self, animation_frames, position, base_speed=BASE_ENEMY_SPEED, hitbox_scale=0.6
    ):
        self.animation_frames = animation_frames
        self.rect = self.animation_frames[0].get_rect(topleft=position)
        self.anim_count = 0
        self.base_anim_speed = 0.15
        self.anim_speed = self.base_anim_speed
        self.base_speed = base_speed  # ОТРИЦАТЕЛЬНОЕ значение для движения влево
        self.speed = base_speed
        self.float_x = float(position[0])  # Точная позиция для плавного движения

        # Хитбокс врага (меньше чем спрайт)
        self.hitbox_scale = hitbox_scale
        self.hitbox = pygame.Rect(
            0,
            0,
            int(self.rect.width * hitbox_scale),
            int(self.rect.height * hitbox_scale),
        )
        self.update_hitbox()

    def update(self, speed_multiplier=1.0):
        """
        Обновляет состояние врага.
        """
        self.anim_speed = self.base_anim_speed * speed_multiplier
        # Умножаем на множитель, но сохраняем отрицательное значение для движения влево
        speed_abs = abs(self.base_speed) * speed_multiplier
        self.speed = -speed_abs  # Всегда отрицательное для движения влево

        # Анимация
        self.anim_count += self.anim_speed
        if self.anim_count >= len(self.animation_frames):
            self.anim_count = 0

        # Движение - используем точное значение с плавающей точкой для плавности
        self.float_x += self.speed
        self.rect.x = int(self.float_x)  # Округляем только при отрисовке
        self.update_hitbox()

    def update_hitbox(self):
        """Обновляет положение хитбокса врага."""
        self.hitbox.center = self.rect.center

    def draw(self, screen):
        """
        Отрисовывает врага на экране.
        """
        current_frame = self.animation_frames[int(self.anim_count)]
        screen.blit(current_frame, self.rect)


class Bird(Enemy):
    def __init__(self, animation_frames, position):
        """
        Инициализация птицы.
        """
        # У птицы скорость выше, но ТОЖЕ ОТРИЦАТЕЛЬНАЯ
        super().__init__(animation_frames, position, base_speed=-8, hitbox_scale=0.5)
        # Случайная высота для птицы
        self.rect.y = random.randint(350, 400)
        self.float_x = float(position[0])  # Инициализируем точную позицию

    def update_hitbox(self):
        """
        Переопределение метода обновления хитбокса для птицы.
        Добавляет вертикальное смещение для лучшего визуального соответствия.
        """
        super().update_hitbox()
        self.hitbox.y += 15


class Kaktus(Enemy):
    def __init__(self, animation_frames, position):
        """
        Инициализация кактуса.
        """
        # Кактусы не анимируются - выбираем случайный спрайт
        single_frame = random.choice(animation_frames)
        # Кактус движется медленнее, но ТОЖЕ ВЛЕВО
        super().__init__(
            [single_frame], position, base_speed=BASE_ENEMY_SPEED, hitbox_scale=0.4
        )
        self.rect.bottom = 500  # Кактусы стоят на земле
        self.float_x = float(position[0])  # Инициализируем точную позицию

    def update_hitbox(self):
        """
        Переопределение метода обновления хитбокса для кактуса.
        Специальная настройка размеров и положения хитбокса.
        """
        super().update_hitbox()

        # Настройка размеров хитбокса кактуса
        self.hitbox.height = int(self.rect.height * 0.6)
        self.hitbox.width = int(self.rect.width * 0.5)

        # Позиционирование хитбокса у основания кактуса
        self.hitbox.midbottom = self.rect.midbottom
        self.hitbox.y -= 10  # Небольшое смещение вверх


def draw_text(surf, text, size, x, y, color="white"):
    """
    Рисует текст на указанной поверхности.
    """
    font_name = pygame.font.match_font("None")
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, False, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def update_game_speed(score, current_multiplier, difficulty_multiplier=1.0):
    """
    Обновляет скорость игры на основе счета и сложности.
    """
    # Базовый множитель в зависимости от сложности
    base_multiplier = difficulty_multiplier

    # Дополнительный множитель в зависимости от счета
    score_bonus = (score // SCORE_THRESHOLD) * 0.2

    # Итоговый множитель с ограничением по максимуму
    total_multiplier = base_multiplier + score_bonus
    speed_multiplier = min(total_multiplier, MAX_SPEED_MULTIPLIER)

    # Воспроизводим звук увеличения скорости при изменении множителя
    if speed_multiplier > current_multiplier:
        speed_sound.play()

    # Обновляем скорость фона
    new_background_speed = BACKGROUND_SPEED * speed_multiplier

    # Уменьшаем задержку между врагами
    base_spawn_delay = BASE_ENEMY_SPAWN_DELAY / difficulty_multiplier
    new_spawn_delay = max(base_spawn_delay / (1 + score_bonus), 0.3)

    return speed_multiplier, new_background_speed, new_spawn_delay


def create_random_enemy(current_time, last_spawn_time, spawn_delay, difficulty):
    """
    Создает случайного врага, если прошло достаточно времени с последнего спавна.
    """
    # Проверяем, можно ли создать нового врага
    if current_time - last_spawn_time >= spawn_delay:
        # В зависимости от сложности меняем вероятности появления врагов
        if difficulty == "hard":
            weights = [0.5, 0.5]  # Больше птиц на сложном уровне
        elif difficulty == "normal":
            weights = [0.4, 0.6]
        else:  # easy
            weights = [0.3, 0.7]

        # Случайный выбор типа врага с учетом весов
        enemy_type = random.choices(["bird", "kaktus"], weights=weights)[0]

        # Создаем врага в зависимости от типа
        if enemy_type == "bird":
            new_enemy = Bird(bird_transform, (DISPLAY_WIDTH, random.randint(350, 400)))
        else:
            new_enemy = Kaktus(kaktus_transform, (DISPLAY_WIDTH, 450))

        return new_enemy, current_time

    # Если враг не создан, возвращаем старое время
    return None, last_spawn_time


# Глобальные игровые переменные
dino = Dino(dino_transform, (100, 450))  # Создание экземпляра динозавра
enemies = []  # Список активных врагов
score = 0  # Текущий счет
last_enemy_time = time.time()  # Время последнего создания врага
speed_multiplier = 1.0  # Множитель скорости игры
background_speed = BACKGROUND_SPEED  # Текущая скорость фона
enemy_spawn_delay = BASE_ENEMY_SPAWN_DELAY  # Текущая задержка спавна врагов
game_active = True  # Активна ли игра
game_over_played = False  # Был ли воспроизведен звук окончания игры


def reset_game():
    """
    Сбрасывает все игровые переменные в начальное состояние.
    Вызывается при начале новой игры.
    """
    global enemies, score, last_enemy_time, speed_multiplier
    global background_speed, enemy_spawn_delay, background_x1_float, background_x2_float
    global game_over_played, game_active

    # Сбрасываем динозавра
    dino.rect.center = (100, 450)
    dino.is_jumping = False
    dino.velocity_y = 0
    dino.anim_count = 0

    # Сбрасываем другие переменные
    enemies.clear()
    score = 0
    last_enemy_time = time.time()
    speed_multiplier = 1.0
    background_speed = BACKGROUND_SPEED
    enemy_spawn_delay = BASE_ENEMY_SPAWN_DELAY
    background_x1_float = 0.0
    background_x2_float = background_width
    game_over_played = False
    game_active = True


def update_background_position():
    """
    Обновляет позицию бесшовного фона.
    Использует два изображения фона для создания эффекта бесконечного скролла.
    """
    global background_x1_float, background_x2_float, background_speed

    # Двигаем оба изображения фона
    background_x1_float -= background_speed
    background_x2_float -= background_speed

    # Сброс позиции, когда фон полностью ушел за экран
    if background_x1_float <= -background_width:
        background_x1_float += background_width * 2

    if background_x2_float <= -background_width:
        background_x2_float += background_width * 2


def main_menu():
    """
    Главное меню игры.
    """
    global sound_enable

    # Устанавливаем громкость в соответствии с сохраненным состоянием
    if sound_enable:
        pygame.mixer.music.set_volume(0.05)
        game_over_sound.set_volume(0.05)
        jump_sound.set_volume(0.05)
        coin_sound.set_volume(0.5)
        speed_sound.set_volume(0.05)
    else:
        pygame.mixer.music.set_volume(0)
        game_over_sound.set_volume(0)
        jump_sound.set_volume(0)
        coin_sound.set_volume(0)
        speed_sound.set_volume(0)

    # Запускаем фоновую музыку
    pygame.mixer.music.play(-1)

    # Создаем элементы интерфейса меню
    menu_font = pygame.font.Font(None, 74)
    title_text = menu_font.render("T-REX-GAME", True, (255, 255, 255))

    # Создаем кнопки меню
    start_button = Button(DISPLAY_WIDTH // 2 - 100, 200, 200, 50, "Start")
    options_button = Button(DISPLAY_WIDTH // 2 - 100, 300, 200, 50, "Settings")
    quit_button = Button(DISPLAY_WIDTH // 2 - 100, 400, 200, 50, "Exit")

    menu_running = True
    while menu_running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Обработка нажатий кнопок
            if start_button.is_clicked(mouse_pos, event):
                menu_running = False
                game_loop()  # Запускаем игру

            if options_button.is_clicked(mouse_pos, event):
                options_menu()  # Открываем меню настроек

            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()

        # Обновление фона даже в меню
        update_background_position()

        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(background, (int(background_x1_float), 0))
        screen.blit(background, (int(background_x2_float), 0))

        # Полупрозрачный слой для лучшей читаемости текста
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Отрисовка текста и кнопок
        screen.blit(title_text, (DISPLAY_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Обновление и отрисовка кнопок
        start_button.check_hover(mouse_pos)
        options_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        start_button.draw(screen)
        options_button.draw(screen)
        quit_button.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


def options_menu():
    """
    Меню настроек игры..
    """
    global sound_enable, difficulty

    # Создаем кнопки
    back_button = Button(DISPLAY_WIDTH // 2 - 125, 500, 250, 50, "Back")

    # Определяем цвета кнопок сложности в зависимости от текущей сложности
    easy_color = (0, 200, 0) if difficulty == "easy" else (100, 100, 100)
    normal_color = (255, 165, 0) if difficulty == "normal" else (100, 100, 100)
    hard_color = (200, 0, 0) if difficulty == "hard" else (100, 100, 100)

    # Кнопки выбора сложности
    speed_button = Button(
        DISPLAY_WIDTH // 2 - 125, 150, 250, 50, "Easy", color=easy_color
    )
    speed_button2 = Button(
        DISPLAY_WIDTH // 2 - 125, 200, 250, 50, "Normal", color=normal_color
    )
    speed_button3 = Button(
        DISPLAY_WIDTH // 2 - 125, 250, 250, 50, "Hard", color=hard_color
    )

    # Кнопки звука (цвет в зависимости от состояния)
    if sound_enable:
        music_on_button = Button(
            DISPLAY_WIDTH // 2 - 125, 400, 80, 50, "On", color=(0, 200, 0)
        )
        music_off_button = Button(DISPLAY_WIDTH // 2 - 25, 400, 80, 50, "Off")
    else:
        music_on_button = Button(DISPLAY_WIDTH // 2 - 125, 400, 80, 50, "On")
        music_off_button = Button(
            DISPLAY_WIDTH // 2 - 25, 400, 80, 50, "Off", color=(200, 0, 0)
        )

    options_running = True
    while options_running:
        mouse_pos = pygame.mouse.get_pos()

        # Обновляем фон для анимации
        update_background_position()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Обработка выбора сложности
            if speed_button.is_clicked(mouse_pos, event):
                difficulty = "easy"
                # Обновляем цвета кнопок для отображения выбора
                speed_button = Button(
                    DISPLAY_WIDTH // 2 - 125, 150, 250, 50, "Easy", color=(0, 200, 0)
                )
                speed_button2 = Button(DISPLAY_WIDTH // 2 - 125, 200, 250, 50, "Normal")
                speed_button3 = Button(DISPLAY_WIDTH // 2 - 125, 250, 250, 50, "Hard")

            if speed_button2.is_clicked(mouse_pos, event):
                difficulty = "normal"
                speed_button = Button(DISPLAY_WIDTH // 2 - 125, 150, 250, 50, "Easy")
                speed_button2 = Button(
                    DISPLAY_WIDTH // 2 - 125,
                    200,
                    250,
                    50,
                    "Normal",
                    color=(255, 165, 0),
                )
                speed_button3 = Button(DISPLAY_WIDTH // 2 - 125, 250, 250, 50, "Hard")

            if speed_button3.is_clicked(mouse_pos, event):
                difficulty = "hard"
                speed_button = Button(DISPLAY_WIDTH // 2 - 125, 150, 250, 50, "Easy")
                speed_button2 = Button(
                    DISPLAY_WIDTH // 2 - 125,
                    200,
                    250,
                    50,
                    "Normal",
                    color=(100, 100, 100),
                )
                speed_button3 = Button(
                    DISPLAY_WIDTH // 2 - 125, 250, 250, 50, "Hard", color=(200, 0, 0)
                )

            # Кнопка возврата в главное меню
            if back_button.is_clicked(mouse_pos, event):
                options_running = False

            # Обработка кнопок звука
            if music_off_button.is_clicked(mouse_pos, event):
                # Выключаем все звуки
                pygame.mixer.music.set_volume(0)
                game_over_sound.set_volume(0)
                jump_sound.set_volume(0)
                coin_sound.set_volume(0)
                speed_sound.set_volume(0)
                sound_enable = False

                # Обновляем цвета кнопок
                music_on_button = Button(DISPLAY_WIDTH // 2 - 125, 400, 80, 50, "On")
                music_off_button = Button(
                    DISPLAY_WIDTH // 2 - 25, 400, 80, 50, "Off", color=(200, 0, 0)
                )

            if music_on_button.is_clicked(mouse_pos, event):
                # Включаем звуки
                pygame.mixer.music.set_volume(0.05)
                game_over_sound.set_volume(0.05)
                jump_sound.set_volume(0.05)
                coin_sound.set_volume(0.05)
                speed_sound.set_volume(0.05)
                sound_enable = True

                # Обновляем цвета кнопок
                music_on_button = Button(
                    DISPLAY_WIDTH // 2 - 125, 400, 80, 50, "On", color=(0, 200, 0)
                )
                music_off_button = Button(DISPLAY_WIDTH // 2 - 25, 400, 80, 50, "Off")

        # Отрисовка
        screen.fill((0, 0, 0))
        screen.blit(background, (int(background_x1_float), 0))
        screen.blit(background, (int(background_x2_float), 0))

        # Полупрозрачный слой для лучшей читаемости
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Заголовок меню
        font = pygame.font.Font(None, 48)
        title = font.render("Settings", True, (255, 255, 255))
        screen.blit(title, (DISPLAY_WIDTH // 2 - title.get_width() // 2, 50))

        # Отображение текущей сложности
        diff_text = font.render(f"Complexity: {difficulty}", True, (255, 255, 255))
        screen.blit(diff_text, (DISPLAY_WIDTH // 2 - diff_text.get_width() // 2, 350))

        # Отрисовка кнопок
        back_button.check_hover(mouse_pos)
        back_button.draw(screen)
        music_off_button.draw(screen)
        music_on_button.draw(screen)
        speed_button.draw(screen)
        speed_button2.draw(screen)
        speed_button3.draw(screen)

        # Текст "Sound:"
        draw_text(screen, "Sound: ", 48, 200, 405, "white")

        pygame.display.flip()
        clock.tick(FPS)


def game_loop():
    """
    Основной игровой цикл.
    """
    global enemies, score, last_enemy_time, speed_multiplier
    global background_speed, enemy_spawn_delay, game_active, game_over_played
    global background_x1_float, background_x2_float

    # Получаем множитель сложности
    difficulty_multiplier = difficulty_multipliers[difficulty]

    # Сбрасываем игру при старте
    reset_game()

    running = True

    # Главный игровой цикл
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        dino.jump()  # Прыжок динозавра
                    else:
                        # Перезапуск игры после проигрыша
                        reset_game()
                        pygame.mixer.music.play(-1)

                if event.key == pygame.K_ESCAPE:
                    # Возврат в главное меню
                    pygame.mixer.music.play(-1)
                    game_over_sound.stop()
                    running = False
                    main_menu()
                    return

        # Обновление позиции фона
        update_background_position()

        # Отрисовка фона
        screen.fill((0, 0, 0))
        screen.blit(background, (int(background_x1_float), 0))
        screen.blit(background, (int(background_x2_float), 0))

        # Отображение информации на экране
        draw_text(screen, f"Score: {score}", 50, 650, 10)
        draw_text(screen, f"Complexity: {difficulty}", 25, 650, 50)

        if speed_multiplier > 1.0:
            draw_text(screen, f"Speed: {speed_multiplier:.1f}x", 20, 650, 80)

        if game_active:
            # Обновляем скорость игры с учетом выбранной сложности
            speed_multiplier, background_speed, enemy_spawn_delay = update_game_speed(
                score, speed_multiplier, difficulty_multiplier
            )

            # Обновление динозавра
            dino.update(speed_multiplier)

            # Создание нового врага с учетом сложности
            current_time = time.time()
            new_enemy, last_enemy_time = create_random_enemy(
                current_time, last_enemy_time, enemy_spawn_delay, difficulty
            )

            if new_enemy:
                enemies.append(new_enemy)

            # Обновление и удаление врагов
            for enemy in enemies[:]:
                enemy.update(speed_multiplier)

                # Проверка столкновений
                if dino.hitbox.colliderect(enemy.hitbox):
                    game_active = False

                    # Воспроизводим звук окончания игры только один раз
                    if not game_over_played:
                        pygame.mixer.music.stop()
                        game_over_sound.play()
                        game_over_played = True

                # Удаление врагов, вышедших за экран
                if enemy.rect.right < 0:
                    enemies.remove(enemy)
                    score += 1  # Увеличение счета
                    coin_sound.play()  # Звук получения очка

            # Отрисовка игровых объектов
            dino.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

        else:
            # Отображение экрана "Game Over"
            screen.blit(game_over, (0, 0))

            # Отображение финальной информации
            draw_text(screen, f"Final Score: {score}", 50, DISPLAY_WIDTH // 2, 100)
            draw_text(screen, f"Complexity: {difficulty}", 30, DISPLAY_WIDTH // 2, 150)
            draw_text(screen, "Press SPACE to restart", 30, DISPLAY_WIDTH // 2, 350)
            draw_text(screen, "Press ESC for menu", 30, DISPLAY_WIDTH // 2, 400)

        # Обновление экрана
        pygame.display.update()
        clock.tick(FPS)


# Запуск игры
if __name__ == "__main__":
    main_menu()
    pygame.quit()
