import sys
import pandas as pd
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog, QWidget, QComboBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class CSV_ImageViewer(QMainWindow):
    def __init__(self):
        """
        Инициализация основного окна приложения и установка пользовательского интерфейса.
        """
        super().__init__()
        self.images = []  # Список для хранения загруженных изображений
        self.image_names = []  # Список для хранения имен файлов изображений
        self.loaded_files = set()  # Множество для хранения имен уже загруженных файлов
        self.current_image_index = 0  # Индекс текущего отображаемого изображения
        self.init_UI()  # Инициализация пользовательского интерфейса

    def init_UI(self):
        """
        Настройка пользовательского интерфейса, включая кнопки и метки.
        """
        self.setWindowTitle('Просмотр изображений CSV')  # Заголовок окна
        self.setFixedSize(900, 900)  # Установка фиксированного размера окна

        # Установка стиля для основного окна
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
        self.load_button.clicked.connect(self.load_csv_files)  # Подключение обработчика нажатия кнопки
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
        self.file_selector.currentIndexChanged.connect(self.switch_image)  # Подключение обработчика изменения выбранного элемента
        self.layout.addWidget(self.file_selector)  # Добавление выпадающего списка в компоновку

    def load_csv_files(self):
        """
        Открытие диалога для выбора нескольких CSV файлов и их загрузка, исключая дубликаты.
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

    def csv_to_image(self, file_path):
        """
        Преобразование CSV файла в изображение.
        :param file_path: Путь к CSV файлу
        :return: Объект изображения PIL
        """
        df = pd.read_csv(file_path, delimiter=';', header=None)  # Чтение CSV файла
        data = df.values  # Преобразование данных в массив
        return Image.fromarray(np.uint8(data), 'L')  # Создание изображения в градациях серого

    def show_image(self, index):
        """
        Отображение изображения по указанному индексу.
        :param index: Индекс изображения в списке
        """
        if 0 <= index < len(self.images):
            self.current_image_index = index  # Обновление текущего индекса изображения
            image = self.images[index]
            q_image = QImage(image.tobytes(), image.width, image.height, image.width, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))  # Отображение изображения в метке

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
            return  # Если нет изображений, выход из функции

        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить изображение', '', 'Image Files (*.jpg *.png *.bmp)')
        if not file_path:
            return  # Если путь не указан, выход из функции

        self.images[self.current_image_index].save(file_path)  # Сохранение изображения в файл


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = CSV_ImageViewer()  # Создание экземпляра класса CSV_ImageViewer
    viewer.show()  # Показ окна приложения
    sys.exit(app.exec_())  # Запуск главного цикла приложения
