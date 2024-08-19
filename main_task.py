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
        Конструктор основного окна приложения.
        Инициализирует все необходимые компоненты и пользовательский интерфейс.
        """
        super().__init__()

        # Инициализация переменных
        self.images = []  # Здесь будут храниться загруженные изображения
        self.image_names = []  # Список имен файлов изображений
        self.loaded_files = set()  # Множество для отслеживания уже загруженных файлов
        self.current_image_index = 0  # Индекс текущего отображаемого изображения

        self.init_UI()  # Настройка пользовательского интерфейса

    def init_UI(self):
        """
        Настройка пользовательского интерфейса.
        Создает и размещает все виджеты на главном окне.
        """
        self.setWindowTitle('Просмотр изображений CSV')  # Устанавливаем заголовок окна
        self.setFixedSize(900, 900)  # Устанавливаем фиксированный размер окна

        # Применяем стиль к главному окну
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;  
            }
        """)

        self.central_widget = QWidget()  # Создаем центральный виджет
        self.setCentralWidget(self.central_widget)  # Устанавливаем центральный виджет
        self.layout = QVBoxLayout()  # Создаем вертикальную компоновку для размещения виджетов
        self.central_widget.setLayout(self.layout)  # Устанавливаем компоновку

        # Метка для отображения изображения
        self.image_label = QLabel('Изображение не загружено')
        self.image_label.setAlignment(Qt.AlignCenter)  # Центрируем текст метки
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #2196F3;  
                padding: 10px;              
                background-color: white;  
            }
        """)
        self.layout.addWidget(self.image_label)  # Добавляем метку в компоновку

        # Кнопка для загрузки CSV файлов
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
        self.load_button.clicked.connect(self.load_csv_files)  # Подключаем обработчик для кнопки
        self.layout.addWidget(self.load_button)  # Добавляем кнопку в компоновку

        # Кнопка для сохранения изображения
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
        self.save_button.clicked.connect(self.save_image)  # Подключаем обработчик для кнопки
        self.layout.addWidget(self.save_button)  # Добавляем кнопку в компоновку

        # Выпадающий список для выбора изображений
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

    def load_csv_files(self):
        """
        Загрузка CSV файлов и преобразование их в изображения.
        Обновляет выпадающий список с именами загруженных изображений.
        """
        files, _ = QFileDialog.getOpenFileNames(self, 'Открыть CSV файлы', '', 'CSV Files (*.csv)')
        if not files:
            return  # Если файлы не выбраны, выходим

        new_files = []  # Список для новых файлов
        for file in files:
            file_name = file.split('/')[-1]  # Извлекаем имя файла
            if file_name not in self.loaded_files:
                self.loaded_files.add(file_name)  # Добавляем имя файла в множество загруженных
                new_files.append(file)

        try:
            # Загружаем новые файлы
            self.images.extend(self.csv_to_image(file) for file in new_files)
            self.image_names.extend([file.split('/')[-1] for file in new_files])
            self.file_selector.addItems([file.split('/')[-1] for file in new_files])
            if self.image_names:
                self.show_image(0)  # Показываем первое изображение из списка
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
            self.current_image_index = index  # Обновляем текущий индекс изображения
            image = self.images[index]
            q_image = QImage(image.tobytes(), image.width, image.height, image.width, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))  # Отображаем изображение

    def switch_image(self, index):
        """
        Переключение изображения при выборе из выпадающего списка.
        :param index: Индекс выбранного изображения
        """
        self.show_image(index)  # Показываем выбранное изображение

    def save_image(self):
        """
        Сохранение текущего изображения в файл.
        """
        if not self.images:
            return  # Если нет изображений, ничего не делаем

        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить изображение', '', 'Image Files (*.jpg *.png *.bmp)')
        if not file_path:
            return  # Если путь не указан, выходим

        self.images[self.current_image_index].save(file_path)  # Сохраняем текущее изображение

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Создание объекта приложения
    viewer = CSV_ImageViewer()  # Создаем экземпляр класса CSV_ImageViewer
    viewer.show()  # Показываем главное окно
    sys.exit(app.exec_())  # Запускаем основной цикл приложения
