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
        
        # Botão Encerrar Turno (grande e dourado)
        self.btn_end_turn = QPushButton("ENCERRAR TURNO")
        self.btn_end_turn.setObjectName("btnEndTurn")
        self.btn_end_turn.setToolTip("Finalizar seu turno e passar para o próximo jogador")
        self.btn_end_turn.clicked.connect(self.on_end_turn)
        self.layout.addWidget(self.btn_end_turn)
        
        # Botão Ajuda
        self.btn_help = QPushButton("?")
        self.btn_help.setObjectName("btnHelp")
        self.btn_help.setToolTip("Mostrar ajuda e regras do jogo")
        self.btn_help.clicked.connect(self.on_help)
        self.layout.addWidget(self.btn_help)
    
    # ===== SLOTS PARA AÇÕES =====
    
    def on_search(self):
        """Ação de buscar/escanear área"""
        self.game_state.log("🔍 Buscando por tesouros e armadilhas...")
        self.search_clicked.emit()
        # TODO: Implementar lógica de busca
        self.main_window.refresh_all()
    
    def on_use_item(self):
        """Ação de usar item"""
        self.game_state.log("🎒 Abrindo inventário...")
        self.use_item_clicked.emit()
        # TODO: Abrir diálogo de seleção de item
        self.main_window.refresh_all()
    
    def on_move(self):
        """Ação de mover (via clique no mapa)"""
        self.game_state.log("👣 Clique no mapa para se mover")
        self.move_clicked.emit()
        # A movimentação é feita clicando no BoardView
        self.main_window.refresh_all()
    
    def on_attack(self):
        """Ação de atacar"""
        self.game_state.log("⚔️ Modo de ataque ativado")
        self.attack_clicked.emit()
        # TODO: Implementar lógica de combate
        self.main_window.refresh_all()
    
    def on_skill(self):
        """Ação de usar habilidade/magia"""
        self.game_state.log("✨ Selecionando habilidade...")
        self.skill_clicked.emit()
        # TODO: Implementar sistema de habilidades
        self.main_window.refresh_all()
    
    def on_end_turn(self):
        """Encerrar turno do jogador atual"""
        self.game_state.end_turn()
        self.end_turn_clicked.emit()
        self.main_window.refresh_all()
    
    def on_help(self):
        """Mostrar ajuda"""
        self.game_state.log("❓ Abrindo ajuda...")
        self.help_clicked.emit()
        # TODO: Abrir diálogo de ajuda com regras
        self.main_window.refresh_all()
    
    def refresh(self):
        """Atualizar estado dos botões baseado no estado do jogo"""
        # Desabilitar botões se não for o turno do jogador ou se o jogo acabou
        # Por enquanto, todos os botões ficam habilitados
        pass
