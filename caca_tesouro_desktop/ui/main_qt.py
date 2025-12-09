import sys
import os
import locale

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path to ensure imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from core.game_state import GameState
from core.dual_game_manager import DualGameManager
from core.graph import Graph
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Create dual game manager for 2-player mode
    dual_manager = DualGameManager()
    
    # Create shared graph
    graph = Graph.sample_graph()
    
    # Initialize both game states
    dual_manager.initialize_dual_games(graph, "Explorador Azul", "Explorador Vermelho")
    
    # Create window with dual manager
    window = MainWindow(dual_manager)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
