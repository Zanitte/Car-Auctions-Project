from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionViewItem
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize, QRect, QAbstractListModel
import textwrap


class ListModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._data = data or []

    def rowCount(self, parent=None):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._data[index.row()]["text"]
        elif role == Qt.DecorationRole:
            image_path = self._data[index.row()].get("image_path")
            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    return pixmap
        return None
class ImageTextDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if not index.data():
            return

        style = QApplication.style() if not option.widget else option.widget.style()
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        text_rect = opt.rect

        pixmaps = index.data(Qt.DecorationRole)
        if pixmaps is None:
            return


        if isinstance(pixmaps, list):
            x_offset = text_rect.left()
            for pixmap in pixmaps:
                if pixmap:
                    pixmap_rect = QRect(x_offset, text_rect.top(), pixmap.width(), pixmap.height())

                    pixmap = pixmap.scaled(pixmap_rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    style.drawItemPixmap(painter, pixmap_rect, Qt.AlignTop, pixmap)

                    x_offset += pixmap.width() + 1  # space between images (lateral)

            text_rect.setLeft(x_offset)

        description = index.data(Qt.DisplayRole)
        if description:
            description_lines = textwrap.wrap(description, width=50)

            line_height = painter.fontMetrics().height()
            y_offset = text_rect.top()
            for line in description_lines:
                painter.drawText(text_rect.left(), y_offset, text_rect.width(), line_height, Qt.TextWordWrap, line)
                y_offset += line_height

    def sizeHint(self, option, index):
        size = QSize()
        if index.isValid():
            pixmaps = index.data(Qt.DecorationRole)
            if pixmaps is not None:
                if isinstance(pixmaps, list):
                    total_width = 0
                    max_height = 0
                    for pixmap in pixmaps:
                        if not pixmap.isNull():
                            total_width += pixmap.width() + 10
                            max_height = max(max_height, pixmap.height())
                    total_width -= 10
                    size.setWidth(total_width)
                    size.setHeight(90)   # space between listings
                size += QStyledItemDelegate.sizeHint(self, option, index)
            description = index.data(Qt.DisplayRole)
            if description:
                description_lines = description.split('\n')
                text_height = option.fontMetrics.height() * len(
                    description_lines)
                size.setHeight(max(size.height(), text_height))
        return size


