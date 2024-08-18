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
        Инициализация основного окна приложения и установка пользовательского интерфейса.
        """
        super().__init__()

        self.images = []  # Список для хранения загруженных изображений
        self.image_names = []  # Список для хранения имен файлов
        self.loaded_files = set()  # Множество для хранения имен уже загруженных файлов
        self.current_image_index = 0  # Индекс текущего отображаемого изображения
        self.color_map = None  # Переменная для хранения цветовой карты
        self.load_color_map()  # Загрузка цветовой карты

        self.slideshow_interval = 2000  # Интервал показа изображений (в миллисекундах)
        self.is_slideshow_running = False  # Флаг для управления слайд-шоу
        self.slideshow_timer = QTimer(self)  # Таймер для слайд-шоу
        self.slideshow_timer.timeout.connect(self.next_image)  # Обработка события таймера для переключения на следующее изображение
        self.init_UI()  # Инициализация пользовательского интерфейса


    def init_UI(self):
        """
        Настройка пользовательского интерфейса, включая кнопки и метки.
        """
        self.setWindowTitle('Просмотр изображений CSV')  # Установка заголовка окна
        self.setFixedSize(900, 900)  # Установка фиксированного размера окна

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;  
            }
        """)

        self.central_widget = QWidget()  # Создание центрального виджета
        self.setCentralWidget(self.central_widget)  # Установка центрального виджета

        self.layout = QVBoxLayout()  # Создание вертикального расположения виджетов
        self.central_widget.setLayout(self.layout)  # Установка компоновки для центрального виджета

        # Метка для отображения изображения
        self.image_label = QLabel('Изображение не загружено')
        self.image_label.setAlignment(Qt.AlignCenter)  # Центрирование изображения
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2196F3;  
                padding: 10px;              
                background-color: white;   
            }
        """)
        self.layout.addWidget(self.image_label)

        # Кнопка загрузки CSV файлов
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
        self.load_button.clicked.connect(self.load_csv_files)
        self.layout.addWidget(self.load_button)

        # Кнопка сохранения изображения
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
        self.save_button.clicked.connect(self.save_image)
        self.layout.addWidget(self.save_button)

        # Кнопка применения цветовой карты
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
        self.apply_color_map_button.clicked.connect(self.apply_color_map)
        self.layout.addWidget(self.apply_color_map_button)

        # Выпадающий список для выбора изображения
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
        self.file_selector.currentIndexChanged.connect(self.switch_image)
        self.layout.addWidget(self.file_selector)

        # Кнопка запуска слайд-шоу
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
        self.start_slideshow_button.clicked.connect(self.start_slideshow)
        self.layout.addWidget(self.start_slideshow_button)

        # Кнопка остановки слайд-шоу
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
        self.stop_slideshow_button.clicked.connect(self.stop_slideshow)
        self.layout.addWidget(self.stop_slideshow_button)

        # Поле для ввода интервала слайд-шоу
        self.interval_spinbox = QSpinBox()  # Создание поля для ввода интервала
        self.interval_spinbox.setRange(100, 10000)  # Установка диапазона значений (0.1 до 10 секунд)
        self.interval_spinbox.setValue(self.slideshow_interval)  # Установка начального значения интервала
        self.interval_spinbox.setSuffix(' ms')
        self.interval_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 10px;              
                border: 2px solid #003366;  
                border-radius: 5px;         
                font-family: 'Arial';       
                font-size: 14px;            
            }
        """)
        self.interval_spinbox.valueChanged.connect(self.update_interval)
        self.layout.addWidget(self.interval_spinbox)

    def load_color_map(self):
        colormap_path = ":/colormap/CET-R1.csv"
        try:
            file = QFile(colormap_path)
            if file.open(QIODevice.ReadOnly):
                df = pd.read_csv(file, delimiter=',', header=None)
                self.color_map = df.values.astype(np.uint8)
                file.close()
            else:
                print("Ошибка при загрузке цветовой карты")
        except Exception as e:
            print(f"Ошибка при загрузке цветовой карты: {e}")
            self.color_map = None

    def load_csv_files(self):
        """
        Открытие диалога для выбора нескольких CSV файлов и их загрузка, исключая дубликаты.
        """
        files, _ = QFileDialog.getOpenFileNames(self, 'Открыть CSV файлы', '', 'CSV Files (*.csv)')  # Открытие диалога выбора файлов
        if not files:
            return  # Выход, если файлы не выбраны

        new_files = []  # Список для хранения новых файлов
        for file in files:
            file_name = file.split('/')[-1]  # Извлечение имени файла
            if file_name not in self.loaded_files:  # Проверка на дубликаты
                self.loaded_files.add(file_name)  # Добавление имени файла в множество загруженных файлов
                new_files.append(file)  # Добавление нового файла в список

        # Загрузка новых файлов
        try:
            self.images.extend(self.csv_to_image(file) for file in new_files)  # Преобразование CSV файлов в изображения
            self.image_names.extend([file.split('/')[-1] for file in new_files])  # Обновление списка имен файлов
            self.file_selector.addItems([file.split('/')[-1] for file in new_files])  # Добавление новых файлов в выпадающий список
            if self.image_names:
                self.show_image(0)  # Отображение первого изображения
        except Exception as e:
            print(f"Ошибка при загрузке файлов: {e}")  # Обработка исключений

    def apply_color_map(self):
        """
        Применение цветовой карты к текущему изображению, если оно градационное.
        """
        if self.color_map is None:
            print("Цветовая карта не загружена.")
            return

        if not self.images:
            return

        try:
            image = self.images[self.current_image_index]  # Получение текущего изображения
            if image.mode == 'L':  # Проверка, является ли изображение градационным
                color_mapped_image = Image.fromarray(self.color_map[image], 'RGB')  # Применение цветовой карты
                self.images[self.current_image_index] = color_mapped_image  # Замена изображения с примененной цветовой картой
                self.show_image(self.current_image_index)  # Отображение измененного изображения
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
            first_line = file.readline().strip()  # Чтение первой строки
            df = pd.read_csv(file, delimiter=';', header=None)  # Чтение данных из CSV файла

        data = df.values  # Преобразование данных в массив
        if first_line == "# rgb":  # Проверка, содержит ли файл RGB данные
            height, width = data.shape  # Получение размеров изображения
            rgb_data = np.zeros((height, width, 3), dtype=np.uint8)  # Создание массива для RGB данных

            for i in range(height):
                for j in range(width):
                    pixel = int(data[i, j])  # Извлечение значения пикселя
                    blue = pixel & 0xFF  # Извлечение синего компонента
                    green = (pixel >> 8) & 0xFF  # Извлечение зеленого компонента
                    red = (pixel >> 16) & 0xFF  # Извлечение красного компонента
                    rgb_data[i, j] = [red, green, blue]  # Установка значения пикселя в массив

            return Image.fromarray(rgb_data, 'RGB')  # Создание изображения из RGB данных
        else:
            # Обработка градационного изображения
            return Image.fromarray(np.uint8(data), 'L')  # Создание градационного изображения

    def show_image(self, index):
        """
        Отображение изображения по указанному индексу.
        :param index: Индекс изображения в списке
        """
        if 0 <= index < len(self.images):  # Проверка, что индекс находится в допустимом диапазоне
            self.current_image_index = index  # Обновление текущего индекса изображения
            image = self.images[index]  # Получение изображения
            q_image = QImage(image.tobytes(), image.width, image.height, image.width * len(image.getbands()),
                             QImage.Format_RGB888 if image.mode == 'RGB' else QImage.Format_Grayscale8)  # Создание QImage
            pixmap = QPixmap.fromImage(q_image)  # Создание QPixmap из QImage
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))  # Установка изображения в метку

    def switch_image(self, index):
        """
        Переключение изображения при выборе из выпадающего списка.
        :param index: Индекс выбранного изображения
        """
        self.show_image(index)  # Отображение выбранного изображения

    def save_image(self):
        """
        Сохранение текущего изображения в файл.
        """
        if not self.images:
            return  # Выход, если нет изображений

        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить изображение', '', 'Image Files (*.jpg *.png *.bmp)')  # Открытие диалога сохранения
        if not file_path:
            return  # Выход, если путь не указан

        self.images[self.current_image_index].save(file_path)  # Сохранение изображения

    def start_slideshow(self):
        """
        Запуск слайд-шоу.
        """
        if not self.images:
            print("Нет изображений для показа в слайд-шоу.")  # Сообщение о том, что нет изображений для слайд-шоу
            return

        if not self.is_slideshow_running:  # Проверка, не запущено ли слайд-шоу
            self.is_slideshow_running = True  # Установка флага слайд-шоу в True
            self.slideshow_timer.start(self.slideshow_interval)  # Запуск таймера с заданным интервалом

    def stop_slideshow(self):
        """
        Остановка слайд-шоу.
        """
        if self.is_slideshow_running:  # Проверка, что слайд-шоу запущено
            self.is_slideshow_running = False  # Установка флага слайд-шоу в False
            self.slideshow_timer.stop()  # Остановка таймера

    def next_image(self):
        """
        Переключение на следующее изображение в слайд-шоу.
        """
        if self.images:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)  # Обновление индекса текущего изображения
            self.show_image(self.current_image_index)  # Отображение следующего изображения

    def update_interval(self):
        """
        Обновление интервала слайд-шоу.
        """
        self.slideshow_interval = self.interval_spinbox.value()  # Установка нового интервала
        if self.is_slideshow_running:  # Проверка, что слайд-шоу запущено
            self.slideshow_timer.setInterval(self.slideshow_interval)  # Обновление интервала таймера


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CSV_ImageViewer()  # Создание экземпляра класса CSV_ImageViewer
    viewer.show()  # Показ окна приложения
    sys.exit(app.exec_())  # Запуск цикла обработки событий