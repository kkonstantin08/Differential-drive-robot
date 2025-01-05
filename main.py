import math
import random
import pygame


class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, map):
        pygame.draw.rect(map, (255, 0, 0), self.rect)


class ObstacleManager:
    def __init__(self, environment,count_objects):
        self.environment = environment
        self.obstacles = []
        self.generate_obstacles(count_objects)

    def generate_obstacles(self,count_objects):
        if count_objects == 0:
            # Максимум 3 препятствия
            num_obstacles = random.randint(0, 0)
        else:
            num_obstacles = random.randint(1, 3)

        for _ in range(num_obstacles):
            # Параметры препятствий
            width = random.randint(50, 150)
            height = random.randint(50, 150)

            # Избегаем края карты
            wall_thickness = self.environment.wall_thickness
            x = random.randint(wall_thickness + 50,
                               self.environment.width - wall_thickness - width - 50)
            y = random.randint(wall_thickness + 50,
                               self.environment.height - wall_thickness - height - 50)

            obstacle = Obstacle(x, y, width, height)
            self.obstacles.append(obstacle)

    def draw_obstacles(self, map):
        for obstacle in self.obstacles:
            obstacle.draw(map)


class Envir:
    def __init__(self, dimentions, wall_thickness):
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.red = (255, 0, 0)
        self.yel = (255, 255, 0)
        self.height = dimentions[0]
        self.width = dimentions[1]
        self.wall_thickness = wall_thickness
        pygame.display.set_caption("Differential drive robot")
        self.map = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.Font('freesansbold.ttf', 50)
        self.text = self.font.render('default', True, self.white, self.black)
        self.textRect = self.text.get_rect()
        self.textRect.center = (dimentions[1] - 600, dimentions[0] - 100)
        self.trail_set = []

    def draw_walls(self):
        pygame.draw.rect(self.map, self.white, (0, 0, self.width, self.wall_thickness))  # Top wall
        pygame.draw.rect(self.map, self.white, (0, 0, self.wall_thickness, self.height))  # Left wall
        pygame.draw.rect(self.map, self.white,
                         (0, self.height - self.wall_thickness, self.width, self.wall_thickness))  # Bottom wall
        pygame.draw.rect(self.map, self.white,
                         (self.width - self.wall_thickness, 0, self.wall_thickness, self.height))  # Right wall

    def write_info(self, Vl, Vr, theta):
        txt = f"Vl = {Vl} Vr = {Vr} theta = {int(math.degrees(theta))}"
        self.text = self.font.render(txt, True, self.white, self.black)
        self.map.blit(self.text, self.textRect)

    def trail(self, pos):
        for i in range(0, len(self.trail_set) - 1):
            pygame.draw.line(self.map, self.yel, (self.trail_set[i][0], self.trail_set[i][1]),
                             (self.trail_set[i + 1][0], self.trail_set[i + 1][1]), width=40)
        self.trail_set.append(pos)


