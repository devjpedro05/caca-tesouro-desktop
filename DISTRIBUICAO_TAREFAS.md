# 👥 Distribuição de Tarefas - Caça ao Tesouro

## 📋 Organização da Equipe

**Objetivo:** Implementar as funcionalidades pendentes do jogo de forma paralela, evitando conflitos de código.

---

## 🎨 LUIZ - Design e Interface Visual

**Perfil:** Bom com design e UI/UX  
**Arquivos:** Principalmente `ui/` e assets  
**Sem dependências críticas de lógica**

### Tarefas Atribuídas

#### 1. Barras de Status Visuais (Prioridade: Alta)
**Arquivos:** `ui/status_bars.py` (novo)
```python
# Criar componente visual para HP e Stamina
class StatusBar(QWidget):
    - Barra de HP (vermelho/verde)
    - Barra de Stamina (azul)
    - Animações de mudança
```
**Integração:** `ui/side_panel.py` (adicionar ao painel lateral)

#### 2. Diálogo de Inventário Visual (Prioridade: Alta)
**Arquivos:** `ui/inventory_dialog.py` (novo)
```python
# UI para mostrar itens do inventário
class InventoryDialog(QDialog):
    - Grid de itens com ícones
    - Tooltips com descrições
    - Botões de usar/descartar
    - Visual estilo medieval
```

#### 3. Diálogo de Seleção de Cartas (Prioridade: Alta)
**Arquivos:** `ui/card_selection_dialog.py` (novo)
```python
# UI para escolher e usar cartas
class CardSelectionDialog(QDialog):
    - Cartas visuais (estilo baralho)
    - Hover effects
    - Descrição da carta
    - Botão de usar
```

#### 4. Melhorias Visuais do Fog of War (Prioridade: Média)
**Arquivos:** `ui/grid_board_view.py` (modificar `_draw_fog()`)
```python
# Adicionar gradiente de iluminação
- Gradiente radial ao redor do jogador
- Efeito de tocha/lanterna
- Transições suaves
```

#### 5. Animações e Efeitos (Prioridade: Baixa)
**Arquivos:** `ui/effects.py` (novo)
```python
# Efeitos visuais diversos
- Partículas ao coletar itens
- Animação de abertura de baú
- Feedback visual de dano
- Brilho em itens raros
```

#### 6. Ícones e Assets (Prioridade: Média)
**Arquivos:** `assets/icons/` (novos)
```
- Ícones de itens (poções, chaves, etc)
- Ícones de cartas
- Ícones de status
- Texturas adicionais
```

**Tempo Estimado:** 8-12 horas  
**Conflitos:** Nenhum (trabalha em arquivos novos ou UI isolada)

---

## 😴 HIGOR - Tarefas Simples e Independentes

**Perfil:** Prefere tarefas mais fáceis  
**Arquivos:** Utilitários, configurações, documentação  
**Tarefas autocontidas**

### Tarefas Atribuídas

#### 1. Sistema de Configurações (Prioridade: Baixa)
**Arquivos:** `core/config.py` (novo)
```python
# Configurações do jogo
class GameConfig:
    TILE_SIZE = 50
    FOG_OPACITY = 220
    MOVEMENT_COST = 2
    # etc...
    
    @staticmethod
    def load_from_file():
        # Carregar de JSON
    
    @staticmethod
    def save_to_file():
        # Salvar em JSON
```

#### 2. Sistema de Sons (Prioridade: Baixa)
**Arquivos:** `core/sound_manager.py` (novo)
```python
# Gerenciador de áudio
class SoundManager:
    def play_sound(self, sound_name):
        # Tocar efeito sonoro
    
    def play_music(self, music_name):
        # Tocar música de fundo
    
    def stop_all():
        # Parar tudo
```

#### 3. Constantes e Enums (Prioridade: Baixa)
**Arquivos:** `core/constants.py` (novo)
```python
# Centralizar constantes
class ItemType(Enum):
    POTION = "potion"
    KEY = "key"
    WEAPON = "weapon"
    # etc...

class Rarity(Enum):
    COMMON = 1
    RARE = 2
    EPIC = 3
    LEGENDARY = 4
```

