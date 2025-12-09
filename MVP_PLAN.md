# 🎮 MVP - Caça ao Tesouro (Mínimo Viável)

## 🎯 Objetivo

Jogo cooperativo/competitivo completo onde 2 jogadores exploram dungeon, combatem monstros e competem para encontrar o tesouro primeiro.

---

## ✅ Status Atual (Já Implementado)

### Core Mechanics

- [x] Movimento simultâneo (WASD / Setas)
- [x] Grid 20x20 com câmaras e túneis
- [x] Fog of War independente
- [x] Sistema de combate tick-based
- [x] Goblins com animação e patrulha
- [x] Consumo de stamina
- [x] HP/Stamina/Gold tracking

### Problemas a Corrigir

- [ ] Combate não está funcionando completamente
- [ ] Condições de vitória não estão claras
- [ ] Falta feedback visual de ações

---

## 🚀 MVP - O Mínimo do Mínimo

### 1. Sistema de Combate Funcional ⚔️

**Status:** 🔴 CRÍTICO - Precisa funcionar completamente

#### 1.1 Iniciar Combate

- [x] Dialog aparece ao encontrar monstro
- [ ] **FIX:** Botão "Iniciar Combate" precisa realmente iniciar o combate
- [ ] Player e Monstro aparecem travados (não se movem)
- [ ] Barras de HP visíveis para ambos

#### 1.2 Combate Tick-Based

- [x] Sistema já existe (`CombatManager`)
- [ ] **FIX:** Garantir que está rodando durante dialog
- [ ] Mostrar dano em tempo real
- [ ] Animação de ataque (shake/flash)
- [ ] Som de golpe (opcional)

#### 1.3 Fim do Combate

- [ ] Dialog fecha automaticamente quando:
  - Monstro morre → Player ganha XP e Gold
  - Player morre → Game Over
- [ ] Monstro morto some do mapa
- [ ] Player pode continuar explorando

**Arquivos a modificar:**

```
ui/grid_board_view.py - show_monster_interaction_dialog()
core/systems/combat_system.py - garantir update contínuo
```

---

### 2. Condições de Vitória/Derrota 🏆

#### 2.1 Vitória - Encontrar Tesouro

- [x] Tesouro existe no mapa (vertex 6)
- [ ] **ADICIONAR:** Dialog de vitória ao alcançar tesouro
- [ ] Mostrar stats finais:
  - Tempo decorrido
  - Monstros derrotados
  - Gold coletado
- [ ] Declarar vencedor (quem chegou primeiro)
- [ ] Opção de "Jogar Novamente"

#### 2.2 Derrota - Morte

- [ ] **ADICIONAR:** Dialog de Game Over quando HP = 0
- [ ] Mostrar causa da morte
- [ ] Opção de "Tentar Novamente"
- [ ] Jogador morto fica como "fantasma" observando o outro

#### 2.3 Vitória Cooperativa (Opcional)

- [ ] Ambos precisam chegar ao tesouro
- [ ] Compartilham vitória se ambos vivos

**Arquivos a criar/modificar:**

```
ui/victory_dialog.py (criar)
ui/game_over_dialog.py (criar)
core/dual_game_manager.py - check_victory_conditions()
```

---

### 3. Feedback Visual Essencial 👁️

#### 3.1 Durante Combate

- [ ] Shake effect ao receber dano
- [ ] Flash vermelho no sprite atingido
- [ ] Popup de dano (já existe, verificar se funciona)
- [ ] HP bar diminuindo visivelmente

#### 3.2 Durante Exploração

- [ ] Indicador de stamina baixa (sprite ofegante?)
- [ ] Highlight do tesouro quando visível
- [ ] Indicador de monstros próximos (som/visual)

**Arquivos a modificar:**

```
ui/grid_board_view.py - _on_combat_damage(), _shake_sprite()
```

---

### 4. Balanceamento Básico ⚖️

#### 4.1 Stats dos Players (inicial)

