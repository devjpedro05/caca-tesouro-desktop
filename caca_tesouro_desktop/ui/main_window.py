from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt, QTimer
from .grid_board_view import GridBoardView  # Changed from BoardView
from .side_panel import SidePanel
import os
import time

class MainWindow(QMainWindow):
    """
    Janela principal do jogo com tema medieval.
    Layout vertical: Topo (BoardView + SidePanel) + BottomBar
    NOVO: Suporta DualGameManager com estados de jogo independentes
    """
    
    def __init__(self, dual_manager):
        super().__init__()
        self.setWindowTitle("⚔️ Caça ao Tesouro - Modo 2 Jogadores")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Store dual game manager
        self.dual_manager = dual_manager
        self.game_state_p1 = dual_manager.game_state_p1
        self.game_state_p2 = dual_manager.game_state_p2
        
        # Track pressed keys for simultaneous player movement
        self.pressed_keys = set()
        
        # Adicionar referência reversa para ambos os game states
        self.game_state_p1.main_window = self
        self.game_state_p2.main_window = self
        
        # For backward compatibility with some code that expects self.game_state
        self.game_state = self.game_state_p1
        
        # Victory tracking
        self._victory_announced = False
        
        # Define objectName para estilização QSS
        self.setObjectName("MainWindow")
        
        # Garantir que a janela principal recebe eventos de teclado
        self.setFocusPolicy(Qt.StrongFocus)
        
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
        
        # ===== SEÇÃO SUPERIOR (Horizontal: Split Screen Views) =====
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 10, 10, 5)
        top_layout.setSpacing(10)
        
        # ===== LEFT SIDE: Player 1 (Red) =====
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Player 1 View - using game_state_p1
        self.board_view_p1 = GridBoardView(self.game_state_p1, player_index=0)
        self.board_view_p1.main_window = self
        left_layout.addWidget(self.board_view_p1, stretch=20)
        
        # Player 1 Side Panel
        p1 = self.dual_manager.get_player1()
        self.side_panel_p1 = SidePanel(self.game_state_p1, self, p1)
        self.side_panel_p1.setMinimumHeight(220)  # Altura mínima para incluir log
        self.side_panel_p1.setMaximumHeight(300)  # Altura máxima para incluir log
        left_layout.addWidget(self.side_panel_p1, stretch=0)
        
        # Player 1 Action Buttons
        self.action_buttons_p1 = self._create_action_buttons(p1, 0)
        left_layout.addWidget(self.action_buttons_p1)
        
        top_layout.addWidget(left_container, stretch=5)
        
        # ===== DIVIDER LINE =====
        from PySide6.QtWidgets import QFrame
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setLineWidth(2)
        top_layout.addWidget(divider)
        
        # ===== RIGHT SIDE: Player 2 (Blue) =====
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Player 2 View - using game_state_p2
        self.board_view_p2 = GridBoardView(self.game_state_p2, player_index=1)
        self.board_view_p2.main_window = self
        right_layout.addWidget(self.board_view_p2, stretch=20)
        
        # Player 2 Side Panel
        p2 = self.dual_manager.get_player2()
        self.side_panel_p2 = SidePanel(self.game_state_p2, self, p2)
        self.side_panel_p2.setMinimumHeight(220)  # Altura mínima para incluir log
        self.side_panel_p2.setMaximumHeight(300)  # Altura máxima para incluir log
        right_layout.addWidget(self.side_panel_p2, stretch=0)
        
        # Player 2 Action Buttons
        self.action_buttons_p2 = self._create_action_buttons(p2, 1)
        right_layout.addWidget(self.action_buttons_p2)
        
        top_layout.addWidget(right_container, stretch=5)
        
        # Keep reference to main board_view for compatibility
        self.board_view = self.board_view_p1
        
        main_layout.addLayout(top_layout, stretch=1)
        
        # ===== SEÇÃO INFERIOR (BottomBar) - REMOVIDA =====
        # Agora cada jogador tem seus próprios botões de ação abaixo do painel
        
        # ===== GAME LOOP TIMER =====
        # Timer to update game state and UI regularly
        self.last_update_time = time.time()
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._game_loop_update)
        self.game_timer.start(16)  # ~60 FPS (16ms)
        
        # ===== REFRESH INICIAL =====
        self.refresh_all()
        
        # Garantir foco na janela principal para capturar teclas
        self.setFocus()
    
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
    
    def _create_action_buttons(self, player, player_index):
        """Criar botões de ação para um jogador específico"""
        from PySide6.QtWidgets import QPushButton
        
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        buttons_layout.setSpacing(8)
        
        # Botão Buscar
        btn_search = QPushButton("🔍\nBuscar")
        btn_search.setObjectName("btnSearch")
        btn_search.setToolTip("Buscar por tesouros ou armadilhas na área")
        btn_search.clicked.connect(lambda: self._on_player_search(player, player_index))
        buttons_layout.addWidget(btn_search)
        
        # Botão Item
        btn_item = QPushButton("🎒\nItem")
        btn_item.setObjectName("btnItem")
        btn_item.setToolTip("Abrir inventário")
        btn_item.clicked.connect(lambda: self._on_player_item(player, player_index))
        buttons_layout.addWidget(btn_item)
        
        # Botão Mover (Centralizar câmera)
        btn_move = QPushButton("👣\nMover")
        btn_move.setObjectName("btnMove")
        btn_move.setToolTip("Centralizar câmera no jogador")
        btn_move.clicked.connect(lambda: self._on_player_move(player, player_index))
        buttons_layout.addWidget(btn_move)
        
        # Botão Atacar
        btn_attack = QPushButton("⚔️\nAtacar")
        btn_attack.setObjectName("btnAttack")
        btn_attack.setToolTip("Atacar um inimigo próximo")
        btn_attack.clicked.connect(lambda: self._on_player_attack(player, player_index))
        buttons_layout.addWidget(btn_attack)
        
        # Botão Magia
        btn_magic = QPushButton("✨\nMagia")
        btn_magic.setObjectName("btnSkill")
        btn_magic.setToolTip("Usar uma habilidade especial")
        btn_magic.clicked.connect(lambda: self._on_player_magic(player, player_index))
        buttons_layout.addWidget(btn_magic)
        
        buttons_layout.addStretch()
        
        return buttons_widget
    
    def _on_player_search(self, player, player_index):
        """Ação de buscar para um jogador específico"""
        if not player:
            return
        
        self.game_state.log(f"🔍 {player.name} examina a área...")
        # Simples: verificar se há algo especial na posição atual
        grid_pos = self.game_state.grid_map.get_player_position(player.id)
        if grid_pos:
            x, y = grid_pos
            obstacle = self.game_state.grid_map.obstacle_manager.get_obstacle((x, y))
            if obstacle and obstacle.is_active:
                self.game_state.log(f"   ⚠️ {player.name} encontrou: {obstacle.obstacle_type.value}!")
            else:
                self.game_state.log(f"   Nada de especial encontrado.")
        
        self.refresh_all()
    
    def _on_player_item(self, player, player_index):
        """Abrir inventário para um jogador específico"""
        if not player:
            return
        
        self.game_state.log(f"🎒 {player.name} abre o inventário")
        from .inventory_dialog import InventoryDialog
        inv_dialog = InventoryDialog(player, self.game_state, self)
        inv_dialog.exec()
        
        self.refresh_all()
    
    def _on_player_move(self, player, player_index):
        """Centralizar câmera no jogador específico"""
        if not player:
            return
        
        self.game_state.log(f"🎥 Centralizando em {player.name}")
        
        # Centralizar a view correspondente no jogador
        if player_index == 0 and hasattr(self, 'board_view_p1'):
            self.board_view_p1.center_on_current_player()
        elif player_index == 1 and hasattr(self, 'board_view_p2'):
            self.board_view_p2.center_on_current_player()
        
        self.refresh_all()
    
    def _on_player_attack(self, player, player_index):
        """Ação de atacar para um jogador específico"""
        if not player:
            return
        
        self.game_state.log(f"⚔️ {player.name}: Para atacar, mova-se em direção ao monstro!")
        self.refresh_all()
    
    def _on_player_magic(self, player, player_index):
        """Ação de magia para um jogador específico"""
        if not player:
            return
        
        self.game_state.log(f"✨ {player.name}: Habilidades ainda não aprendidas.")
        self.refresh_all()
    
    def refresh_all(self):
        """Atualizar todos os componentes da interface"""
        # Refresh both board views in split-screen mode
        if hasattr(self, 'board_view_p1'): self.board_view_p1.refresh()
        if hasattr(self, 'board_view_p2'): self.board_view_p2.refresh()
        if hasattr(self, 'side_panel_p1'): self.side_panel_p1.refresh()
        if hasattr(self, 'side_panel_p2'): self.side_panel_p2.refresh()
    
    def _game_loop_update(self):
        """Called by timer to update game state and UI"""
        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update dual game manager (updates both game states)
        self.dual_manager.update(delta_time)
        
        # Check for victory
        winner = self.dual_manager.check_victory_conditions()
        if winner and not self._victory_announced:
            self._victory_announced = True
            self._show_victory_dialog(winner)
        
        # Refresh UI to reflect changes (HP bars, positions, etc)
        self.refresh_all()
    
    def keyPressEvent(self, event):
        """Capturar eventos de teclado e distribuir para as views apropriadas"""
        key = event.key()
        
        # Player Azul (Blue #0000FF) - WASD -> View P1 (game_state_p1)
        if key in (Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D):
            self.board_view_p1.keyPressEvent(event)
        
        # Player Vermelho (Red #FF0000) - Arrow Keys -> View P2 (game_state_p2)
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            self.board_view_p2.keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Capturar eventos de liberação de tecla e distribuir para as views apropriadas"""
        key = event.key()
        
        # Player Azul (Blue #0000FF) - WASD -> View P1 (game_state_p1)
        if key in (Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D):
            self.board_view_p1.keyReleaseEvent(event)
        
        # Player Vermelho (Red #FF0000) - Arrow Keys -> View P2 (game_state_p2)
        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            self.board_view_p2.keyReleaseEvent(event)
    
    def _show_victory_dialog(self, winner):
        """Show victory dialog when a player wins"""
        from PySide6.QtWidgets import QMessageBox
        
        score_p1, score_p2 = self.dual_manager.get_scores()
        
        title = f"🏆 VITÓRIA - {winner.name}! 🏆"
        message = f"""
{winner.name} VENCEU O JOGO!

📊 Pontuação Final:
{self.dual_manager.get_player1().name}: {score_p1} pontos
{self.dual_manager.get_player2().name}: {score_p2} pontos

⭐ Level: {winner.level}
💰 Ouro: {winner.gold}
🎯 XP: {winner.experience}
"""
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
                min-width: 400px;
            }
            QMessageBox QLabel {
                color: #FFD700;
                font-size: 14px;
                font-weight: bold;
            }
            QMessageBox QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #FFD700;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #FFA500;
            }
        """)
        
        msg_box.exec()
        
        # Stop game loop after victory
        self.game_timer.stop()