#### 4. Utilitários Gerais (Prioridade: Baixa)
**Arquivos:** `core/utils.py` (novo)
```python
# Funções auxiliares
def calculate_distance(pos1, pos2):
    # Distância euclidiana

def get_random_item(rarity):
    # Item aleatório por raridade

def format_time(seconds):
    # Formatar tempo de jogo
```

#### 5. Testes Unitários Básicos (Prioridade: Baixa)
**Arquivos:** `tests/test_utils.py` (novo)
```python
# Testes simples
def test_distance_calculation():
    assert calculate_distance((0,0), (3,4)) == 5

def test_fog_opacity():
    fog = FogOfWar(10, 10)
    assert fog.get_fog_opacity(0, 0) == 220
```

#### 6. Documentação (Prioridade: Média)
**Arquivos:** `docs/` (novos)
```
- CONTRIBUTING.md (como contribuir)
- GAMEPLAY.md (como jogar)
- API.md (documentação de código)
```

**Tempo Estimado:** 4-6 horas  
**Conflitos:** Nenhum (arquivos completamente novos)

---

## 💪 DIÓGENES - Tarefas Críticas e Complexas

**Perfil:** Desenvolvedor experiente  
**Arquivos:** Lógica core do jogo  
**Tarefas mais importantes**

### Tarefas Atribuídas

#### 1. Sistema de Combate Completo (Prioridade: CRÍTICA)
**Arquivos:** `core/combat_system.py` (novo)
```python
# Sistema de combate por turnos
class CombatSystem:
    def __init__(self, player, monster):
        self.player = player
        self.monster = monster
        self.turn = 0
    
    def player_attack(self):
        # Calcular dano
        # Aplicar ao monstro
        # Verificar morte
    
    def monster_attack(self):
        # IA do monstro
        # Calcular dano
        # Aplicar ao jogador
    
    def use_card(self, card):
        # Aplicar efeito da carta
    
    def check_victory(self):
        # Verificar fim de combate
```

**Arquivos:** `ui/combat_dialog.py` (novo)
```python
# UI de combate
class CombatDialog(QDialog):
    - Mostrar HP de ambos
    - Botões de ação
    - Log de combate
    - Animações de ataque
```

#### 2. Sistema de Cartas Funcional (Prioridade: CRÍTICA)
**Arquivos:** `core/card_effects.py` (novo)
```python
# Efeitos das cartas
class CardEffects:
    @staticmethod
    def apply_exploration_card(card, player, game_state):
        # Efeitos de exploração
    
    @staticmethod
    def apply_combat_card(card, combat_system):
        # Efeitos de combate
    
    @staticmethod
    def apply_resource_card(card, player):
        # Efeitos de recurso
```

**Integração:** Conectar com `CardSelectionDialog` do Luiz

#### 3. Sistema de Loot (Prioridade: Alta)
**Arquivos:** `core/loot_system.py` (novo)
```python
# Geração de loot
class LootSystem:
    def generate_chest_loot(self, rarity):
        # Gerar itens aleatórios
        # Baseado em raridade
        return items
    
    def generate_monster_loot(self, monster_level):
        # Loot por matar monstro
        return items
    
    def add_to_inventory(self, player, items):
        # Adicionar ao inventário
```

#### 4. Sistema de Uso de Itens (Prioridade: Alta)
**Arquivos:** `core/item_system.py` (novo)
```python
# Uso de itens
class ItemSystem:
    @staticmethod
    def use_potion(player, potion_type):
        # Restaurar HP/Stamina
    
    @staticmethod
    def use_key(player, door):
        # Destrancar porta
    
    @staticmethod
    def use_tool(player, obstacle):
        # Usar ferramenta em obstáculo
```

**Integração:** Conectar com `InventoryDialog` do Luiz

