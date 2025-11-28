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

## 🔄 Ordem de Implementação Recomendada (11 DIAS)

### 📅 Sprint 1 - Dias 1-4 (Fundação Crítica)
**Diógenes (4 dias):**
- Dia 1-2: Sistema de Combate Completo ⚡
- Dia 3-4: Sistema de Cartas Funcional ⚡

**Luiz (4 dias):**
- Dia 1-2: Barras de Status Visuais
- Dia 3-4: Diálogo de Inventário Visual

**Higor (4 dias):**
- Dia 1-2: Constantes e Enums + Config
- Dia 3-4: Sistema de Sons + Utilitários

**Entrega Sprint 1:** Combate jogável, UI básica, estrutura de suporte

---

### 📅 Sprint 2 - Dias 5-8 (Funcionalidades Core)
**Diógenes (4 dias):**
- Dia 5-6: Sistema de Loot Completo
- Dia 7-8: Sistema de Uso de Itens + Armadilhas

**Luiz (4 dias):**
- Dia 5-6: Diálogo de Seleção de Cartas
- Dia 7-8: Melhorias Visuais do Fog + Efeitos

**Higor (4 dias):**
- Dia 5-6: Testes Unitários Básicos
- Dia 7-8: Documentação Essencial

**Entrega Sprint 2:** Loot, inventário funcional, UI polida

---

### 📅 Sprint 3 - Dias 9-11 (Finalização e Polish)
**Diógenes (3 dias):**
- Dia 9-10: Condições de Vitória/Derrota
- Dia 11: Integração final + Bug fixes

**Luiz (3 dias):**
- Dia 9-10: Animações e Efeitos Visuais
- Dia 11: Ícones e Assets finais

**Higor (3 dias):**
- Dia 9-10: Testes de integração
- Dia 11: Documentação final + README

**Entrega Sprint 3:** Jogo completo e jogável! 🎮

---

### ⏰ Cronograma Detalhado

| Dia | Diógenes | Luiz | Higor |
|-----|----------|------|-------|
| 1 | Combat System (início) | Status Bars | Constants + Enums |
| 2 | Combat System (fim) | Status Bars | GameConfig |
| 3 | Card Effects (início) | Inventory Dialog | SoundManager |
| 4 | Card Effects (fim) | Inventory Dialog | Utils |
| 5 | Loot System (início) | Card Selection Dialog | Testes básicos |
| 6 | Loot System (fim) | Card Selection Dialog | Testes básicos |
| 7 | Item System + Traps | Fog Improvements | Docs (GAMEPLAY) |
| 8 | Item System + Traps | Visual Effects | Docs (API) |
| 9 | Victory/Defeat | Animations | Testes integração |
| 10 | Victory/Defeat | Icons/Assets | Testes integração |
| 11 | **INTEGRAÇÃO FINAL** | **POLISH FINAL** | **DOCS FINAL** |

---

### 🎯 Metas Diárias

**Todos os dias:**
- Commit no final do dia
- Push para branch pessoal
- Atualizar checklist
- Comunicar bloqueios

**Reuniões rápidas:**
- Dia 1 (manhã): Kickoff
- Dia 4 (tarde): Review Sprint 1
- Dia 8 (tarde): Review Sprint 2
- Dia 11 (tarde): Entrega final

---

## 📝 Regras para Evitar Conflitos

### 1. Estratégia de Branches (RECOMENDADO ✅)

**Cada pessoa trabalha em sua própria branch:**

```bash
# Luiz cria sua branch
git checkout -b feature/luiz-ui-improvements

# Higor cria sua branch
git checkout -b feature/higor-utils

# Diógenes cria sua branch
git checkout -b feature/diogenes-combat
```

**Vantagens:**
- ✅ Zero conflitos durante desenvolvimento
- ✅ Trabalho paralelo sem interferência
- ✅ Fácil reverter mudanças
- ✅ Code review antes de merge
- ✅ Histórico limpo

---

### 2. Workflow Diário

**Início do dia:**
```bash
# Atualizar sua branch com main
git checkout main
git pull origin main
git checkout feature/seu-nome-tarefa
git merge main  # Traz atualizações do main
```

**Durante o dia:**
```bash
# Commits pequenos e frequentes
git add .
git commit -m "feat: Adiciona barra de HP visual"
git push origin feature/seu-nome-tarefa
```

**Fim do dia:**
```bash
# Push final
git add .
git commit -m "feat: Completa implementação de StatusBar"
git push origin feature/seu-nome-tarefa

# Criar Pull Request no GitHub
# Aguardar review antes de merge
```

---

### 3. Processo de Merge

**Quando terminar uma tarefa:**

1. **Criar Pull Request (PR) no GitHub:**
   - Ir para: `https://github.com/devjpedro05/caca-tesouro-desktop`
   - Click em "Pull Requests" → "New Pull Request"
   - Base: `main` ← Compare: `feature/sua-branch`
   - Título: "feat: Implementa Sistema de Combate"
   - Descrição: Listar o que foi feito
   - Assignees: Marcar revisor

2. **Code Review:**
   - Outro membro da equipe revisa
   - Comenta se necessário
   - Aprova quando OK

3. **Merge:**
   ```bash
   # Opção 1: Merge via GitHub (RECOMENDADO)
   # Click em "Merge Pull Request" no GitHub
   
   # Opção 2: Merge manual
   git checkout main
   git pull origin main
   git merge feature/sua-branch
   git push origin main
   ```

