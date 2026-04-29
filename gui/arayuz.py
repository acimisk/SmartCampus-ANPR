from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QSizePolicy,
    QVBoxLayout, QHBoxLayout, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor


class Arayuz(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plaka Okuma Sistemi")
        self.setGeometry(200, 100, 1200, 700)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #0f172a;
                color: #e2e8f0;
                font-family: Segoe UI, Arial, sans-serif;
            }
            QFrame#Card {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
            }
            QLabel#Title {
                font-size: 20px;
                font-weight: 600;
                color: #f8fafc;
            }
            QLabel#Subtle {
                color: #94a3b8;
                font-size: 12px;
            }
            QLabel#StatusBadge {
                border-radius: 10px;
                padding: 8px 12px;
                background-color: #334155;
                color: #f8fafc;
                font-weight: 600;
            }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 8px 10px;
                color: #f1f5f9;
            }
            QPushButton {
                background-color: #2563eb;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                color: #ffffff;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton#SuccessButton {
                background-color: #15803d;
            }
            QPushButton#SuccessButton:hover {
                background-color: #166534;
            }
            QPushButton#DangerButton {
                background-color: #b91c1c;
            }
            QPushButton#DangerButton:hover {
                background-color: #991b1b;
            }
            QTableWidget {
                background-color: #111827;
                alternate-background-color: #0b1220;
                border: 1px solid #1f2937;
                border-radius: 10px;
                gridline-color: #1f2937;
                color: #e2e8f0;
                selection-background-color: #1d4ed8;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                background-color: #111827;
                color: #e2e8f0;
                border-bottom: 1px solid #1f2937;
                padding: 6px;
            }
            QTableWidget::item:alternate {
                background-color: #0b1220;
            }
            QTableWidget::item:selected {
                background-color: #1d4ed8;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: #f8fafc;
                border: none;
                padding: 8px;
                font-weight: 600;
            }
            """
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        central_widget.setLayout(main_layout)

        header_card = QFrame()
        header_card.setObjectName("Card")
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(14, 12, 14, 12)
        header_card.setLayout(header_layout)

        title_wrap = QVBoxLayout()
        self.title_label = QLabel("Smart Campus ANPR Dashboard")
        self.title_label.setObjectName("Title")
        self.subtitle_label = QLabel("Canli plaka tanima, erisim kontrolu ve olay loglama")
        self.subtitle_label.setObjectName("Subtle")
        title_wrap.addWidget(self.title_label)
        title_wrap.addWidget(self.subtitle_label)

        self.status_badge = QLabel("Sistem Hazir")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setAlignment(Qt.AlignCenter)
        self.status_badge.setMinimumWidth(180)

        header_layout.addLayout(title_wrap)
        header_layout.addStretch()
        header_layout.addWidget(self.status_badge)

        top_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Plaka ara...")
        self.search_input.setMinimumHeight(36)

        self.search_button = QPushButton("Temizle")
        self.search_button.setMinimumHeight(36)
        self.search_button.clicked.connect(self.search_input.clear)

        top_layout.addWidget(self.search_input)
        top_layout.addWidget(self.search_button)

        access_layout = QHBoxLayout()
        self.plate_manage_input = QLineEdit()
        self.plate_manage_input.setPlaceholderText("Plaka (or: 34ABC123)")
        self.owner_manage_input = QLineEdit()
        self.owner_manage_input.setPlaceholderText("Sahip adi (opsiyonel)")
        self.add_authorized_button = QPushButton("Yetkili Ekle/Guncelle")
        self.add_authorized_button.setObjectName("SuccessButton")
        self.remove_authorized_button = QPushButton("Yetkiyi Kaldir")
        self.remove_authorized_button.setObjectName("DangerButton")
        self.owner_query_button = QPushButton("Sahip Sorgula")

        access_layout.addWidget(self.plate_manage_input, 2)
        access_layout.addWidget(self.owner_manage_input, 2)
        access_layout.addWidget(self.add_authorized_button)
        access_layout.addWidget(self.remove_authorized_button)
        access_layout.addWidget(self.owner_query_button)

        info_layout = QHBoxLayout()
        self.last_plate_label = QLabel("Son Plaka: -")
        self.last_plate_label.setObjectName("Subtle")
        self.last_time_label = QLabel("Zaman: -")
        self.last_time_label.setObjectName("Subtle")
        self.last_status_label = QLabel("Durum: -")
        self.last_status_label.setObjectName("Subtle")
        info_layout.addWidget(self.last_plate_label)
        info_layout.addSpacing(12)
        info_layout.addWidget(self.last_time_label)
        info_layout.addSpacing(12)
        info_layout.addWidget(self.last_status_label)
        info_layout.addStretch()

        self.owner_info_label = QLabel("Sahip Bilgisi: -")
        self.owner_info_label.setObjectName("Subtle")
        info_layout.addWidget(self.owner_info_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        self.video_frame = QFrame()
        self.video_frame.setObjectName("Card")

        video_layout = QVBoxLayout()
        self.video_label = QLabel("Video Alanı")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.video_label.setMinimumSize(320, 180)
        self.video_label.setStyleSheet(
            "background-color: #020617; border-radius: 10px; border: 1px solid #1f2937;"
        )

        video_layout.addWidget(self.video_label)
        self.video_frame.setLayout(video_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Plaka", "Durum", "Tarih"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        content_layout.addWidget(self.video_frame, 2)
        content_layout.addWidget(self.table, 1)

        main_layout.addWidget(header_card)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(access_layout)
        main_layout.addLayout(info_layout)
        main_layout.addLayout(content_layout)

    def set_status_badge(self, text, color):
        self.status_badge.setText(text)
        self.status_badge.setStyleSheet(
            f"""
            QLabel#StatusBadge {{
                border-radius: 10px;
                padding: 8px 12px;
                background-color: {color};
                color: #f8fafc;
                font-weight: 600;
            }}
            """
        )

    def set_last_detection(self, plate, status, timestamp):
        self.last_plate_label.setText(f"Son Plaka: {plate}")
        self.last_time_label.setText(f"Zaman: {timestamp}")
        self.last_status_label.setText(f"Durum: {status}")

    @staticmethod
    def build_status_item(status):
        status_upper = status.upper()
        item = QTableWidgetItem(status_upper)
        if status_upper == "AUTHORIZED":
            item.setForeground(QBrush(QColor("#22c55e")))
        elif status_upper == "UNAUTHORIZED":
            item.setForeground(QBrush(QColor("#ef4444")))
        else:
            item.setForeground(QBrush(QColor("#f59e0b")))
        return item