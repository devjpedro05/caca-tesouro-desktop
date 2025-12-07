from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt
from .grid_board_view import GridBoardView  # Changed from BoardView
from .side_panel import SidePanel
from .bottom_bar import BottomBar
import os

class MainWindow(QMainWindow):
    """
    Janela principal do jogo com tema medieval.
    Layout vertical: Topo (BoardView + SidePanel) + BottomBar
    """
    
    def __init__(self, game_state):
        super().__init__()
        self.setWindowTitle("⚔️ Caça ao Tesouro em Redes de Túneis")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        self.game_state = game_state
        
        # Define objectName para estilização QSS
        self.setObjectName("MainWindow")
        
        # ===== CARREGAR TEMA QSS =====
        self._load_stylesheet()
        
        # ===== WIDGET CENTRAL =====
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # ===== LAYOUT PRINCIPAL (Vertical) =====
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== SEÇÃO SUPERIOR (Horizontal: BoardView + SidePanel) =====
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 5)
        top_layout.setSpacing(10)
        
        # GridBoardView (70% da largura) - Changed from BoardView
        self.board_view = GridBoardView(game_state)
        self.board_view.main_window = self
        top_layout.addWidget(self.board_view, stretch=7)
        
        # SidePanel Area (30% da largura) - DIVIDED VERTICALLY IN SCROLL AREA
        
        # Container widget for side panels
        side_container = QWidget()
        side_layout = QVBoxLayout(side_container)
        side_layout.setSpacing(10)
        side_layout.setContentsMargins(0, 0, 0, 0) # Tight margins
        
        # Player 1 Panel (Red)
        p1 = game_state.players[0] if len(game_state.players) > 0 else None
        self.side_panel_p1 = SidePanel(game_state, self, p1)
        side_layout.addWidget(self.side_panel_p1)
        
        # Player 2 Panel (Blue)
        p2 = game_state.players[1] if len(game_state.players) > 1 else None
        self.side_panel_p2 = SidePanel(game_state, self, p2)
        side_layout.addWidget(self.side_panel_p2)
        
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(side_container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Add scroll area to top layout
        top_layout.addWidget(scroll_area, stretch=3)
        
        main_layout.addLayout(top_layout, stretch=1)
        
        # ===== SEÇÃO INFERIOR (BottomBar) =====
        self.bottom_bar = BottomBar(game_state, self)
        main_layout.addWidget(self.bottom_bar)
        
        # ===== REFRESH INICIAL =====
        self.refresh_all()
    
    def _load_stylesheet(self):
        """Carregar e aplicar o tema QSS medieval"""
        try:
            # Caminho para o arquivo QSS
            qss_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets", "themes", "medieval", "medieval_theme.qss"
            )
            
            if os.path.exists(qss_path):
                with open(qss_path, 'r', encoding='utf-8') as f:
                    stylesheet = f.read()
                    
                # Ajustar caminhos relativos das imagens no QSS
                # Converter para caminho absoluto e formato de URL
                base_dir = os.path.dirname(os.path.dirname(__file__))
                assets_path = os.path.join(base_dir, "assets", "themes", "medieval")
                
                # Converter para formato de URL (file:///)
                # No Windows, precisamos converter \ para / e adicionar file:///
                assets_url = assets_path.replace('\\', '/')
                
                # Substituir os caminhos relativos pelos absolutos
                stylesheet = stylesheet.replace(
                    'url(assets/themes/medieval/',
                    f'url({assets_url}/'
                )
                
                self.setStyleSheet(stylesheet)
                print(f"✅ Tema medieval carregado com sucesso de: {qss_path}")
            else:
                print(f"⚠️ Arquivo QSS não encontrado: {qss_path}")
                print("   Usando estilo padrão do sistema.")
        except Exception as e:
            print(f"❌ Erro ao carregar tema QSS: {e}")
            import traceback
            traceback.print_exc()
            print("   Usando estilo padrão do sistema.")

    def refresh_all(self):
        """Atualizar todos os componentes da interface"""
        self.board_view.refresh()
        if hasattr(self, 'side_panel_p1'): self.side_panel_p1.refresh()
        if hasattr(self, 'side_panel_p2'): self.side_panel_p2.refresh()
        self.bottom_bar.refresh()
