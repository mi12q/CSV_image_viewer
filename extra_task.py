import sys
import pandas as pd
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog, QWidget, \
    QComboBox, QSpinBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QFile, QIODevice, QTimer
import colormap


class CSV_ImageViewer(QMainWindow):
    def __init__(self):
        """
        Конструктор основного окна приложения.
        Инициализирует все необходимые компоненты и пользовательский интерфейс.
        """
        super().__init__()

        # Инициализация переменных
        self.images = []  # Список для хранения изображений
        self.image_names = []  # Список для хранения имен файлов изображений
        self.loaded_files = set()  # Множество для хранения загруженных файлов (избегаем дублирования)
        self.current_image_index = 0  # Индекс текущего изображения в списке
        self.color_map = None  # Цветовая карта для преобразования изображений
        self.slideshow_interval = 2000  # Интервал между сменой изображений в слайд-шоу (в миллисекундах)
        self.is_slideshow_running = False  # Флаг, указывающий на состояние слайд-шоу
        self.slideshow_timer = QTimer(self)  # Таймер для слайд-шоу

        # Подключение слота для переключения изображений по таймеру
        self.slideshow_timer.timeout.connect(self.next_image)
        self.load_color_map()  # Загрузка цветовой карты при запуске приложения
        self.init_UI()  # Настройка пользовательского интерфейса

    def init_UI(self):
        """
        Настройка пользовательского интерфейса.
        Создает и размещает все виджеты на главном окне.
        """
        self.setWindowTitle('Просмотр изображений CSV')  # Устанавливаем заголовок окна
        self.setFixedSize(900, 900)  # Устанавливаем фиксированный размер окна

        # Устанавливаем стиль для основного окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

        # Создаем и настраиваем центральный виджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Создаем вертикальную компоновку для размещения виджетов
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Создаем метку для отображения изображений
        self.image_label = QLabel('Изображение не загружено')
        self.image_label.setAlignment(Qt.AlignCenter)  # Центрируем изображение
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2196F3;
                padding: 10px;
                background-color: white;
            }
        """)
        self.layout.addWidget(self.image_label)

        # Создаем кнопку для загрузки CSV файлов
        self.load_button = QPushButton('Загрузить CSV')
        self.load_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #002244;
            }
        """)
        self.load_button.clicked.connect(self.load_csv_files)  # Подключаем действие кнопки к функции загрузки файлов
        self.layout.addWidget(self.load_button)

        # Создаем кнопку для сохранения текущего изображения
        self.save_button = QPushButton('Сохранить изображение')
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #002244;
            }
        """)
        self.save_button.clicked.connect(self.save_image)  # Подключаем действие кнопки к функции сохранения изображения
        self.layout.addWidget(self.save_button)

        # Создаем кнопку для применения цветовой карты к изображению
        self.apply_color_map_button = QPushButton('Применить цветовую карту')
        self.apply_color_map_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #002244;
            }
        """)
        self.apply_color_map_button.clicked.connect(self.apply_color_map)  # Подключаем действие кнопки к функции применения цветовой карты
        self.layout.addWidget(self.apply_color_map_button)

        # Создаем выпадающий список для выбора изображений
        self.file_selector = QComboBox()
        self.file_selector.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #003366;
                border-radius: 5px;
                font-family: 'Arial';
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.file_selector.currentIndexChanged.connect(self.switch_image)  # Подключаем обработчик выбора изображения
        self.layout.addWidget(self.file_selector)  # Добавляем выпадающий список в компоновку

        # Создаем кнопку для запуска слайд-шоу
        self.start_slideshow_button = QPushButton('Запустить слайд-шоу')
        self.start_slideshow_button.setStyleSheet("""
            QPushButton {
                background-color: #003366;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #002244;
            }
        """)
        self.start_slideshow_button.clicked.connect(self.start_slideshow)  # Подключаем действие кнопки к функции запуска слайд-шоу
        self.layout.addWidget(self.start_slideshow_button)

        # Создаем кнопку для остановки слайд-шоу
        self.stop_slideshow_button = QPushButton('Остановить слайд-шоу')
        self.stop_slideshow_button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                font-family: 'Arial';
                font-size: 14px;
                font-weight: bold;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
        """)
        self.stop_slideshow_button.clicked.connect(
            self.stop_slideshow)  # Подключаем действие кнопки к функции остановки слайд-шоу
        self.layout.addWidget(self.stop_slideshow_button)

        # Создаем поле для ввода интервала слайд-шоу
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(100, 10000)  # Устанавливаем диапазон интервала от 100 мс до 10 секунд
        self.interval_spinbox.setValue(self.slideshow_interval)  # Устанавливаем начальное значение
        self.interval_spinbox.setSuffix(' ms')  # Устанавливаем единицу измерения
        self.interval_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                border: 2px solid #003366;
                border-radius: 5px;
                font-family: 'Arial';
                font-size: 14px;
            }
        """)
        self.interval_spinbox.valueChanged.connect(
            self.update_interval)  # Подключаем изменение значения к функции обновления интервала
        self.layout.addWidget(self.interval_spinbox)

    def load_color_map(self):
        """
        Загрузка цветовой карты из файла.
        Цветовая карта используется для преобразования градационных изображений в цветные.
        """
        colormap_path = ":/colormap/CET-R1.csv"  # Путь к файлу цветовой карты
        try:
            file = QFile(colormap_path)
            if file.open(QIODevice.ReadOnly):  # Попытка открыть файл для чтения
                df = pd.read_csv(file, delimiter=',', header=None)  # Чтение CSV файла с цветовой картой
                self.color_map = df.values.astype(np.uint8)  # Преобразование данных в формат numpy array
                file.close()
                print("Цветовая карта успешно загружена.")
            else:
                print("Не удалось открыть файл цветовой карты.")
        except Exception as e:
            print(f"Ошибка при загрузке цветовой карты: {e}")

    def load_csv_files(self):
        """
        Загрузка CSV файлов и преобразование их в изображения.
        Обновляет выпадающий список с именами загруженных изображений.
        """
        files, _ = QFileDialog.getOpenFileNames(self, 'Открыть CSV файлы', '', 'CSV Files (*.csv)')
        if not files:
            return

        new_files = []  # Список для новых файлов
        for file in files:
            file_name = file.split('/')[-1]  # Извлечение имени файла из пути
            if file_name not in self.loaded_files:
                self.loaded_files.add(file_name)  # Добавление имени файла в множество загруженных файлов
                new_files.append(file)

        try:
            # Загрузка новых файлов
            self.images.extend(self.csv_to_image(file) for file in new_files)
            self.image_names.extend([file.split('/')[-1] for file in new_files])
            self.file_selector.addItems([file.split('/')[-1] for file in new_files])
            if self.image_names:
                self.show_image(0)  # Показываем первое изображение
        except Exception as e:
            print(f"Ошибка при загрузке файлов: {e}")

    def apply_color_map(self):
        """
        Применение цветовой карты к текущему изображению.
        Цветовая карта преобразует градационное изображение в цветное.
        """
        if self.color_map is None:
            print("Цветовая карта не загружена.")
            return

        if not self.images:
            print("Нет изображений для применения цветовой карты.")
            return

        try:
            image = self.images[self.current_image_index]
            if image.mode == 'L':  # Если изображение градационного типа
                color_mapped_image = Image.fromarray(self.color_map[image], 'RGB')  # Применение цветовой карты
                self.images[self.current_image_index] = color_mapped_image  # Замена изображения
                self.show_image(self.current_image_index)  # Отображение обновленного изображения
            else:
                print("Цветовая карта применяется только к градационным изображениям.")
        except Exception as e:
            print(f"Ошибка при применении цветовой карты: {e}")

    def csv_to_image(self, file_path):
        """
        Преобразование CSV файла в изображение.
        :param file_path: Путь к CSV файлу
        :return: Объект изображения PIL
        """
        with open(file_path, 'r') as file:
            first_line = file.readline().strip()  # Чтение первой строки для определения формата
            df = pd.read_csv(file, delimiter=';', header=None)  # Чтение данных CSV

        data = df.values
        if first_line == "# rgb":  # Проверка формата файла
            height, width = data.shape
            rgb_data = np.zeros((height, width, 3), dtype=np.uint8)

            for i in range(height):
                for j in range(width):
                    pixel = int(data[i, j])
                    blue = pixel & 0xFF
                    green = (pixel >> 8) & 0xFF
                    red = (pixel >> 16) & 0xFF
                    rgb_data[i, j] = [red, green, blue]

            return Image.fromarray(rgb_data, 'RGB')  # Создание изображения RGB
        else:
            return Image.fromarray(np.uint8(data), 'L')  # Создание градационного изображения

    def show_image(self, index):
        """
        Отображение изображения по указанному индексу.
        :param index: Индекс изображения в списке
        """
        if 0 <= index < len(self.images):
            self.current_image_index = index
            image = self.images[index]
            # Конвертирование изображения PIL в формат QImage
            q_image = QImage(image.tobytes(), image.width, image.height, image.width * len(image.getbands()),
                             QImage.Format_RGB888 if image.mode == 'RGB' else QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(),
                                                     Qt.KeepAspectRatio))  # Отображение изображения с сохранением пропорций

    def switch_image(self, index):
        """
        Переключение изображения при выборе из выпадающего списка.
        :param index: Индекс выбранного изображения
        """
        self.show_image(index)

    def save_image(self):
        """
        Сохранение текущего изображения в файл.
        """
        if not self.images:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить изображение', '', 'Image Files (*.jpg *.png *.bmp)')
        if not file_path:
            return

        self.images[self.current_image_index].save(file_path)  # Сохранение изображения по указанному пути

    def start_slideshow(self):
        """
        Запуск слайд-шоу для отображения изображений по очереди.
        """
        if not self.images:
            print("Нет изображений для слайд-шоу.")
            return

        if not self.is_slideshow_running:
            self.is_slideshow_running = True
            self.slideshow_timer.start(self.slideshow_interval)  # Запуск таймера с указанным интервалом

    def stop_slideshow(self):
        """
        Остановка слайд-шоу.
        """
        if self.is_slideshow_running:
            self.is_slideshow_running = False
            self.slideshow_timer.stop()  # Остановка таймера

    def next_image(self):
        """
        Переключение на следующее изображение в слайд-шоу.
        """
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image(self.current_image_index)  # Показ следующего изображения

    def update_interval(self):
        """
        Обновление интервала смены изображений в слайд-шоу.
        """
        self.slideshow_interval = self.interval_spinbox.value()
        if self.is_slideshow_running:
            self.slideshow_timer.setInterval(self.slideshow_interval)  # Установка нового интервала для таймера


if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создание объекта приложения
    viewer = CSV_ImageViewer()  # Создаем экземпляр класса CSV_ImageViewer
    viewer.show()  # Показываем главное окно
    sys.exit(app.exec_())  # Запускаем основной цикл приложения
