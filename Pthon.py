from PySide2 import QtWidgets


class MyDialog(QtWidgets.QDialog):
    def __init__(self):
        super(MyDialog, self).__init__()
        self.setWindowTitle("My Dialog")
        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("Hello, world!")
        layout.addWidget(label)
        button = QtWidgets.QPushButton("Click me!")
        button.clicked.connect(self.on_button_clicked)
        layout.addWidget(button)
        self.setLayout(layout)
    def on_button_clicked(self):
        MaxPlus.Core.EvalMAXScript('messageBox "Button clicked!"')
dialog = MyDialog()
dialog.exec_()
