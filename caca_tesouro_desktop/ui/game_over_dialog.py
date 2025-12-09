# ui/game_over_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class GameOverDialog(QDialog):
    """Dialog shown when a player dies"""
    
    try_again = Signal()
    quit_game = Signal()
    
    def __init__(self, player, cause="combate", stats=None, parent=None):
        """
        Args:
            player: Player object who died
            cause: Reason for death (e.g., "combate", "armadilha")
            stats: Optional dict with game statistics
        """
        super().__init__(parent)
        self.setWindowTitle("💀 Game Over")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Set stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #4d1a1a;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #888888;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Skull icon and title
        title = QLabel("💀 GAME OVER 💀")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Death message
        death_msg = QLabel(f"{player.name} foi derrotado!")
        death_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        death_font = QFont()
        death_font.setPointSize(20)
        death_font.setBold(True)
        death_msg.setFont(death_font)
        layout.addWidget(death_msg)
        
        # Cause of death
        cause_label = QLabel(f"Causa: {cause.title()}")
        cause_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cause_font = QFont()
        cause_font.setPointSize(16)
        cause_label.setFont(cause_font)
        layout.addWidget(cause_label)
        
        layout.addSpacing(20)
        
        # Optional stats display
        if stats:
            stats_label = QLabel()
            stats_text = f"""
            <div style='text-align: center; font-size: 16px;'>
            <p><b>⏱️ Tempo Sobrevivido:</b> {stats.get('time', '00:00')}</p>
            <p><b>⚔️ Monstros Derrotados:</b> {stats.get('monsters_killed', 0)}</p>
            <p><b>💰 Gold Coletado:</b> {stats.get('gold', 0)}</p>
            </div>
            """
            stats_label.setText(stats_text)
            stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            stats_label.setWordWrap(True)
            layout.addWidget(stats_label)
            
            layout.addSpacing(20)
        
        # Flavor text
        flavor_text = QLabel("Seus companheiros continuarão a busca pelo tesouro...")
        flavor_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        flavor_text.setStyleSheet("color: #aaaaaa; font-style: italic;")
        layout.addWidget(flavor_text)
        
        layout.addSpacing(20)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        try_again_btn = QPushButton("🔄 Tentar Novamente")
        try_again_btn.setMinimumHeight(50)
        try_again_btn.clicked.connect(self._on_try_again)
        buttons_layout.addWidget(try_again_btn)
        
        quit_btn = QPushButton("❌ Sair")
        quit_btn.setMinimumHeight(50)
        quit_btn.clicked.connect(self._on_quit)
        buttons_layout.addWidget(quit_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def _on_try_again(self):
        """Emit try again signal and close dialog"""
        self.try_again.emit()
        self.accept()
    
    def _on_quit(self):
        """Emit quit signal and close dialog"""
        self.quit_game.emit()
        self.accept()