```python
HP: 100
Max HP: 100
Stamina: 100
Attack: 15
Defense: 5
Speed: 5
```

#### 4.2 Stats dos Goblins

```python
HP: 30-50 (baseado em level)
Attack: 8-12
Defense: 2-5
Speed: 3-7
```

#### 4.3 Custos de Stamina

```python
Movimento: 3 por tile
Ataque: 5 por golpe
Regeneração: +10 por segundo (fora de combate)
```

#### 4.4 Sistema de Níveis Simples

- [ ] Monstros em câmaras distantes são mais fortes
- [ ] Tesouro protegido por Goblin Lv5 (boss)

**Arquivos a modificar:**

```
core/player.py - ajustar stats iniciais
core/obstacles.py - balancear monstros
```

---

### 5. UI/UX Mínima 🎨

#### 5.1 HUD Essencial (já existe)

- [x] HP bar
- [x] Stamina bar
- [x] Gold counter
- [ ] **ADICIONAR:** Timer do jogo
- [ ] **ADICIONAR:** Monstros derrotados

#### 5.2 Dialogs Funcionais

- [x] Dialog de encontro com monstro
- [ ] **FIX:** Combate funcionar dentro do dialog
- [ ] **ADICIONAR:** Victory dialog
- [ ] **ADICIONAR:** Game Over dialog

#### 5.3 Menu de Pausa

- [ ] **ADICIONAR:** Tecla ESC pausa jogo
- [ ] Opções: Continuar, Reiniciar, Sair

**Arquivos a criar:**

```
ui/pause_menu.py
ui/hud_overlay.py (melhorar existente)
```

---

## 📋 Checklist de Implementação (Ordem de Prioridade)

### Sprint 1: Combate Funcional (1-2 dias)

- [ ] 1. Corrigir botão "Iniciar Combate" no dialog
- [ ] 2. Garantir que CombatManager.update() roda durante combate
- [ ] 3. Mostrar dano em tempo real (HP bars atualizando)
- [ ] 4. Dialog fecha automaticamente ao fim do combate
- [ ] 5. Monstro morto some do mapa
- [ ] 6. Testar combate completo de início ao fim

### Sprint 2: Vitória/Derrota (1 dia)

- [ ] 1. Criar VictoryDialog com stats finais
- [ ] 2. Criar GameOverDialog
- [ ] 3. Implementar check_victory_conditions() completo
- [ ] 4. Testar cenário: Player 1 ganha encontrando tesouro
- [ ] 5. Testar cenário: Player 1 morre em combate
- [ ] 6. Testar cenário: Ambos chegam ao tesouro

### Sprint 3: Polish e Balanceamento (1 dia)

- [ ] 1. Adicionar shake effect ao receber dano
- [ ] 2. Adicionar timer de jogo no HUD
- [ ] 3. Balancear stats de players e monstros
- [ ] 4. Adicionar menu de pausa (ESC)
- [ ] 5. Testar gameplay completo 3x

### Sprint 4: Bugs e Testes Finais (1 dia)

- [ ] 1. Corrigir fog of war delay
- [ ] 2. Corrigir overlapping de sprites
- [ ] 3. Prevenir dialogs duplicados
- [ ] 4. Playtest completo com 2 pessoas
- [ ] 5. Ajustes finais baseados em feedback

**TOTAL: 4-5 dias de desenvolvimento**

---

## 🎮 Gameplay Loop Completo (MVP)

```
1. Jogo inicia → 2 players em câmaras separadas
   ↓
2. Exploram dungeon simultaneamente
   ↓
3. Encontram monstros → Combate tick-based
   ↓
4. Derrotam monstros → Ganham Gold/XP
   ↓
5. Continuam explorando
   ↓
6. OBJETIVO: Encontrar tesouro primeiro
   ↓
7. FIM:
   - Vitória: Quem chegar primeiro ao tesouro
   - Derrota: HP = 0
   ↓
8. Tela de resultado → Jogar novamente
```

---

## 🔧 Código Prioritário

### 1. Corrigir Combate (`ui/grid_board_view.py`)

