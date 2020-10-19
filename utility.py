import matplotlib.pyplot as plt
from PyQt5 import QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, FigureCanvasAgg


class TeXRenderer:
    """Класс, отвечающий за отрисовку формул, написанных с помомщью LaTeX"""
    def __init__(self, font_size=12, dpi=300):
        self.fig = Figure(dpi=dpi)
        self.fig.set_canvas(FigureCanvasAgg(self.fig))
        self.renderer = self.fig.canvas.get_renderer()
        self.font_size = font_size

    def draw_formula(self, formula: str) -> QtGui.QPixmap:
        fig = self.fig
        fig.clear()
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        tex = ax.text(0, 0, formula, ha='left', va='bottom', fontsize=self.font_size)
        width, height = fig.get_size_inches()
        fig_bbox = fig.get_window_extent(self.renderer)
        text_bbox = tex.get_window_extent(self.renderer)
        tight_width = text_bbox.width * width / fig_bbox.width
        tight_height = text_bbox.height * height / fig_bbox.height
        fig.set_size_inches(tight_width, tight_height)
        buf, size = fig.canvas.print_to_buffer()
        image = QtGui.QImage.rgbSwapped(QtGui.QImage(buf, *size, QtGui.QImage.Format_ARGB32))
        pixmap = QtGui.QPixmap(image)
        return pixmap
# TODO
#
# class MatplotlibPlotter(FigureCanvasQTAgg):
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         pass
