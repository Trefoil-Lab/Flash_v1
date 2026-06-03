import sys
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
)
import interface
from MainWindow import Ui_MainWindow

def main():
    app = QApplication(sys.argv)

    window = test_MainWindow()
    window.show()

    app.exec()

class test_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hello world!')


        # material data
        mat_param_box = QGroupBox()
        mat_param_label = QLabel()
        mat_param_label.setText('Material Parameters')
        mat_param_box.add (mat_param_label)

        # electrical data
        elec_param_box = QVBoxLayout()
        elec_param_label = QLabel()
        elec_param_label.setText('Electrical Parameters')
        elec_param_box.addChildWidget(elec_param_label)
        
        # parameters container
        param_container = QVBoxLayout()
        param_container.addChildLayout(mat_param_box)
        param_container.addChildLayout(elec_param_box)

        # graphs container
        graphs_container = QHBoxLayout()

        # left graph


        # content container (paramaters, graphs)
        content_container = QHBoxLayout()
        content_container.addChildLayout(param_container)
        content_container.addChildLayout(graphs_container)

        # controls container
        controls_container = QHBoxLayout()
        controls_start = QPushButton()
        controls_start.setText('Start')
        controls_container.addChildWidget(controls_start)

        top_level = QVBoxLayout()
        top_level.addChildLayout(controls_container)
        top_level.addChildLayout(content_container)
        self.setCentralWidget(top_level)
        

    def button_press(self):
        self.button.setText("Clicked!")

if __name__ == "__main__":
    main()
