"""Template for a programmatic PyQt dialog in QGIS."""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class ModernDialog(QDialog):
    """A premium, programmatically created dialog."""

    def __init__(self, parent=None):
        """Initialize the modern dialog.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Antigravity - Modern Dialog")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Build the UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("<h2>Configure Analysis</h2>")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Input Group
        input_layout = QHBoxLayout()
        input_label = QLabel("Layer Name:")
        self.layer_input = QLineEdit()
        self.layer_input.setPlaceholderText("Enter layer name...")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.layer_input)
        layout.addLayout(input_layout)

        # Dropdown Group
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Interpolation Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(
            ["Inverse Distance Weighting", "Kriging", "Nearest Neighbor"]
        )
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_run = QPushButton("Run Action")
        self.btn_run.setStyleSheet(
            "background-color: #6f42c1; color: white; "
            "font-weight: bold; border-radius: 4px; padding: 8px;"
        )

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_run.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_run)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_data(self):
        """Return the user input."""
        return {"layer": self.layer_input.text(), "mode": self.mode_combo.currentText()}


if __name__ == "__main__":
    # For standalone testing with PyQt
    import sys

    from qgis.PyQt.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dlg = ModernDialog()
    if dlg.exec_():
        print(f"Data: {dlg.get_data()}")
    sys.exit()
