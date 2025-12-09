# ui/victory_dialog.py
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class VictoryDialog(QDialog):
    """Dialog shown when a player wins the game"""
    
    play_again = Signal()
    quit_game = Signal()
    
    def __init__(self, winner, stats, parent=None):
        """
        Args:
            winner: Player object who won
            stats: Dict with game statistics
                - 'time': Game duration string
                - 'monsters_killed': Number of monsters defeated
                - 'gold': Gold collected
        """
        super().__init__(parent)
        self.setWindowTitle("🏆 VITÓRIA!")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Set stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #1a4d1a;
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
        
        # Trophy icon and title
        title = QLabel("🏆 VITÓRIA! 🏆")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(32)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Winner announcement
        winner_label = QLabel(f"🎉 {winner.name} encontrou o tesouro!")
        winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winner_font = QFont()
        winner_font.setPointSize(20)
        winner_font.setBold(True)
        winner_label.setFont(winner_font)
        layout.addWidget(winner_label)
        
        layout.addSpacing(20)
        
        # Stats display
        stats_label = QLabel()
        stats_text = f"""
        <div style='text-align: center; font-size: 16px;'>
        <p><b>⏱️ Tempo de Jogo:</b> {stats.get('time', '00:00')}</p>
        <p><b>⚔️ Monstros Derrotados:</b> {stats.get('monsters_killed', 0)}</p>
        <p><b>💰 Gold Coletado:</b> {stats.get('gold', 0)}</p>
        <p><b>💚 HP Restante:</b> {winner.hp}/{winner.max_hp}</p>
        </div>
        """
        stats_label.setText(stats_text)
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setWordWrap(True)
        layout.addWidget(stats_label)
        
        layout.addSpacing(20)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        play_again_btn = QPushButton("🔄 Jogar Novamente")
        play_again_btn.setMinimumHeight(50)
        play_again_btn.clicked.connect(self._on_play_again)
        buttons_layout.addWidget(play_again_btn)
        
        quit_btn = QPushButton("❌ Sair")
        quit_btn.setMinimumHeight(50)
        quit_btn.clicked.connect(self._on_quit)
        buttons_layout.addWidget(quit_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def _on_play_again(self):
        """Emit play again signal and close dialog"""
        self.play_again.emit()
        self.accept()
    
    def _on_quit(self):
        """Emit quit signal and close dialog"""
        self.quit_game.emit()
        self.accept()
