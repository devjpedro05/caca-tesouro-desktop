from PySide6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
from PySide6.QtCore import Qt

class InventoryDialog(QDialog):
    """Dialog to show player inventory"""
    def __init__(self, player, parent=None):
        super().__init__(parent)
        self.player = player
        self.setWindowTitle(f"🎒 Inventário de {player.name}")
        self.setMinimumSize(300, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        lbl_title = QLabel(f"Itens de {self.player.name}")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        # List
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Populate
        if not self.player.inventory:
            self.list_widget.addItem("Inventário vazio")
        else:
            for item, count in self.player.inventory.items():
                self.list_widget.addItem(f"{count}x {item}")
        
        # Close button
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
