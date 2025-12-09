from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox, QFrame, QProgressBar
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPalette, QColor

class SidePanel(QWidget):
    """
    Painel lateral com tema de pergaminho medieval.
    Contém seções para Quest Log, Evento Atual e Estatísticas do Jogador.
    """
    
    def __init__(self, game_state, main_window, player=None):
        super().__init__()
        self.game_state = game_state
        self.main_window = main_window
        self.player = player  # Specific player to track
        
        # Define objectName para estilização QSS
        self.setObjectName("SidePanel")
        
        # Layout principal vertical
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # ===== SEÇÃO 1: QUEST LOG (Registro de Missões) =====
        self.quest_log_panel = QGroupBox("📜 REGISTRO DE MISSÕES")
        self.quest_log_panel.setObjectName("QuestLogPanel")
        quest_log_layout = QVBoxLayout(self.quest_log_panel)
        
        self.lbl_quest_log = QLabel(
            "• Encontre o tesouro escondido nos túneis\n"
            "• Evite armadilhas e monstros\n"
            "• Economize recursos (ouro)\n"
            "• Chegue primeiro ao tesouro!"
        )
        self.lbl_quest_log.setObjectName("QuestLogText")
        self.lbl_quest_log.setWordWrap(True)
        self.lbl_quest_log.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        quest_log_layout.addWidget(self.lbl_quest_log)
        
        self.layout.addWidget(self.quest_log_panel)
        
        # ===== SEÇÃO 2: CURRENT EVENT (Evento Atual) =====
        self.current_event_panel = QGroupBox("⚡ EVENTO ATUAL")
        self.current_event_panel.setObjectName("CurrentEventPanel")
        current_event_layout = QVBoxLayout(self.current_event_panel)
        
        self.lbl_current_event = QLabel("Aguardando ação do jogador...")
        self.lbl_current_event.setObjectName("CurrentEventText")
        self.lbl_current_event.setWordWrap(True)
        self.lbl_current_event.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        current_event_layout.addWidget(self.lbl_current_event)
        
        self.layout.addWidget(self.current_event_panel)
        
        # ===== SEÇÃO 3: PLAYER STATS (Estatísticas do Jogador) =====
        self.player_stats_panel = QGroupBox("👤 ESTATÍSTICAS DO JOGADOR")
        self.player_stats_panel.setObjectName("PlayerStatsPanel")
        player_stats_layout = QVBoxLayout(self.player_stats_panel)
        
        # Nome do jogador
        self.lbl_player_name = QLabel("Jogador: -")
        self.lbl_player_name.setObjectName("PlayerName")
        player_stats_layout.addWidget(self.lbl_player_name)
        
        # ⭐ BARRA DE HP ANIMADA
        hp_container = QWidget()
        hp_layout = QVBoxLayout(hp_container)
        hp_layout.setContentsMargins(0, 5, 0, 5)
        hp_layout.setSpacing(3)
        
        self.lbl_hp = QLabel("❤️ HP: 100/100")
        self.lbl_hp.setObjectName("PlayerStat")
        hp_layout.addWidget(self.lbl_hp)
        
        self.hp_bar = QProgressBar()
        self.hp_bar.setMinimum(0)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setValue(100)
        self.hp_bar.setTextVisible(False)
        self.hp_bar.setFixedHeight(20)
        self.hp_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #8B4513;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #DC143C, stop:0.5 #FF6347, stop:1 #DC143C);
                border-radius: 3px;
            }
        """)
        hp_layout.addWidget(self.hp_bar)
        player_stats_layout.addWidget(hp_container)
        
        # ⭐ BARRA DE STAMINA ANIMADA
        stamina_container = QWidget()
        stamina_layout = QVBoxLayout(stamina_container)
        stamina_layout.setContentsMargins(0, 5, 0, 5)
        stamina_layout.setSpacing(3)
        
        self.lbl_stamina = QLabel("⚡ Stamina: 100/100")
        self.lbl_stamina.setObjectName("PlayerStat")
        stamina_layout.addWidget(self.lbl_stamina)
        
        self.stamina_bar = QProgressBar()
        self.stamina_bar.setMinimum(0)
        self.stamina_bar.setMaximum(100)
        self.stamina_bar.setValue(100)
        self.stamina_bar.setTextVisible(False)
        self.stamina_bar.setFixedHeight(20)
        self.stamina_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2E8B57;
                border-radius: 5px;
                background-color: #2C1810;
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #32CD32, stop:0.5 #7FFF00, stop:1 #32CD32);
                border-radius: 3px;
            }
        """)
        stamina_layout.addWidget(self.stamina_bar)
        player_stats_layout.addWidget(stamina_container)
        
        # Animações
        self.hp_animation = QPropertyAnimation(self.hp_bar, b"value")
        self.hp_animation.setDuration(500)  # 500ms
        self.hp_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.stamina_animation = QPropertyAnimation(self.stamina_bar, b"value")
        self.stamina_animation.setDuration(400)  # 400ms
        self.stamina_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Posição
        self.lbl_movement = QLabel("🚶 Posição: -")
        self.lbl_movement.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_movement)
        
        # Action Points
        self.lbl_action_points = QLabel("🎯 AP: 3/3")
        self.lbl_action_points.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_action_points)
        
        # Cartas
        self.lbl_cards = QLabel("🃏 Cartas: 0")
        self.lbl_cards.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_cards)
        
        # Ouro
        self.lbl_gold = QLabel("💰 Ouro gasto: 0")
        self.lbl_gold.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_gold)
        
        # Custo total
        self.lbl_cost = QLabel("📊 Total de movimentos: 0")
        self.lbl_cost.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_cost)
        
        self.layout.addWidget(self.player_stats_panel)
        
        # ===== SEÇÃO 4: AÇÕES RÁPIDAS =====
        # Botão de rolar dado
        self.btn_roll = QPushButton("🎲 Rolar Dado")
        self.btn_roll.clicked.connect(self.on_roll_dice)
        self.layout.addWidget(self.btn_roll)
        
        # Botão de usar carta
        self.btn_card = QPushButton("🃏 Usar Carta")
        self.btn_card.clicked.connect(self.on_use_card)
        self.layout.addWidget(self.btn_card)
        
        # ===== SEÇÃO 5: LOG DE EVENTOS =====
        log_label = QLabel("📋 Log de Eventos:")
        log_label.setObjectName("QuestLogTitle")
        self.layout.addWidget(log_label)
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(150)
        self.layout.addWidget(self.txt_log)
        
        # Espaçador para empurrar tudo para cima
        self.layout.addStretch()
        
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
        p = self.game_state.current_player
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
            new_stamina = p.stamina
            if old_stamina != new_stamina:
                self.animate_stamina_change(old_stamina, new_stamina)
            self.stamina_bar.setMaximum(p.max_stamina)
            self.lbl_stamina.setText(f"⚡ Stamina: {p.stamina}/{p.max_stamina}")
            
            # Atualizar estatísticas
            self.lbl_movement.setText(f"🚶 Posição: {self.game_state.graph.vertices[p.current_vertex_id].name}")
            
            # Action Points com cor
            ap_color = "green" if p.action_points > 1 else ("orange" if p.action_points > 0 else "red")
            self.lbl_action_points.setText(f"🎯 AP: {p.action_points}/{p.max_action_points}")
            self.lbl_action_points.setStyleSheet(f"color: {ap_color};")
            
            self.lbl_cards.setText(f"🃏 Cartas: {len(p.hand_cards)}")
            self.lbl_gold.setText(f"💰 Ouro gasto: {p.total_cost}")
            self.lbl_cost.setText(f"📊 Total de movimentos: {len(self.game_state.logs)}")
            
            # Atualizar evento atual
            if hasattr(self.game_state, 'current_event') and self.game_state.current_event:
                self.lbl_current_event.setText(self.game_state.current_event)
            else:
                self.lbl_current_event.setText(f"Turno de {p.name} - Aguardando ação...")
        else:
            self.lbl_player_name.setText("Jogador: -")
            self.lbl_hp.setText("❤️ HP: 0/0")
            self.hp_bar.setValue(0)
            self.lbl_stamina.setText("⚡ Stamina: 0/0")
            self.stamina_bar.setValue(0)
            self.lbl_movement.setText("🚶 Posição: -")
            self.lbl_action_points.setText("🎯 AP: 0/0")
            self.lbl_cards.setText("🃏 Cartas: 0")
            self.lbl_gold.setText("💰 Ouro gasto: 0")
            self.lbl_cost.setText("📊 Total de movimentos: 0")
        
        # Atualizar log
        self.txt_log.clear()
        for log in self.game_state.logs:
            self.txt_log.append(log)
        
        # Scroll para o final
        self.txt_log.verticalScrollBar().setValue(
            self.txt_log.verticalScrollBar().maximum()
        )
            
    def on_roll_dice(self):
        """Rolar dado para movimento"""
        self.game_state.roll_dice()
        self.main_window.refresh_all()
        
    def on_use_card(self):
        """Usar carta da mão"""
        p = self.game_state.current_player
        if p and p.hand_cards:
            card = p.hand_cards[0]
            if self.game_state.play_card(p.id, card.id):
                self.main_window.refresh_all()
            else:
                self.game_state.log(f"Não foi possível usar a carta {card.type.value} (precisa de alvo?).")
                self.main_window.refresh_all()
        self.hp_animation = QPropertyAnimation(self.hp_bar, b"value")
        self.hp_animation.setDuration(500)  # 500ms
        self.hp_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.stamina_animation = QPropertyAnimation(self.stamina_bar, b"value")
        self.stamina_animation.setDuration(400)  # 400ms
        self.stamina_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Posição
        self.lbl_movement = QLabel("🚶 Posição: -")
        self.lbl_movement.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_movement)
        
        # Action Points
        self.lbl_action_points = QLabel("🎯 AP: 3/3")
        self.lbl_action_points.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_action_points)
        
        # Cartas
        self.lbl_cards = QLabel("🃏 Cartas: 0")
        self.lbl_cards.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_cards)
        
        # Ouro
        self.lbl_gold = QLabel("💰 Ouro gasto: 0")
        self.lbl_gold.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_gold)
        
        # Custo total
        self.lbl_cost = QLabel("📊 Total de movimentos: 0")
        self.lbl_cost.setObjectName("PlayerStat")
        player_stats_layout.addWidget(self.lbl_cost)
        
        self.layout.addWidget(self.player_stats_panel)
        
        # ===== SEÇÃO 4: AÇÕES RÁPIDAS =====
        # Botão de rolar dado
        self.btn_roll = QPushButton("🎲 Rolar Dado")
        self.btn_roll.clicked.connect(self.on_roll_dice)
        self.layout.addWidget(self.btn_roll)
        
        # Botão de usar carta
        self.btn_card = QPushButton("🃏 Usar Carta")
        self.btn_card.clicked.connect(self.on_use_card)
        self.layout.addWidget(self.btn_card)
        
        # ===== SEÇÃO 5: LOG DE EVENTOS =====
        log_label = QLabel("📋 Log de Eventos:")
        log_label.setObjectName("QuestLogTitle")
        self.layout.addWidget(log_label)
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(150)
        self.layout.addWidget(self.txt_log)
        
        # Espaçador para empurrar tudo para cima
        self.layout.addStretch()
        
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
        """Atualizar informações do painel com dados do jogador específico"""
        p = self.player
        if not p:
            # Fallback (should not happen in dual panel mode)
            p = self.game_state.current_player
            
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
            
            # Action Points com cor
            # ap_color = "green" if p.action_points > 1 else ("orange" if p.action_points > 0 else "red")
            # self.lbl_action_points.setText(f"🎯 AP: {p.action_points}/{p.max_action_points}")
            # self.lbl_action_points.setStyleSheet(f"color: {ap_color};")
            # REMOVED AP DISPLAY - it's real time now, stamina is king.
            self.lbl_action_points.setText(f"") 
            
            self.lbl_cards.setText(f"🃏 Cartas: {len(p.hand_cards)}")
            self.lbl_gold.setText(f"💰 Ouro: {p.gold}")
            self.lbl_cost.setText(f"📊 Custo Total: {p.total_cost}")
            
            # Atualizar evento atual (global or generic message)
            # if hasattr(self.game_state, 'current_event') and self.game_state.current_event:
            #    self.lbl_current_event.setText(self.game_state.current_event)
            # else:
            self.lbl_current_event.setText(f"Explorando...")
        else:
             pass # Clear fields logic removed for brevity, initialized with defaults
        
        # Atualizar log
        self.txt_log.clear()
        for log in self.game_state.logs:
            self.txt_log.append(log)
        
        # Scroll para o final
        self.txt_log.verticalScrollBar().setValue(
            self.txt_log.verticalScrollBar().maximum()
        )
            
    def on_roll_dice(self):
        """Rolar dado para movimento (Depreciado em tempo real, mantido para compatibilidade)"""
        if self.player:
            val = self.game_state.roll_dice()
            self.game_state.log(f"🎲 {self.player.name} rolou: {val} (Use para testes de sorte!)")
            self.main_window.refresh_all()
        
    def on_use_card(self):
        """Usar carta da mão"""
        p = self.player or self.game_state.current_player
        if p:
            if not p.hand_cards:
                self.game_state.log(f"❌ {p.name} não possui cartas!")
                self.main_window.refresh_all()
                return

            # Open Cards Dialog
            from .cards_dialog import CardsDialog
            dialog = CardsDialog(p, self.game_state, self)
            dialog.exec()
            self.main_window.refresh_all()

    def set_current_event(self, message):
        """Atualizar o evento atual dinamicamente"""
        self.lbl_current_event.setText(message)
