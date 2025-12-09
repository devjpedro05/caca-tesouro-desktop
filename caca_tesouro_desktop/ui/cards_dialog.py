from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QGridLayout
from PySide6.QtCore import Qt

class CardsDialog(QDialog):
    """Dialog to show player cards"""
    def __init__(self, player, game_state, parent=None):
        super().__init__(parent)
        self.player = player
        self.game_state = game_state
        self.setWindowTitle(f"🎴 Cartas de {player.name}")
        self.setMinimumSize(400, 500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        lbl_title = QLabel(f"Cartas na Mão ({len(self.player.hand_cards)})")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        # Cards Area (Scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)
        
        row = 0
        col = 0
        for card in self.player.hand_cards:
            btn_card = QPushButton(f"{card.type.value}\n(Lv {card.level})")
            btn_card.setMinimumHeight(80)
            btn_card.clicked.connect(lambda checked=False, c=card: self.use_card(c))
            grid.addWidget(btn_card, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # "Use All" button
        btn_use_all = QPushButton("🃏 Usar Todas as Cartas (Combo!)")
        btn_use_all.setStyleSheet("background-color: #8A2BE2; color: white; font-weight: bold; padding: 10px;")
        btn_use_all.clicked.connect(self.use_all_cards)
        layout.addWidget(btn_use_all)
        
        # Close button
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.reject)
        layout.addWidget(btn_close)

    def use_card(self, card):
        """Use a single card"""
        if self.game_state.play_card(self.player.id, card.id):
            self.game_state.log(f"🎴 {self.player.name} usou {card.type.value}")
            self.accept()
        else:
             pass # Failed (feedback handled by game state log)

    def use_all_cards(self):
        """Use all cards in hand"""
        count = 0
        # Iterate copy of list since we are modifying it
        for card in list(self.player.hand_cards):
             if self.game_state.play_card(self.player.id, card.id):
                 count += 1
        
        self.game_state.log(f"💥 COMBO! {self.player.name} usou {count} cartas de uma vez!")
        self.accept()
