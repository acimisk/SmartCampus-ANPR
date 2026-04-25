from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QTableWidget,
    QVBoxLayout, QHBoxLayout, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt


class Arayuz(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plaka Okuma Sistemi")
        self.setGeometry(200, 100, 1200, 700)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Üst alan
        top_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Plaka ara...")

        self.search_button = QPushButton("Ara")

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)

        # Alt alan
        content_layout = QHBoxLayout()

        # Sol taraf: video alanı
        self.video_frame = QFrame()
        self.video_frame.setStyleSheet("background-color: #1f1f1f;")

        video_layout = QVBoxLayout()
        self.video_label = QLabel("Video Alanı")
        self.video_label.setAlignment(Qt.AlignCenter)

        video_layout.addWidget(self.video_label)
        self.video_frame.setLayout(video_layout)

        # Sağ taraf: tablo
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Plaka", "Tarih"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        content_layout.addWidget(self.video_frame, 2)
        content_layout.addWidget(self.table, 1)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(content_layout)