```python
def show_monster_interaction_dialog(self, monster_state, player):
    # ... código existente ...

    # ADICIONAR: Timer para update de combate
    combat_timer = QTimer()
    combat_timer.setInterval(120)  # mesmo do game loop

    def update_combat():
        if hasattr(self.game_state, 'combat_manager'):
            # Força update do combate
            self.game_state.combat_manager.update(0.12)

            # Atualiza HP bars no dialog
            player_hp_label.setText(f"{player.hp}/{player.max_hp}")
            monster_hp_label.setText(f"{monster_state.monster.hp}/{monster_state.monster.max_hp}")

            # Verifica fim do combate
            if not player.is_alive or not monster_state.monster.is_alive():
                combat_timer.stop()
                dialog.close()

    combat_timer.timeout.connect(update_combat)

    # Quando clica "Iniciar Combate"
    combat_btn.clicked.connect(lambda: [
        self.game_state.combat_manager.start_combat(player, monster_state.monster),
        combat_timer.start()
    ])
```

### 2. Victory Dialog (`ui/victory_dialog.py` - CRIAR)

```python
class VictoryDialog(QDialog):
    def __init__(self, winner, stats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🏆 VITÓRIA!")

        layout = QVBoxLayout()

        # Winner announcement
        title = QLabel(f"🎉 {winner.name} encontrou o tesouro!")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Stats
        stats_label = QLabel(f"""
        ⏱️ Tempo: {stats['time']}
        ⚔️ Monstros derrotados: {stats['monsters_killed']}
        💰 Gold coletado: {stats['gold']}
        """)
        layout.addWidget(stats_label)

        # Buttons
        play_again_btn = QPushButton("🔄 Jogar Novamente")
        quit_btn = QPushButton("❌ Sair")

        layout.addWidget(play_again_btn)
        layout.addWidget(quit_btn)

        self.setLayout(layout)
```

### 3. Check Victory (`core/dual_game_manager.py`)

```python
def check_victory_conditions(self) -> Optional[Player]:
    """Verifica condições de vitória"""

    # Player 1 alcançou tesouro?
    if self.game_state_p1.game_mode == GameMode.VICTORY:
        return self.game_state_p1.players[0]

    # Player 2 alcançou tesouro?
    if self.game_state_p2.game_mode == GameMode.VICTORY:
        return self.game_state_p2.players[0]

    # Algum player morreu?
    if not self.game_state_p1.players[0].is_alive:
        # P2 ganha por eliminação
        return self.game_state_p2.players[0]

    if not self.game_state_p2.players[0].is_alive:
        # P1 ganha por eliminação
        return self.game_state_p1.players[0]

    return None  # Jogo continua
```

---

## 🎯 Critérios de Sucesso do MVP

### Funcional

- [ ] Combate funciona de início ao fim
- [ ] Monstros morrem e somem do mapa
- [ ] Players podem morrer
- [ ] Tesouro pode ser encontrado
- [ ] Vencedor é declarado corretamente
- [ ] Pode jogar novamente após fim

### Performance

- [ ] 60 FPS constante
- [ ] Sem crashes durante 10min de gameplay
- [ ] Movimento responsivo (<50ms input lag)

### UX

- [ ] Regras do jogo são claras
- [ ] Feedback visual de ações importantes
- [ ] Não há bugs bloqueantes
- [ ] Dois jogadores conseguem jogar simultaneamente

---

## 📝 Notas Finais

### Scope Creep - O que NÃO fazer no MVP

❌ Sistema de itens complexo
❌ Múltiplos tipos de monstro
❌ Skill tree
❌ Saves
❌ Multiplayer online
❌ Áudio
❌ Configurações avançadas

### Foco Total

✅ Combate funcionando
✅ Vitória/Derrota clara
✅ Gameplay loop completo
✅ Bug-free experience

---

**Meta:** MVP jogável e completo em **4-5 dias** ⏱️
**Status Atual:** Dia 1 - Implementando combate funcional