4. **Limpar branch:**
   ```bash
   # Deletar branch local
   git branch -d feature/sua-branch
   
   # Deletar branch remota
   git push origin --delete feature/sua-branch
   ```

---

### 4. Resolução de Conflitos

**Se houver conflito ao mergear:**

```bash
# 1. Atualizar main
git checkout main
git pull origin main

# 2. Voltar para sua branch
git checkout feature/sua-branch

# 3. Mergear main na sua branch
git merge main

# 4. Se houver conflito, Git vai avisar
# Abrir arquivos com conflito e resolver manualmente

# 5. Após resolver
git add .
git commit -m "fix: Resolve conflitos com main"
git push origin feature/sua-branch
```

**Exemplo de conflito:**
```python
<<<<<<< HEAD
# Seu código
def calculate_damage(attack):
    return attack * 2
=======
# Código do main
def calculate_damage(attack, defense):
    return attack - defense
>>>>>>> main
```

**Resolver para:**
```python
# Versão final (escolher a melhor ou combinar)
def calculate_damage(attack, defense=0):
    return (attack * 2) - defense
```

---

### 5. Convenção de Commits

**Formato:**
```
tipo: Descrição curta (máx 50 chars)

Descrição detalhada opcional (se necessário)
```

**Tipos:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação (sem mudança de lógica)
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Manutenção

**Exemplos:**
```bash
git commit -m "feat: Adiciona sistema de combate por turnos"
git commit -m "fix: Corrige cálculo de dano em monstros"
git commit -m "docs: Atualiza README com instruções de jogo"
git commit -m "refactor: Extrai lógica de loot para LootSystem"
```

---

### 6. Arquivos por Pessoa (Evitar Conflitos)

**Luiz (UI):**
- ✅ `ui/status_bars.py` (novo)
- ✅ `ui/inventory_dialog.py` (novo)
- ✅ `ui/card_selection_dialog.py` (novo)
- ✅ `ui/effects.py` (novo)
- ✅ `assets/icons/*` (novos)
- ⚠️ `ui/grid_board_view.py` (apenas método `_draw_fog()`)

**Higor (Utils):**
- ✅ `core/config.py` (novo)
- ✅ `core/sound_manager.py` (novo)
- ✅ `core/constants.py` (novo)
- ✅ `core/utils.py` (novo)
- ✅ `tests/*` (novos)
- ✅ `docs/*` (novos)

**Diógenes (Core):**
- ✅ `core/combat_system.py` (novo)
- ✅ `core/card_effects.py` (novo)
- ✅ `core/loot_system.py` (novo)
- ✅ `core/item_system.py` (novo)
- ✅ `core/trap_system.py` (novo)
- ✅ `ui/combat_dialog.py` (novo)
- ⚠️ `core/game_state.py` (modificar com cuidado)

**⚠️ Arquivos Compartilhados (Comunicar antes!):**
- `core/game_state.py`
- `ui/grid_board_view.py`
- `ui/main_window.py`

---

### 7. Comunicação de Mudanças

**Antes de modificar arquivo compartilhado:**
```
1. Avisar no grupo: "Vou modificar game_state.py"
2. Aguardar confirmação
3. Fazer mudança
4. Commit e push rápido
5. Avisar: "game_state.py atualizado"
```

**Integração entre pessoas:**
```
Diógenes termina CombatSystem
  ↓
Avisa Luiz: "CombatSystem pronto, pode integrar"
  ↓
Luiz cria CombatDialog usando CombatSystem
  ↓
Testa integração
  ↓
Merge
```

---

### 8. Checklist Diário

**Todo dia, cada pessoa deve:**
- [ ] Pull do main pela manhã
- [ ] Trabalhar na sua branch
- [ ] Commits pequenos e frequentes
- [ ] Push no final do dia
- [ ] Atualizar checklist de tarefas
- [ ] Comunicar bloqueios
- [ ] Revisar PRs de outros (se solicitado)

---

### 9. Exemplo Completo de Workflow

**Dia 1 - Luiz implementa StatusBar:**

```bash
# Manhã
git checkout main
git pull origin main
git checkout -b feature/luiz-status-bars

# Desenvolvimento
# ... cria ui/status_bars.py ...
git add ui/status_bars.py
git commit -m "feat: Cria componente StatusBar para HP/Stamina"

# ... implementa lógica ...
git add ui/status_bars.py
git commit -m "feat: Adiciona animações de mudança de HP"

# ... integra com side_panel ...
git add ui/side_panel.py
git commit -m "feat: Integra StatusBar no painel lateral"

# Fim do dia
git push origin feature/luiz-status-bars

# GitHub
# Cria Pull Request
# Aguarda review de Diógenes ou Higor
# Após aprovação, merge
```

**Resultado:** Trabalho isolado, sem conflitos! ✅

---

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

**Prazo:** 11 dias (Sprint intenso!)

---

## 🚨 Regras para Cumprir o Prazo

### Priorização Agressiva
- **Foco total** nas tarefas atribuídas
- **Sem gold plating** - funcional > perfeito
- **MVP primeiro** - polish depois

### Comunicação Diária
- Daily standup 15min (9h)
- Bloqueios reportados imediatamente
- Ajuda mútua quando necessário

### Qualidade Mínima
- Código funcional > código perfeito
- Testes básicos obrigatórios
- Documentação inline essencial

### Integração Contínua
- Commits pequenos e frequentes
- Pull requests revisados em <2h
- Merge diário na branch dev

Boa sorte, equipe! Vamos conseguir! 🚀💪
