from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal

class BottomBar(QWidget):
    """
    Barra inferior com botões de ação do jogo.
    Estilo medieval com botões circulares de pedra e botão dourado de encerrar turno.
    """
    
    # Sinais para ações
    search_clicked = Signal()
    use_item_clicked = Signal()
    move_clicked = Signal()
    attack_clicked = Signal()
    skill_clicked = Signal()
    end_turn_clicked = Signal()
    help_clicked = Signal()
    
    def __init__(self, game_state, main_window):
        super().__init__()
        self.game_state = game_state
        self.main_window = main_window
        
        # Define objectName para estilização QSS
        self.setObjectName("BottomBar")
        
        # Layout horizontal
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.layout.setSpacing(12)
        
        # ===== BOTÕES DE AÇÃO CIRCULARES (Esquerda) =====
        
        # Botão Buscar/Escanear
        self.btn_search = QPushButton("🔍\nBuscar")
        self.btn_search.setObjectName("btnSearch")
        self.btn_search.setToolTip("Buscar por tesouros ou armadilhas na área")
        self.btn_search.clicked.connect(self.on_search)
        self.layout.addWidget(self.btn_search)
        
        # Botão Usar Item
        self.btn_item = QPushButton("🎒\nItem")
        self.btn_item.setObjectName("btnItem")
        self.btn_item.setToolTip("Usar um item do inventário")
        self.btn_item.clicked.connect(self.on_use_item)
        self.layout.addWidget(self.btn_item)
        
        # Botão Mover
        self.btn_move = QPushButton("👣\nMover")
        self.btn_move.setObjectName("btnMove")
        self.btn_move.setToolTip("Mover para uma posição adjacente (clique no mapa)")
        self.btn_move.clicked.connect(self.on_move)
        self.layout.addWidget(self.btn_move)
        
        # Botão Atacar
        self.btn_attack = QPushButton("⚔️\nAtacar")
        self.btn_attack.setObjectName("btnAttack")
        self.btn_attack.setToolTip("Atacar um inimigo próximo")
        self.btn_attack.clicked.connect(self.on_attack)
        self.layout.addWidget(self.btn_attack)
        
        # Botão Habilidade/Magia
        self.btn_skill = QPushButton("✨\nMagia")
        self.btn_skill.setObjectName("btnSkill")
        self.btn_skill.setToolTip("Usar uma habilidade especial ou magia")
        self.btn_skill.clicked.connect(self.on_skill)
        self.layout.addWidget(self.btn_skill)
        
        # ===== ESPAÇADOR CENTRAL =====
        self.layout.addStretch()
        
        # ===== BOTÕES PRINCIPAIS (Direita) =====
        
        # Botão Ajuda
        self.btn_help = QPushButton("?")
        self.btn_help.setObjectName("btnHelp")
        self.btn_help.setToolTip("Mostrar ajuda e regras do jogo")
        self.btn_help.clicked.connect(self.on_help)
        self.layout.addWidget(self.btn_help)
    
    # ===== SLOTS PARA AÇÕES =====
    
    # ===== SLOTS PARA AÇÕES =====
    
    def on_search(self):
        """Ação de buscar/escanear área"""
        # Determine active player (e.g., focused player or player 1 default for single user, or contextual)
        # Since it's real-time/simultaneous, these bottom buttons might be ambiguous.
        # Assuming they apply to the "local" player or Player 1 for now, or finding best heuristic.
        # Let's use P1 (Red) as default for bottom bar clicks if not specified? 
        # Or better: Log that this feature is best used via keyboard/interaction?
        # User requested "implement buttons", so let's make them work for Player 1 or "Main" player.
        
        player = self.game_state.players[0] if self.game_state.players else None
        if not player: return

        self.game_state.log(f"🔍 {player.name} examina a área...")
        self.search_clicked.emit()
        
        # Simple Logic: Check if there's hidden stuff? For now just flavor text/anim
        self.game_state.log(f"   Nada de incomum encontrado à vista.")
        
        self.main_window.refresh_all()
    
    def on_use_item(self):
        """Ação de usar item"""
        player = self.game_state.players[0] if self.game_state.players else None
        if not player: return

        self.game_state.log(f"🎒 {player.name} abre a mochila...")
        self.use_item_clicked.emit()
        
        from .inventory_dialog import InventoryDialog
        inv_dialog = InventoryDialog(player, self)
        inv_dialog.exec()
        
        self.main_window.refresh_all()
    
    def on_move(self):
        """Ação de mover (Centralizar Câmera)"""
        self.game_state.log("🎥 Centralizando câmera nos jogadores")
        self.move_clicked.emit()
        
        if hasattr(self.main_window, 'board_view'):
            self.main_window.board_view.center_on_current_player() # This centers on 'current' (P1 usually)
            
        self.main_window.refresh_all()
    
    def on_attack(self):
        """Ação de atacar"""
        self.game_state.log("⚔️ Para atacar, mova-se em direção ao monstro!")
        self.attack_clicked.emit()
        self.main_window.refresh_all()
    
    def on_skill(self):
        """Ação de usar habilidade/magia"""
        self.game_state.log("✨ Habilidades ainda não aprendidas.")
        self.skill_clicked.emit()
        self.main_window.refresh_all()
    
    def on_help(self):
        """Mostrar ajuda"""
        self.game_state.log("❓ Use Setas ou WASD para mover. Encontre o tesouro!")
        self.help_clicked.emit()
        self.main_window.refresh_all()
    
    def refresh(self):
        """Atualizar estado dos botões baseado no estado do jogo"""
        pass