#### 5. Armadilhas Funcionais (Prioridade: Média)
**Arquivos:** `core/trap_system.py` (novo)
```python
# Sistema de armadilhas
class TrapSystem:
    def detect_trap(self, player, position):
        # Chance de detectar
        # Baseado em habilidade
    
    def trigger_trap(self, player, trap):
        # Aplicar dano
        # Efeitos especiais
    
    def disarm_trap(self, player, trap):
        # Chance de desarmar
        # Recompensa por sucesso
```

#### 6. Condições de Vitória/Derrota (Prioridade: Alta)
**Arquivos:** `core/game_state.py` (modificar)
```python
# Adicionar verificações
def check_victory(self):
    # Jogador encontrou tesouro?
    # Completou objetivos?

def check_defeat(self):
    # Jogadores sem HP?
    # Tempo esgotado?
    
def end_game(self, victory):
    # Mostrar tela final
    # Calcular pontuação
```

**Tempo Estimado:** 12-16 horas  
**Conflitos:** Possível com Luiz (interfaces), coordenar integração

---

## 🔄 Ordem de Implementação Recomendada

### Sprint 1 (Semana 1)
**Diógenes:**
1. Sistema de Combate
2. Sistema de Cartas Funcional

**Luiz:**
1. Barras de Status
2. Diálogo de Inventário

**Higor:**
1. Constantes e Enums
2. Sistema de Configurações

### Sprint 2 (Semana 2)
**Diógenes:**
3. Sistema de Loot
4. Sistema de Uso de Itens

**Luiz:**
3. Diálogo de Seleção de Cartas
4. Melhorias Visuais do Fog

**Higor:**
3. Sistema de Sons
4. Utilitários Gerais

### Sprint 3 (Semana 3)
**Diógenes:**
5. Armadilhas Funcionais
6. Condições de Vitória/Derrota

**Luiz:**
5. Animações e Efeitos
6. Ícones e Assets

**Higor:**
5. Testes Unitários
6. Documentação

---

## 📝 Regras para Evitar Conflitos

### 1. Convenção de Branches
```bash
# Cada pessoa trabalha em sua branch
git checkout -b feature/luiz-ui-improvements
git checkout -b feature/higor-utils
git checkout -b feature/diogenes-combat
```

### 2. Arquivos por Pessoa
- **Luiz:** Apenas `ui/` e `assets/`
- **Higor:** Apenas arquivos novos em `core/` (utils, config, etc)
- **Diógenes:** `core/` (sistemas principais)

### 3. Comunicação
- Avisar no grupo antes de modificar arquivo compartilhado
- Pull requests para revisar antes de merge
- Daily standup (5 min) para alinhar

### 4. Integração
- Diógenes e Luiz: Coordenar interfaces (combate, cartas, inventário)
- Testar integração antes de merge
- Usar signals/slots do Qt para desacoplar

---

## ✅ Checklist de Entrega

### Luiz
- [ ] StatusBar funcionando no painel
- [ ] InventoryDialog abrindo e mostrando itens
- [ ] CardSelectionDialog com visual de cartas
- [ ] Fog com gradiente
- [ ] Pelo menos 3 efeitos visuais
- [ ] 10+ ícones criados

### Higor
- [ ] GameConfig carregando/salvando
- [ ] SoundManager tocando sons
- [ ] Constants.py com todos enums
- [ ] Utils.py com 5+ funções
- [ ] 5+ testes passando
- [ ] 3 documentos criados

### Diógenes
- [ ] Combate funcional (player vs monster)
- [ ] Cartas aplicando efeitos
- [ ] Loot sendo gerado e coletado
- [ ] Itens sendo usados
- [ ] Armadilhas detectáveis/desarmáveis
- [ ] Vitória/Derrota funcionando

---

## 🎯 Meta Final

**Jogo completamente jogável com:**
- Exploração com fog of war ✅ (já feito)
- Combate funcional ⏳ (Diógenes)
- Cartas usáveis ⏳ (Diógenes + Luiz)
- Inventário visual ⏳ (Luiz + Diógenes)
- UI polida ⏳ (Luiz)
- Sons e configurações ⏳ (Higor)

**Prazo Sugerido:** 3 semanas

Boa sorte, equipe! 🚀
