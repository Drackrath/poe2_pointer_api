import re
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QCursor, QPixmap, QFont, QKeySequence
import pytesseract
from PIL import ImageGrab
import sys
from item import Item  # Import the Item class
       
class RectangleOverlay(QWidget):
    def __init__(self, parent=None):
        super(RectangleOverlay, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.rect_width = 300
        self.rect_height = 300

        self.setFixedSize(self.rect_width, self.rect_height)
        self.setMouseTracking(True)
        self.update_position()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(10)

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        self.delay_timer = QTimer(self)
        self.delay_timer.timeout.connect(self.delayed_update)
        self.delay_timer.start(2000)

        self.shortcut = QShortcut(QKeySequence(Qt.Key_F9), self)
        self.shortcut.activated.connect(self.close_application)

        self.latest_ocr_text = ""
        self.latest_item = None

    def delayed_update(self):
        self.update_position()
        self.capture_and_ocr()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(Qt.red)
        pen.setWidth(5)
        painter.setPen(pen)
    
        painter.drawRect(0, 0, self.rect_width, self.rect_height)
    
        if self.latest_item:
            dps_values = self.latest_item.calculate_dps()
            dps_text = f"DPS: Current: {dps_values[0]:.2f}, Base: {dps_values[1]:.2f}, Max Qual: {dps_values[2]:.2f}"
        else:
            dps_text = "DPS: Calculating..."
    
        painter.setFont(QFont("Arial", 10))
    
        text_rect = QRect(10, self.rect_height - 30, self.rect_width - 20, 20)
        
        # Draw semi-transparent black bar without border
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.black)
        painter.setOpacity(0.9)
        painter.drawRect(text_rect)
        
        # Draw DPS text
        painter.setPen(QPen(Qt.white))
        painter.setOpacity(1.0)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignTop, dps_text)
    
        painter.end()

    def capture_and_ocr(self):
        mouse_pos = QCursor.pos()
        overlay_x = mouse_pos.x() - self.rect_width // 2
        overlay_y = mouse_pos.y() - self.rect_height // 2
        capture_rect = QRect(overlay_x, overlay_y, self.rect_width, self.rect_height)

        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(0, capture_rect.x(), capture_rect.y(), capture_rect.width(), capture_rect.height())

        img = pixmap.toImage()

        temp_path = 'temp_overlay.png'
        img.save(temp_path)

        self.run_ocr(temp_path)

    def run_ocr(self, image_path):
        text = pytesseract.image_to_string(image_path)
        print("OCR Output:", text)

        self.latest_ocr_text = text
        self.latest_item = self.parse_item(text)
        
        print("Parsed Item:", self.latest_item)

    def parse_item(self, text):
        name = None
        physical_damage = None
        cold_damage = None
        lightning_damage = None
        chaos_damage = None
        fire_damage = None
        elemental_damage = None
        critical_hit_chance = None
        attacks_per_second = None
        item_level = None
        quality = None  # Added quality parsing

        text = text.lower()
        text = text.replace('dps:', '')

        ocr_misreads = {
            'coup damage': 'cold damage',
            'codt damage': 'cold damage',
            'cotd damage': 'cold damage',
            'cou damage': 'cold damage',
            'coto damage': 'cold damage',
            'cold damage': 'cold damage',
            'lightning damage': 'lightning damage',
            'chaos damage': 'chaos damage',
            'fire damage': 'fire damage',
            'elemental damage': 'elemental damage'
        }

        for misread, correct in ocr_misreads.items():
            text = text.replace(misread, correct)

        def parse_damage_range(damage_str):
            """Helper function to convert damage ranges into tuples."""
            ranges = damage_str.split(',')
            damage_tuples = []
            for dmg_range in ranges:
                min_max = dmg_range.split('-')
                if len(min_max) == 2:
                    damage_tuples.append((int(min_max[0]), int(min_max[1])))
            return damage_tuples

        patterns = {
            'physical_damage': r'physical damage[:\s]+(\d+-\d+)',
            'cold_damage': r'cold damage[:\s]+(\d+-\d+)',
            'lightning_damage': r'lightning damage[:\s]+(\d+-\d+)',
            'chaos_damage': r'chaos damage[:\s]+(\d+-\d+)',
            'fire_damage': r'fire damage[:\s]+(\d+-\d+)',
            'elemental_damage': r'elemental damage[:\s]+(\d{1,3}-\d{1,3}(?:,\s*\d{1,3}-\d{1,3})*)',
            'critical_hit_chance': r'critical hit chance[:\s]+(\d+\.\d+%)',
            'attacks_per_second': r'attacks per second[:\s]+(\d+\.\d+)',
            'item_level': r'item level[:\s]+(\d+)',
            'name': r'([a-z\s]+)',
            'quality': r'quality[:\s\+]+(\d+%)'  # Improved quality regex
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1)
                if key == 'name':
                    name = value.strip()
                elif key == 'physical_damage':
                    physical_damage = parse_damage_range(value.strip())
                elif key == 'cold_damage':
                    cold_damage = parse_damage_range(value.strip())
                elif key == 'lightning_damage':
                    lightning_damage = parse_damage_range(value.strip())
                elif key == 'chaos_damage':
                    chaos_damage = parse_damage_range(value.strip())
                elif key == 'fire_damage':
                    fire_damage = parse_damage_range(value.strip())
                elif key == 'elemental_damage':
                    elemental_damage = parse_damage_range(value.strip())
                elif key == 'critical_hit_chance':
                    critical_hit_chance = value.strip()
                elif key == 'attacks_per_second':
                    attacks_per_second = value.strip()
                elif key == 'item_level':
                    item_level = value.strip()
                elif key == 'quality':  # Handle quality parsing
                    quality = value.strip().replace('%', '')

        if not name or len(name) < 3:
            name = "Unknown Item"

        return Item(name, physical_damage, cold_damage, lightning_damage, chaos_damage, fire_damage, elemental_damage, critical_hit_chance, attacks_per_second, item_level, quality)

    def update_position(self):
        mouse_pos = QCursor.pos()
        overlay_x = mouse_pos.x() - self.rect_width // 2
        overlay_y = mouse_pos.y() - self.rect_height // 2
        self.move(overlay_x, overlay_y)

    def close_application(self):
        self.close()
