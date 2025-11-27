import sys
import os

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from core.game_state import GameState
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    game_state = GameState.new_default_game()
    window = MainWindow(game_state)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
