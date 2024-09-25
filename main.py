import pygame
import os
import random

# Настройки окна

# Настройки камеры
initial_camera_x = 0
initial_camera_y = 0
initial_camera_scale = 1.0
camera_speed = 5

# Загрузка изображения
image_filename = 'testImage.png'
image_path = os.path.join(os.path.dirname(__file__), image_filename)

# Инициализация Pygame
pygame.init()

window_width = 800
window_height = 600
window_surface = pygame.display.set_mode((window_width, window_height))

window_caption = "Canvas with Camera"
pygame.display.set_caption(window_caption)
clock = pygame.time.Clock()

# Загрузка изображения
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image '{image_filename}' not found in the current directory.")
image = pygame.image.load(image_path)
image_rect = image.get_rect()

# Центрирование изображения на сцене
image_rect.center = (window_width // 2, window_height // 2)

# Камера
class Camera:
    def __init__(self, x, y, scale):
        self.camera_x = x
        self.camera_y = y
        self.camera_scale = scale

    def move(self, delta_x, delta_y):
        self.camera_x += delta_x
        self.camera_y += delta_y

    def zoom(self, zoom_factor, mouse_position):
        old_scale = self.camera_scale
        self.camera_scale = max(0.1, self.camera_scale + zoom_factor)

        # Позиция мыши на экране и её пересчёт в мировые координаты до зума
        mouse_world_x = (mouse_position[0] / old_scale) - self.camera_x
        mouse_world_y = (mouse_position[1] / old_scale) - self.camera_y

        # Обновляем координаты камеры, чтобы картинка зумировалась относительно точки, на которую указывает мышь
        self.camera_x = (mouse_position[0] / self.camera_scale) - mouse_world_x
        self.camera_y = (mouse_position[1] / self.camera_scale) - mouse_world_y

    def apply_transform(self, rect):
        transformed_rect = rect.copy()
        transformed_rect.x = (rect.x + self.camera_x) * self.camera_scale
        transformed_rect.y = (rect.y + self.camera_y) * self.camera_scale
        transformed_rect.width *= self.camera_scale
        transformed_rect.height *= self.camera_scale
        return transformed_rect

# Класс прямоугольника
class Rectangle:
    def __init__(self, position_x, position_y, width, height, color, name):
        self.position_x = position_x
        self.position_y = position_y
        self.width = width
        self.height = height
        self.color = color
        self.name = name

    def draw(self, surface, camera, is_selected=False):
        # Прямоугольник рисуется от левой нижней точки, нужно учесть смещение
        rect = pygame.Rect(self.position_x, self.position_y - self.height, self.width, self.height)
        transformed_rect = camera.apply_transform(rect)
        pygame.draw.rect(surface, self.color, transformed_rect)
        
        # Если объект выделен, рисуем полупрозрачную рамку
        if is_selected:
            overlay_color = (0, 0, 255, 100)  # Синий цвет с прозрачностью
            overlay_surface = pygame.Surface((transformed_rect.width, transformed_rect.height), pygame.SRCALPHA)
            overlay_surface.fill(overlay_color)
            surface.blit(overlay_surface, transformed_rect.topleft)

    def is_mouse_over(self, mouse_pos, camera):
        # Преобразование позиции мыши в мировые координаты
        transformed_mouse_x = mouse_pos[0] / camera.camera_scale - camera.camera_x
        transformed_mouse_y = mouse_pos[1] / camera.camera_scale - camera.camera_y

        # Проверка попадания мыши на объект
        return self.position_x <= transformed_mouse_x <= self.position_x + self.width and \
               self.position_y - self.height <= transformed_mouse_y <= self.position_y

# Функция для генерации случайного прямоугольника
def generate_random_rectangle(name):
    random_x = random.randint(0, window_width // 2)
    random_y = random.randint(0, window_height // 2)
    random_width = random.randint(50, 150)
    random_height = random.randint(50, 150)
    random_color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    return Rectangle(random_x, random_y, random_width, random_height, random_color, name)

# Инициализация камеры
camera = Camera(initial_camera_x, initial_camera_y, initial_camera_scale)

# Прямоугольники
rectangles = []

# Выбранный объект
selected_rectangle = None

# Кнопка "Добавить прямоугольник"
font = pygame.font.SysFont(None, 36)
button_rect = pygame.Rect(10, 50, 250, 40)
button_text_surface = font.render("Добавить прямоугольник", True, (0, 0, 0))

# Основной цикл программы
running = True
is_dragging = False
previous_mouse_position = None
rectangle_count = 0  # Счетчик для именования прямоугольников

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Перетаскивание камеры средней кнопкой мыши
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Нажата средняя кнопка мыши
            is_dragging = True
            previous_mouse_position = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONUP and event.button == 2:  # Отпущена средняя кнопка мыши
            is_dragging = False

        if event.type == pygame.MOUSEMOTION and is_dragging:
            current_mouse_position = pygame.mouse.get_pos()
            delta_x = current_mouse_position[0] - previous_mouse_position[0]
            delta_y = current_mouse_position[1] - previous_mouse_position[1]
            camera.move(delta_x / camera.camera_scale, delta_y / camera.camera_scale)
            previous_mouse_position = current_mouse_position

        # Масштабирование колесиком мыши
        if event.type == pygame.MOUSEWHEEL:
            mouse_position = pygame.mouse.get_pos()  # Получаем текущую позицию мыши
            camera.zoom(event.y * 0.1, mouse_position)  # Масштабируем относительно позиции мыши

        # Нажатие на кнопку "Добавить прямоугольник"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos):
                rectangle_count += 1
                rectangles.append(generate_random_rectangle(f"Rect {rectangle_count}"))
            else:
                # Проверка объектов в обратном порядке для корректного перекрытия
                for rectangle in reversed(rectangles):
                    if rectangle.is_mouse_over(mouse_pos, camera):
                        selected_rectangle = rectangle
                        break

    # Очистка экрана
    window_surface.fill((255, 255, 255))

    # Отрисовка изображения с учетом позиции и масштаба камеры
    transformed_image_rect = camera.apply_transform(image_rect)
    window_surface.blit(pygame.transform.scale(image, (int(transformed_image_rect.width), int(transformed_image_rect.height))), transformed_image_rect.topleft)

    # Отрисовка всех прямоугольников
    for rectangle in rectangles:
        rectangle.draw(window_surface, camera, is_selected=(rectangle == selected_rectangle))

    # Отрисовка кнопки
    pygame.draw.rect(window_surface, (200, 200, 200), button_rect)  # Кнопка с фоном
    window_surface.blit(button_text_surface, (button_rect.x + 10, button_rect.y + 5))  # Текст на кнопке

    # Отображение информации о камере
    camera_info = f"Camera X: {camera.camera_x:.1f}, Y: {camera.camera_y:.1f}, Scale: {camera.camera_scale:.2f}"
    camera_info_surface = font.render(camera_info, True, (0, 0, 0))
    window_surface.blit(camera_info_surface, (10, 10))

    guide_info = "масштаб и перемещение при помощи колесика"
    guide_info_surface = font.render(guide_info, True, (0, 0, 0))
    window_surface.blit(guide_info_surface , (10, 100))

    # Отображение информации о выбранном прямоугольнике
    if selected_rectangle:
        rectangle_info = f"Selected: {selected_rectangle.name}, X: {selected_rectangle.position_x}, Y: {selected_rectangle.position_y}, W: {selected_rectangle.width}, H: {selected_rectangle.height}"
        rectangle_info_surface = font.render(rectangle_info, True, (0, 0, 0))
        window_surface.blit(rectangle_info_surface, (10, 140))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение работы Pygame
pygame.quit()
