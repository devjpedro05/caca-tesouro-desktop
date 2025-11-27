"""
Interaction Dialog for obstacle encounters
Shows action menu when player encounters an obstacle
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from core.obstacle_manager import ObstacleType

class InteractionDialog(QDialog):
    """Dialog for interacting with obstacles"""
    
    # Signals
    action_selected = Signal(str)  # Emits action type: "attack", "item", "card", "flee"
    
    def __init__(self, obstacle, player, parent=None):
        super().__init__(parent)
        self.obstacle = obstacle
        self.player = player
        self.selected_action = None
        
        self.setWindowTitle("Encontrou um Obstáculo!")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout()
        
        # Title based on obstacle type
        title = self.get_title()
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        description = self.get_description()
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Action buttons
        actions_layout = QVBoxLayout()
        
        # Attack button (for monsters)
        if self.obstacle.obstacle_type == ObstacleType.MONSTER:
            attack_btn = QPushButton("⚔️ Atacar")
            attack_btn.clicked.connect(lambda: self.select_action("attack"))
            actions_layout.addWidget(attack_btn)
        
        # Use Item button
        use_item_btn = QPushButton("🎒 Usar Item do Inventário")
        use_item_btn.clicked.connect(lambda: self.select_action("item"))
        actions_layout.addWidget(use_item_btn)
        
        # Use Card button
        use_card_btn = QPushButton("🎴 Usar Carta")
        use_card_btn.clicked.connect(lambda: self.select_action("card"))
        actions_layout.addWidget(use_card_btn)
        
        # Flee button
        flee_btn = QPushButton("🏃 Fugir / Voltar")
        flee_btn.clicked.connect(lambda: self.select_action("flee"))
        actions_layout.addWidget(flee_btn)
        
        layout.addLayout(actions_layout)
        
        self.setLayout(layout)
    
    def get_title(self):
        """Get title based on obstacle type"""
        if self.obstacle.obstacle_type == ObstacleType.MONSTER:
            monster_type = self.obstacle.data.get("type", "Monstro")
            level = self.obstacle.data.get("level", 1)
            return f"👹 {monster_type.capitalize()} Lv{level} bloqueando o caminho!"
        elif self.obstacle.obstacle_type == ObstacleType.DOOR_LOCKED:
            return "🚪 Porta Trancada!"
        elif self.obstacle.obstacle_type == ObstacleType.CHEST:
            return "📦 Baú de Tesouro!"
        elif self.obstacle.obstacle_type == ObstacleType.TRAP:
            return "🪤 Armadilha Detectada!"
        else:
            return "❓ Obstáculo Encontrado!"
    
    def get_description(self):
        """Get description based on obstacle type"""
        if self.obstacle.obstacle_type == ObstacleType.MONSTER:
            return "Um monstro está bloqueando sua passagem!\nVocê precisa derrotá-lo ou fugir."
        elif self.obstacle.obstacle_type == ObstacleType.DOOR_LOCKED:
            required = self.obstacle.required_item or "chave"
            return f"A porta está trancada.\nVocê precisa de: {required}"
        elif self.obstacle.obstacle_type == ObstacleType.CHEST:
            return "Você encontrou um baú!\nO que deseja fazer?"
        elif self.obstacle.obstacle_type == ObstacleType.TRAP:
            damage = self.obstacle.data.get("damage", 10)
            return f"Há uma armadilha aqui!\nCausará {damage} de dano se ativada."
        else:
            return "Você encontrou algo no caminho."
    
    def select_action(self, action):
        """Handle action selection"""
        self.selected_action = action
        self.action_selected.emit(action)
        self.accept()
    
    def get_selected_action(self):
        """Get the selected action"""
        return self.selected_action
