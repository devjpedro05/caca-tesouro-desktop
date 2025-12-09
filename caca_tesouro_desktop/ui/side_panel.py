from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox, QFrame, QProgressBar
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPalette, QColor

class SidePanel(QWidget):
    """
    Painel compacto horizontal com cards de informação do jogador.
    """
    
    def __init__(self, game_state, main_window, player=None):
        super().__init__()
        self.game_state = game_state
        self.main_window = main_window
        self.player = player  # Specific player to track
        
        # Define objectName para estilização QSS
        self.setObjectName("SidePanel")
        
        # Layout principal HORIZONTAL para cards lado a lado
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        
        # ===== CARD 1: PLAYER INFO =====
        player_card = QGroupBox("👤 JOGADOR")
        player_card.setObjectName("PlayerStatsPanel")
        player_card_layout = QVBoxLayout(player_card)
        player_card_layout.setSpacing(3)
        player_card_layout.setContentsMargins(5, 5, 5, 5)
        
        # Nome do jogador
        self.lbl_player_name = QLabel("Jogador: -")
        self.lbl_player_name.setObjectName("PlayerName")
        player_card_layout.addWidget(self.lbl_player_name)
        
        # HP Bar
        self.lbl_hp = QLabel("❤️ HP: 100/100")
        self.lbl_hp.setObjectName("PlayerStat")
        player_card_layout.addWidget(self.lbl_hp)
        
        self.hp_bar = QProgressBar()
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(False)
        self.hp_bar.setFixedHeight(15)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: #2C1810;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #DC143C, stop:0.5 #FF6347, stop:1 #DC143C);
                border-radius: 3px;
            }
        """)
        player_card_layout.addWidget(self.hp_bar)
        
        # Stamina Bar
        self.lbl_stamina = QLabel("⚡ Stamina: 100/100")
        self.lbl_stamina.setObjectName("PlayerStat")
        player_card_layout.addWidget(self.lbl_stamina)
        
        self.stamina_bar = QProgressBar()
        self.stamina_bar.setMinimum(0)
        self.stamina_bar.setMaximum(100)
        self.stamina_bar.setValue(100)
        self.stamina_bar.setTextVisible(False)
        self.stamina_bar.setFixedHeight(15)
        self.stamina_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2E8B57;
                border-radius: 5px;
                background-color: #2C1810;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #32CD32, stop:0.5 #7FFF00, stop:1 #32CD32);
                border-radius: 3px;
            }
        """)
        player_card_layout.addWidget(self.stamina_bar)
        
        self.layout.addWidget(player_card, stretch=2)
        
        # ===== CARD 2: STATS =====
        stats_card = QGroupBox("📊 STATUS")
        stats_card.setObjectName("CurrentEventPanel")
        stats_card_layout = QVBoxLayout(stats_card)
        stats_card_layout.setSpacing(3)
        stats_card_layout.setContentsMargins(5, 5, 5, 5)
        
        # Posição
        self.lbl_movement = QLabel("🚶 Posição: -")
        self.lbl_movement.setObjectName("PlayerStat")
        stats_card_layout.addWidget(self.lbl_movement)
        
        # Action Points
        self.lbl_action_points = QLabel("🎯 AP: 3/3")
        self.lbl_action_points.setObjectName("PlayerStat")
        stats_card_layout.addWidget(self.lbl_action_points)
        
        # Cartas
        self.lbl_cards = QLabel("🃏 Cartas: 0")
        self.lbl_cards.setObjectName("PlayerStat")
        stats_card_layout.addWidget(self.lbl_cards)
        
        # Ouro
        self.lbl_gold = QLabel("💰 Ouro: 0")
        self.lbl_gold.setObjectName("PlayerStat")
        stats_card_layout.addWidget(self.lbl_gold)
        
        self.layout.addWidget(stats_card, stretch=1)
        
        # ===== CARD 3: EVENT =====
        event_card = QGroupBox("⚡ EVENTO")
        event_card.setObjectName("QuestLogPanel")
        event_card_layout = QVBoxLayout(event_card)
        event_card_layout.setSpacing(3)
        event_card_layout.setContentsMargins(5, 5, 5, 5)
        
        self.lbl_current_event = QLabel("Aguardando ação...")
        self.lbl_current_event.setObjectName("CurrentEventText")
        self.lbl_current_event.setWordWrap(True)
        self.lbl_current_event.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        event_card_layout.addWidget(self.lbl_current_event)
        
        self.layout.addWidget(event_card, stretch=2)
        
        # ===== LOG AREA (below cards) =====
        log_card = QGroupBox("📋 LOG")
        log_card.setObjectName("QuestLogPanel")
        log_layout = QVBoxLayout(log_card)
        log_layout.setSpacing(0)
        log_layout.setContentsMargins(3, 3, 3, 3)
        
        from PySide6.QtWidgets import QTextEdit
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(80)  # Compact log area
        self.txt_log.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #555;
                font-size: 10px;
                padding: 2px;
            }
        """)
        log_layout.addWidget(self.txt_log)
        
        self.layout.addWidget(log_card, stretch=1)
        
        # Animações para barras
        self.hp_animation = QPropertyAnimation(self.hp_bar, b"value")
        self.hp_animation.setDuration(500)
        self.hp_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.stamina_animation = QPropertyAnimation(self.stamina_bar, b"value")
        self.stamina_animation.setDuration(400)
        self.stamina_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.refresh()

    def animate_hp_change(self, old_value, new_value):
        """Anima mudança de HP"""
        self.hp_animation.stop()
        self.hp_animation.setStartValue(old_value)
        self.hp_animation.setEndValue(new_value)
        self.hp_animation.start()
        
        # Mudar cor da barra baseado no HP
        if new_value > 70:
            color_gradient = "stop:0 #DC143C, stop:0.5 #FF6347, stop:1 #DC143C"  # Vermelho
        elif new_value > 30:
            color_gradient = "stop:0 #FF8C00, stop:0.5 #FFA500, stop:1 #FF8C00"  # Laranja
        else:
            color_gradient = "stop:0 #8B0000, stop:0.5 #DC143C, stop:1 #8B0000"  # Vermelho escuro
        
        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {color_gradient});
                border-radius: 3px;
            }}
        """)
    
    def animate_stamina_change(self, old_value, new_value):
        """Anima mudança de Stamina"""
        self.stamina_animation.stop()
        self.stamina_animation.setStartValue(old_value)
        self.stamina_animation.setEndValue(new_value)
        self.stamina_animation.start()
        
        # Mudar cor da barra baseado na Stamina
        if new_value > 50:
            color_gradient = "stop:0 #32CD32, stop:0.5 #7FFF00, stop:1 #32CD32"  # Verde
        elif new_value > 20:
            color_gradient = "stop:0 #FFD700, stop:0.5 #FFFF00, stop:1 #FFD700"  # Amarelo
        else:
            color_gradient = "stop:0 #FF4500, stop:0.5 #FF6347, stop:1 #FF4500"  # Vermelho

        self.stamina_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #2E8B57;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {color_gradient});
                border-radius: 3px;
            }}
        """)

    def refresh(self):
        """Atualizar informações do painel com dados do jogo"""
        # Use the specific player assigned to this panel, not current_player
        p = self.player
        if p:
            # Atualizar nome do jogador com cor
            self.lbl_player_name.setText(f"Jogador: {p.name}")
            self.lbl_player_name.setStyleSheet(f"color: {p.color}; font-weight: bold; font-size: 14px;")
            
            # ⭐ Atualizar HP com animação
            old_hp = self.hp_bar.value()
            new_hp = p.hp
            if old_hp != new_hp:
                self.animate_hp_change(old_hp, new_hp)
            self.hp_bar.setMaximum(p.max_hp)
            self.lbl_hp.setText(f"❤️ HP: {p.hp}/{p.max_hp}")
            
            # ⭐ Atualizar Stamina com animação
            old_stamina = self.stamina_bar.value()
            new_stamina = int(p.stamina)
            if old_stamina != new_stamina:
                self.animate_stamina_change(old_stamina, new_stamina)
            self.stamina_bar.setMaximum(p.max_stamina)
            self.lbl_stamina.setText(f"⚡ Stamina: {int(p.stamina)}/{p.max_stamina}")
            
            # Atualizar estatísticas
            vertex_name = "?"
            if 0 <= p.current_vertex_id < len(self.game_state.graph.vertices):
                 vertex_name = self.game_state.graph.vertices[p.current_vertex_id].name
            self.lbl_movement.setText(f"🚶 Posição: {vertex_name}")
            
            # Action Points - removido (não usado em modo tempo real)
            # Mostrar level ao invés de AP
            self.lbl_action_points.setText(f"⭐ Nível: {p.level}")
            
            self.lbl_cards.setText(f"🃏 Cartas: {len(p.hand_cards)}")
            self.lbl_gold.setText(f"💰 Ouro: {p.gold}")
            
            # Atualizar evento atual
            self.lbl_current_event.setText(f"Explorando...")
        else:
            self.lbl_player_name.setText("Jogador: -")
            self.lbl_hp.setText("❤️ HP: 0/0")
            self.hp_bar.setValue(0)
            self.lbl_stamina.setText("⚡ Stamina: 0/0")
            self.stamina_bar.setValue(0)
            self.lbl_movement.setText("🚶 Posição: -")
            self.lbl_action_points.setText("🎯 AP: -/-")
            self.lbl_cards.setText("🃏 Cartas: 0")
            self.lbl_gold.setText("💰 Ouro: 0")
            self.lbl_current_event.setText("Aguardando...")
        
        # Atualizar log (últimas 10 mensagens)
        if hasattr(self, 'txt_log'):
            self.txt_log.clear()
            recent_logs = self.game_state.logs[-10:] if len(self.game_state.logs) > 10 else self.game_state.logs
            for log in recent_logs:
                self.txt_log.append(log)
            
            # Scroll para o final
            self.txt_log.verticalScrollBar().setValue(
                self.txt_log.verticalScrollBar().maximum()
            )
            self.lbl_gold.setText("💰 Ouro: 0")
            self.lbl_current_event.setText("Aguardando...")

    def animate_hp_change(self, old_value, new_value):
        """Anima mudança de HP"""
        self.hp_animation.stop()
        self.hp_animation.setStartValue(old_value)
        self.hp_animation.setEndValue(new_value)
        self.hp_animation.start()
        
        # Mudar cor da barra baseado no HP
        if new_value > 70:
            color_gradient = "stop:0 #DC143C, stop:0.5 #FF6347, stop:1 #DC143C"  # Vermelho
        elif new_value > 30:
            color_gradient = "stop:0 #FF8C00, stop:0.5 #FFA500, stop:1 #FF8C00"  # Laranja
        else:
            color_gradient = "stop:0 #8B0000, stop:0.5 #DC143C, stop:1 #8B0000"  # Vermelho escuro
        
        self.hp_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {color_gradient});
                border-radius: 3px;
            }}
        """)
    
    def animate_stamina_change(self, old_value, new_value):
        """Anima mudança de Stamina"""
        self.stamina_animation.stop()
        self.stamina_animation.setStartValue(old_value)
        self.stamina_animation.setEndValue(new_value)
        self.stamina_animation.start()
        
        # Mudar cor da barra baseado na Stamina
        if new_value > 50:
            color_gradient = "stop:0 #32CD32, stop:0.5 #7FFF00, stop:1 #32CD32"  # Verde
        elif new_value > 20:
            color_gradient = "stop:0 #FFD700, stop:0.5 #FFFF00, stop:1 #FFD700"  # Amarelo
        else:
            color_gradient = "stop:0 #FF4500, stop:0.5 #FF6347, stop:1 #FF4500"  # Vermelho

        self.stamina_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #2E8B57;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {color_gradient});
                border-radius: 3px;
            }}
        """)

    def on_roll_dice(self):
        """Rolar dado para movimento (Depreciado em tempo real, mantido para compatibilidade)"""
        if self.player:
            self.game_state.log(f"🎲 {self.player.name} rolou o dado (mas deve usar WASD/Setas para mover!)")
        
    def on_use_card(self):
        """Usar carta da mão"""
        p = self.player or self.game_state.current_player
        if p and p.hand_cards:
            card = p.hand_cards[0]
            if self.game_state.play_card(p.id, card.id):
                self.main_window.refresh_all()
            else:
                self.game_state.log(f"Não foi possível usar a carta {card.type.value} (precisa de alvo?).")
                self.main_window.refresh_all()
        else:
            self.game_state.log("Sem cartas na mão!")
            self.main_window.refresh_all()

    def set_current_event(self, message):
        """Atualizar o evento atual dinamicamente"""
        self.lbl_current_event.setText(message)