class Robot:
    def __init__(self, startpos, robotImg, width):
        self.m2p = 3779.52
        self.w = width
        self.x, self.y = startpos
        self.theta = 0
        self.vl = 0.09 * self.m2p
        self.vr = 0.09 * self.m2p
        self.direction = 1  # 1 = вправо, -1 = влево
        self.vertical_step = 50  # шаг вверх при смене строки
        self.finished_snake = False  # Флаг завершения змейки
        self.maxspeed = 0.1 * self.m2p
        self.minspeed = -0.09 * self.m2p
        self.count = 0  # кол-во разворотов
        self.is_turning = False

        # Графика
        self.img = pygame.image.load(robotImg)
        self.rotated = self.img
        self.rect = self.rotated.get_rect(center=(self.x, self.y))
        self.radius = max(self.rect.width, self.rect.height) / 2

    def turn_right(self):
        self.is_turning = True
        self.vr = 0
        self.vl = 0.04 * self.m2p
        for i in range(15):
            self.theta += ((self.vr - self.vl) / self.w * dt) / 2
            # Обновляем изображение робота
            self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
            self.rect = self.rotated.get_rect(center=(self.x, self.y))
            if int(math.degrees(self.theta)) <= -180:
                self.vr = 0.08 * self.m2p
                self.vl = 0.08 * self.m2p
                self.count += 1
                self.theta = -math.pi
                break
        self.is_turning = False
    def turn_left(self):
        self.is_turning = True
        self.vl = 0
        self.vr = 0.04 * self.m2p
        for i in range(15):
            self.theta += ((self.vr - self.vl) / self.w * dt) / 2
            # Обновляем изображение робота
            self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
            self.rect = self.rotated.get_rect(center=(self.x, self.y))
            if int(math.degrees(self.theta)) >= 0:
                self.vl = 0.08 * self.m2p
                self.vr = 0.08 * self.m2p
                self.theta = 0
                break
        self.is_turning = False

    def move_autonomous(self, dt, environment):
        # Базовые параметры движения
        base_speed = 0.08 * self.m2p

        # Расчет нового положения
        new_x = self.x + ((self.vl + self.vr) / 2) * math.cos(self.theta) * dt
        new_y = self.y - ((self.vl + self.vr) / 2) * math.sin(self.theta) * dt

        if new_x + 50 > environment.width - environment.wall_thickness:
            self.turn_right()
            for _ in range(2):
                if int(math.degrees(self.theta)) > -180 and self.is_turning == False:
                    self.turn_right()
                else:
                    break

        if new_x - 50 < environment.wall_thickness and self.count != 0:
            self.turn_left()
            for _ in range(2):
                if int(math.degrees(self.theta)) < 0 and self.is_turning == False:
                    self.turn_left()
                else:
                    break
        if self.check_bottom_wall(new_x,new_y,environment):
            self.vr = 0
            self.vl = 0
            self.theta = 0


        # Расширенная проверка столкновения
        robot_rect = pygame.Rect(new_x - self.radius, new_y - self.radius,
                                 self.radius * 2, self.radius * 2)

        for obstacle in obstacle_manager.obstacles:
            if robot_rect.colliderect(obstacle.rect):
                # Расширенный анализ препятствия
                obstacle_center_x = obstacle.x + obstacle.width / 2
                obstacle_center_y = obstacle.y + obstacle.height / 2

                # Точный расчет расстояний и зазоров
                dist_to_top = abs(self.y - obstacle.y)
                dist_to_bottom = abs(self.y - (obstacle.y + obstacle.height))

                # Расчет свободного пространства с запасом
                space_margin = self.radius * 2

                # Проверка свободного пространства с учетом краевых случаев
                space_above = (
                        obstacle.x - space_margin > environment.wall_thickness and
                        obstacle.x + obstacle.width + space_margin < environment.width - environment.wall_thickness and
                        obstacle.y - space_margin > environment.wall_thickness
                )

                space_below = (
                        obstacle.x - space_margin > environment.wall_thickness and
                        obstacle.x + obstacle.width + space_margin < environment.width - environment.wall_thickness and
                        obstacle.y + obstacle.height + space_margin < environment.height - environment.wall_thickness
                )

                # Плавный поворот с интерполяцией
                def smooth_turn(target_angle, steps=30):
                    current_angle = self.theta
                    angle_diff = target_angle - current_angle

                    for _ in range(steps):
                        # Интерполяция угла
                        self.theta += angle_diff / steps

                        # Плавное изменение скорости
                        self.vl = base_speed * math.cos(self.theta)
                        self.vr = base_speed * math.sin(self.theta)

                        # Обновление изображения
                        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
                        self.rect = self.rotated.get_rect(center=(self.x, self.y))

                        # Небольшая задержка для плавности
                        pygame.time.delay(10)

                # Интеллектуальный выбор траектории
                if space_above and space_below:
                    # Выбор кратчайшего пути с учетом текущего положения
                    if dist_to_top <= dist_to_bottom:
                        # Объезд сверху
                        smooth_turn(-math.pi / 2)
                        new_x = obstacle.x - self.radius
                        new_y = obstacle.y - self.radius
                    else:
                        # Объезд снизу
                        smooth_turn(math.pi / 2)
                        new_x = obstacle.x - self.radius
                        new_y = obstacle.y + obstacle.height + self.radius

                elif space_above:
                    # Объезд сверху
                    smooth_turn(-math.pi / 2)
                    new_x = obstacle.x - self.radius
                    new_y = obstacle.y - self.radius

                elif space_below:
                    # Объезд снизу
                    smooth_turn(math.pi / 2)
                    new_x = obstacle.x - self.radius
                    new_y = obstacle.y + obstacle.height + self.radius

                else:
                    # Сложный случай - полный объезд
                    if new_x > obstacle_center_x:
                        # Объезд по часовой стрелке
                        smooth_turn(math.pi)
                    else:
                        # Объезд против часовой стрелки
                        smooth_turn(-math.pi)

                    # Дополнительная проверка на возможность объезда
                    if not self.check_full_path_clear(obstacle, environment):
                        # Экстренная остановка
                        self.vl = 0
                        self.vr = 0
                        return

                return

        # Стандартное движение
        self.x, self.y = new_x, new_y
        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def check_full_path_clear(self, obstacle, environment):
        check_points = [
            (obstacle.x - self.radius * 2, obstacle.y - self.radius * 2),
            (obstacle.x + obstacle.width + self.radius * 2, obstacle.y - self.radius * 2),
            (obstacle.x - self.radius * 2, obstacle.y + obstacle.height + self.radius * 2),
            (obstacle.x + obstacle.width + self.radius * 2, obstacle.y + obstacle.height + self.radius * 2)
        ]

        for point in check_points:
            if not self.is_point_clear(point, environment):
                return False
        return True

    def is_point_clear(self, point, environment):
        for obstacle in obstacle_manager.obstacles:
            if obstacle.rect.collidepoint(point):
                return False

        if (point[0] < environment.wall_thickness or
                point[0] > environment.width - environment.wall_thickness or
                point[1] < environment.wall_thickness or
                point[1] > environment.height - environment.wall_thickness):
            return False
        return True

    def draw(self, map):
        map.blit(self.rotated, self.rect)

    def check_bottom_wall(self, new_x, new_y, environment):
        wall_thickness = environment.wall_thickness
        buffer = self.radius

        if new_y + buffer > environment.height - wall_thickness:  # нижняя стенка
            return True
        return False
    def move(self, event=None, environment=None):
        keys = pygame.key.get_pressed()  # Получаем текущее состояние всех клавиш

        # Проверяем, зажаты ли клавиши и изменяем скорость
        if keys[pygame.K_KP4]:  # Увеличение скорости левого колеса
            self.vl += 0.001 * self.m2p
        if keys[pygame.K_KP1]:  # Уменьшение скорости левого колеса
            self.vl -= 0.001 * self.m2p
        if keys[pygame.K_KP6]:  # Увеличение скорости правого колеса
            self.vr += 0.001 * self.m2p
        if keys[pygame.K_KP3]:  # Уменьшение скорости правого колеса
            self.vr -= 0.001 * self.m2p

        new_x = self.x + ((self.vl + self.vr) / 2) * math.cos(self.theta) * dt
        new_y = self.y - ((self.vl + self.vr) / 2) * math.sin(self.theta) * dt

        if environment and not self.check_wall_collision(new_x, new_y, environment):
            self.x = new_x
            self.y = new_y
            self.theta += (self.vr - self.vl) / self.w * dt
        else:
            self.vl = 0
            self.vr = 0

        # сбрасываем угол
        if self.theta > 2 * math.pi or self.theta < -2 * math.pi:
            self.theta = 0

        # устанавливаем максимальную скорость
        self.vr = min(self.vr, self.maxspeed)
        self.vl = min(self.vl, self.maxspeed)
        # устанавливаем минимальную скорость
        self.vr = max(self.vr, self.minspeed)
        self.vl = max(self.vl, self.minspeed)

        self.rotated = pygame.transform.rotozoom(self.img, math.degrees(self.theta), 1)
        self.rect = self.rotated.get_rect(center=(self.x, self.y))

    def check_wall_collision(self, new_x, new_y, environment):
        wall_thickness = environment.wall_thickness
        buffer = self.radius

        if (new_x - buffer < wall_thickness or  # лева стенка
                new_x + buffer > environment.width - wall_thickness or  # права стенка
                new_y - buffer < wall_thickness or  # верхняя стенка
                new_y + buffer > environment.height - wall_thickness):  # нижняя стенка
            return True
        return False


