import re
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QCursor, QPixmap, QFont, QKeySequence
import pytesseract
from PIL import ImageGrab
import sys
from overlay import RectangleOverlay

def main():
    app = QApplication(sys.argv)
    overlay = RectangleOverlay()
    overlay.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()