print('Здравствуйте! Давайте настроим программу =)')
print('Примечание: алгоритм обхождения препятсвий не работает, но Вы можете протестировать генерацию препятствий')
count_objects = int(input('Нужны ли препятствия? Если нет - введите 0, в ином случае - любую другую клавишу >>>'))
wall_thickness = int(input('Ширина стен(рекомендуется вводить значения от 20 до 50) >>> '))
mode = input('Выберите режим:\n'
             'M(англ) - ручное управление \n'
             'A(англ) - автономное управление\n'
             '>>>')
while mode != 'M' and mode != 'A':
    print('Неверные входные данные. Попробуйте еще раз')
    mode = input('Выберите режим:\n'
                 'M(англ) - ручное управление \n'
                 'A(англ) - автономное управление\n'
                 '>>>')
room_height = int(input('Введите высоту комнаты(не меньше 500 и не больше 900) >>> '))
while room_height < 500 or room_height > 900:
    print('Неверные входные данные')
    room_height = int(input('Введите высоту комнаты(не меньше 600 и не больше 900) >>> '))
room_width = int(input('Введите высоту комнаты(не меньше 700 и не больше 1000) >>> '))
while room_width < 700 or room_width > 1200:
    print('Неверные входные данные')
    room_width = int(input('Введите высоту комнаты(не меньше 700 и не больше 1200) >>> '))

pygame.init()
dims = (room_height, room_width)
environment = Envir(dims,wall_thickness)
if mode == 'M':
    start = (wall_thickness+60, wall_thickness+60)
else:
    start = (wall_thickness, wall_thickness + 20)


print(mode)
# Создаем менеджер препятствий
obstacle_manager = ObstacleManager(environment,count_objects)

robot = Robot(start, "./robot.png", 0.15 * 3779.52)

running = True
dt = 0
last_time = pygame.time.get_ticks()

# Основной цикл симуляции
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if mode == 'M':
            robot.move(event, environment)

    # Автономный режим
    if mode == 'A':
        robot.move_autonomous(dt, environment)
    else:
        robot.move(None, environment)

    # Обновление графики
    dt = (pygame.time.get_ticks() - last_time) / 1000
    last_time = pygame.time.get_ticks()

    environment.map.fill(environment.black)
    environment.draw_walls()

    # Рисуем препятствия
    obstacle_manager.draw_obstacles(environment.map)

    robot.draw(environment.map)
    environment.trail((robot.x, robot.y))
    environment.write_info(int(robot.vl), int(robot.vr), robot.theta)

    pygame.display.update()

pygame.quit()