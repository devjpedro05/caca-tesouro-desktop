#!/usr/bin/env python3
"""
Script para gerar documentação completa do projeto em Markdown
"""

def generate_full_documentation():
    doc = """# 📚 DOCUMENTAÇÃO COMPLETA DO PROJETO CAÇA AO TESOURO

## Documentação Técnica e Didática - Aplicação de Algoritmos de Grafos em Jogos

**Autor**: Projeto Educacional  
**Data**: Dezembro 2024  
**Linguagem**: Python 3.8+  
**Framework**: PySide6

---

## SUMÁRIO

1. [Introdução ao Projeto](#1-introdução-ao-projeto)
2. [Fundamentos de Teoria dos Grafos](#2-fundamentos-de-teoria-dos-grafos)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [Algoritmos de Grafos Implementados](#4-algoritmos-de-grafos-implementados)
5. [Sistema de Mapas e Grid](#5-sistema-de-mapas-e-grid)
6. [Mecânicas do Jogo](#6-mecânicas-do-jogo)
7. [Fluxo de Gameplay Completo](#7-fluxo-de-gameplay-completo)
8. [Implementação Técnica Detalhada](#8-implementação-técnica-detalhada)
9. [Conclusão](#9-conclusão)

---

# 1. INTRODUÇÃO AO PROJETO

## 1.1 Visão Geral

O **Caça ao Tesouro Desktop** é um jogo educacional desenvolvido em Python que demonstra a aplicação prática de **algoritmos de grafos** em um ambiente de exploração de dungeons medievais. O projeto foi desenvolvido como uma ferramenta didática para ensinar conceitos de:

- **Teoria dos Grafos**: Representação de ambientes como redes de vértices e arestas
- **Algoritmos de Busca**: BFS (Busca em Largura) e DFS (Busca em Profundidade)
- **Algoritmos de Caminho Mínimo**: Dijkstra e A* (A-Star)
- **Estruturas de Dados**: Filas, pilhas, heaps, dicionários
- **Programação Orientada a Objetos**: Classes, herança, encapsulamento
- **Desenvolvimento de Interfaces Gráficas**: PySide6 (Qt para Python)

## 1.2 Objetivos Educacionais

Este projeto visa demonstrar de forma prática:

1. **Como grafos representam ambientes complexos**: Dungeons como redes de câmaras (vértices) conectadas por túneis (arestas)
2. **Como algoritmos de busca resolvem problemas reais**: Encontrar caminhos, detectar rotas, calcular distâncias
3. **Como estruturas de dados otimizam o desempenho**: Uso de heaps para filas de prioridade, dicionários para memoização
4. **Como integrar teoria e prática**: Transformar algoritmos acadêmicos em mecânicas de jogo interativas

## 1.3 Características Principais do Jogo

### Gameplay
- **Modo Multiplayer Local**: 2 jogadores explorando simultaneamente
- **Exploração de Dungeon**: Grid visual 25x25 representando 6 câmaras interconectadas
- **Sistema de Combate Por Turnos**: Batalhas táticas contra 6 tipos diferentes de monstros
- **Sistema de Cartas Estratégicas**: 10 tipos de cartas que usam algoritmos de grafos
- **Inventário e Recursos**: Gerenciamento de HP, Stamina, Ouro e Itens
- **Fog of War**: Sistema de exploração que revela áreas gradualmente
- **Objetivo**: Ser o primeiro a encontrar o tesouro na câmara final

### Tecnologias Utilizadas
- **Python 3.8+**: Linguagem de programação principal
- **PySide6**: Framework Qt para interface gráfica moderna
- **Algoritmos de Grafos**: BFS, Dijkstra, A* implementados do zero
- **Design Patterns**: Observer, Strategy, State para arquitetura limpa

## 1.4 O Que Você Vai Aprender

Ao estudar este projeto, você compreenderá:

- Como modelar problemas do mundo real usando grafos
- A diferença prática entre BFS, Dijkstra e A*
- Quando usar cada algoritmo de busca
- Como implementar pathfinding eficiente
- Como otimizar código com estruturas de dados adequadas
- Como criar jogos educativos usando Python

---

# 2. FUNDAMENTOS DE TEORIA DOS GRAFOS

## 2.1 O Que É Um Grafo?

Um **grafo** é uma estrutura matemática composta por:

- **Vértices (V)**: Também chamados de nós, representam entidades ou locais
- **Arestas (E)**: Também chamadas de arcos, representam conexões entre vértices
- **Pesos**: Valores numéricos associados às arestas (custo, distância, tempo)

### Representação Matemática
```
G = (V, E)

onde:
V = {v₀, v₁, v₂, ..., vₙ}  (conjunto de vértices)
E = {(vᵢ, vⱼ, w)}          (conjunto de arestas com pesos)
```

### Exemplo Simples
```
Grafo de 4 cidades conectadas por estradas:

    São Paulo ----[120km]---- Rio de Janeiro
        |                           |
      [100km]                    [200km]
        |                           |
    Campinas -----[150km]------ Belo Horizonte
```

Este grafo possui:
- **4 vértices**: {São Paulo, Rio, Campinas, BH}
- **4 arestas**: com pesos representando distâncias em km

## 2.2 Tipos de Grafos

### Grafo Direcionado vs Não-Direcionado

**Não-Direcionado** (usado no jogo):
```
A ←→ B  (pode ir de A para B e de B para A)
```

**Direcionado**:
```
A → B  (só pode ir de A para B)
```

### Grafo Ponderado vs Não-Ponderado

**Ponderado** (usado no jogo):
```
A --[5]-- B  (aresta tem peso/custo)
```

**Não-Ponderado**:
```
A ------- B  (todas arestas custam 1)
```

## 2.3 Aplicação no Jogo: Dungeon Como Grafo

### Mapeamento Conceitual

No Caça ao Tesouro, modelamos o dungeon inteiro como um grafo:

**Vértices = Câmaras do Dungeon**
- Cada câmara é um local que o jogador pode ocupar
- Possui atributos: nome, bioma, recursos, monstros, armadilhas
- Exemplos: "Entrada", "Caverna Azul", "Câmara do Tesouro"

**Arestas = Túneis Conectando Câmaras**
- Cada túnel permite movimento entre duas câmaras
- Possui peso = custo de movimento (stamina gasta, tempo necessário)
- Pode estar em estados diferentes: aberto, bloqueado, instável

### Exemplo Prático do Grafo do Jogo

```
Estrutura do Dungeon (7 vértices, 12 arestas):

v0 = "Entrada" (Spawn Jogador Vermelho)
v1 = "Caverna Azul" (Spawn Jogador Azul)
v2 = "Salão dos Ecos"
v3 = "Túnel Escuro"
v4 = "Ponte de Pedra"
v5 = "Lago Subterrâneo"
v6 = "Câmara do Tesouro" (Objetivo Final)

Conexões com Pesos:

v0 --[peso:3]-- v1  (Túnel da Entrada para Caverna Azul)
v0 --[peso:4]-- v2  (Túnel da Entrada para Salão dos Ecos)
v1 --[peso:2]-- v3  (Túnel da Caverna Azul para Túnel Escuro)
v1 --[peso:5]-- v4  (Túnel da Caverna Azul para Ponte de Pedra)
v2 --[peso:3]-- v4  (Túnel do Salão para Ponte)
v2 --[peso:4]-- v5  (Túnel do Salão para Lago)
v3 --[peso:6]-- v6  (Passagem Secreta para o Tesouro)
v4 --[peso:2]-- v6  (Caminho Direto para o Tesouro)
v5 --[peso:5]-- v6  (Túnel do Lago para o Tesouro)
v1 --[peso:2]-- v2  (Passagem Estreita)
v3 --[peso:3]-- v4  (Túnel Auxiliar)
v4 --[peso:2]-- v5  (Passagem pelo Lago)
```

### Visualização do Grafo

```
           v0 (Entrada)
          /  \\
        [3]  [4]
        /      \\
      v1       v2
     /|\\      /|\\
  [2]| [5] [3]| [4]
   / |   \\  / |   \\
  v3 [2]  v4 [2]  v5
   \\     / \\     /
   [6] [2] [2] [5]
     \\ /     \\ /
       v6 (Tesouro)
```

## 2.4 Propriedades do Grafo do Jogo

1. **Não-Direcionado**: Jogadores podem mover em ambas direções pelos túneis
2. **Ponderado**: Cada túnel tem custo diferente (representa distância/dificuldade)
3. **Conexo**: Inicialmente, todos vértices são alcançáveis a partir de qualquer outro
4. **Dinâmico**: Durante o jogo, arestas podem ser:
   - **Bloqueadas**: Por desabamentos ou cartas
   - **Desbloqueadas**: Usando explosivos ou cartas
   - **Modificadas**: Peso pode ser reduzido com carta "Corda"

## 2.5 Representação em Código

### Lista de Adjacência (Estrutura Usada)

```python
# Estrutura mais eficiente para grafos esparsos
adjacency_list = {
    0: [(1, peso:3), (2, peso:4)],  # v0 conecta a v1 e v2
    1: [(0, peso:3), (3, peso:2), (4, peso:5), (2, peso:2)],
    2: [(0, peso:4), (1, peso:2), (4, peso:3), (5, peso:4)],
    # ... etc
}
```

**Vantagens**:
- Espaço: O(V + E) - Apenas conexões que existem
- Acesso a vizinhos: O(grau do vértice)
- Ideal para grafos esparsos (poucas conexões)

### Matriz de Adjacência (Alternativa)

```python
# Matriz N x N onde N = número de vértices
#     v0  v1  v2  v3  v4  v5  v6
# v0 [ 0   3   4   ∞   ∞   ∞   ∞ ]
# v1 [ 3   0   2   2   5   ∞   ∞ ]
# v2 [ 4   2   0   ∞   3   4   ∞ ]
# ...
```

**Desvantagens**:
- Espaço: O(V²) - Desperdiça memória para grafos esparsos
- Melhor para grafos densos (muitas conexões)

**No nosso jogo**: 7 vértices, 12 arestas = grafo esparso
- Lista: 7 + 12 = 19 entradas
- Matriz: 7 × 7 = 49 células (57% desperdício!)

---

# 3. ARQUITETURA DO SISTEMA

## 3.1 Estrutura de Diretórios Completa

```
caca_tesouro_desktop/
│
├── core/                        # 🧠 Lógica Central do Jogo
│   ├── graph.py                 # Sistema de grafos (Vertex, Edge, Graph)
│   ├── algorithms.py            # Algoritmos de busca (BFS, Dijkstra, A*)
│   ├── grid_map.py              # Conversão grafo → grid visual
│   ├── player.py                # Sistema de jogador (stats, inventário)
│   ├── combat.py                # Sistema de combate por turnos
│   ├── cards.py                 # Sistema de cartas (10 tipos)
│   ├── obstacles.py             # Monstros e obstáculos
│   ├── game_state.py            # Estado global do jogo
│   ├── events.py                # Sistema de eventos
│   └── resources.py             # Gerenciamento de recursos
│
├── ui/                          # 🎨 Interface Gráfica (PySide6)
│   ├── main_qt.py               # Ponto de entrada da aplicação
│   ├── main_window.py           # Janela principal do jogo
│   ├── grid_board_view.py       # Renderização do grid 25x25
│   ├── side_panel.py            # Painel lateral (stats, inventário)
│   ├── bottom_bar.py            # Barra inferior (ações, logs)
│   ├── interaction_dialog.py    # Diálogos de interação (combate, baús)
│   ├── cards_dialog.py          # Interface de seleção de cartas
│   ├── inventory_dialog.py      # Interface do inventário
│   ├── animated_sprite.py       # Sistema de animação de sprites
│   ├── frame_animated_sprite.py # Sprites com frames múltiplos
│   └── goblin_sprite.py         # Sprite específico de goblin
│
├── assets/                      # 📦 Recursos Visuais
│   ├── themes/                  # Temas visuais
│   ├── monster.png              # Sprite de monstro
│   ├── door_locked.png          # Sprite de porta trancada
│   ├── chest.png                # Sprite de baú
│   └── *.png                    # Outras texturas
│
├── tests/                       # 🧪 Testes Unitários
│   ├── test_graph.py
│   ├── test_algorithms.py
│   └── test_combat.py
│
├── docs/                        # 📚 Documentação
│   └── DOCUMENTACAO_COMPLETA.md # Este documento
│
├── README.md                    # Instruções básicas
├── requirements.txt             # Dependências Python
└── generate_documentation.py   # Script gerador de docs
```

## 3.2 Fluxo de Dados no Sistema

```
1. INICIALIZAÇÃO
   ├─> Game State cria Grafo
   ├─> Grafo cria Vértices e Arestas
   ├─> Grid Map converte Grafo → Grid 25x25
   ├─> UI renderiza Grid
   └─> Players são posicionados

2. LOOP DE JOGO
   ├─> Player input (WASD / Setas)
   ├─> Game State valida movimento
   ├─> Algoritmo (BFS/Dijkstra/A*) calcula caminho
   ├─> Player move no Grafo
   ├─> Grid Map atualiza posição visual
   ├─> UI anima movimento
   ├─> Eventos são processados (combate, baús)
   └─> Volta ao início do loop

3. COMBATE
   ├─> Detectar colisão Player ↔ Monster
   ├─> Combat System calcula dano
   ├─> Stats são atualizados
   ├─> UI mostra animações
   └─> Resultados são aplicados

4. CARTAS
   ├─> Player seleciona carta
   ├─> Card System valida uso
   ├─> Algoritmo é executado (ex: BFS para ECO)
   ├─> Grafo é modificado (ex: bloquear aresta)
   └─> UI reflete mudanças
```

## 3.3 Componentes Principais Detalhados

### 3.3.1 Módulo `core/graph.py` - Sistema de Grafos

**Responsabilidade**: Implementação completa da estrutura de grafos

**Classes Principais**:

```python
class BiomeType(Enum):
    """Tipos de ambientes/biomas"""
    CAVE = "cave"
    UNDERGROUND_LAKE = "underground_lake"
    CRYSTAL_CAVERN = "crystal_cavern"
    LAVA_CHAMBER = "lava_chamber"
    # ... mais tipos

class Vertex:
    """Representa uma câmara/local no dungeon"""
    id: int                    # Identificador único
    name: str                  # Nome descritivo
    x, y: float                # Coordenadas 2D para heurística
    biome: BiomeType           # Tipo de ambiente
    hazards: List[HazardType]  # Perigos ambientais
    explored: bool             # Foi visitado?
    has_monster: bool          # Tem monstro?
    monster_type: str          # Tipo do monstro
    resources: Dict[str, int]  # Recursos disponíveis
    obstacles: List[Obstacle]  # Lista de obstáculos

class Edge:
    """Representa um túnel/passagem"""
    id: int                    # Identificador único
    v1_id, v2_id: int          # Vértices conectados
    weight: int                # Custo de atravessar
    edge_type: EdgeType        # Tipo de túnel
    blocked: bool              # Está bloqueado?
    stability: int             # Estabilidade (0-100)
    collapse_chance: float     # Chance de colapsar

class Graph:
    """Grafo completo do dungeon"""
    vertices: Dict[int, Vertex]        # Todos vértices
    edges: Dict[int, Edge]             # Todas arestas
    adj: Dict[int, List[int]]          # Lista de adjacência
```

**Métodos Importantes**:

```python
# Construção do grafo
graph.add_vertex(name, x, y, biome, hazards) → Vertex
graph.add_edge(v1_id, v2_id, weight, type) → Edge

# Navegação
graph.neighbors(vertex_id, include_blocked) → List[(vertex_id, Edge)]
graph.get_edge(v1_id, v2_id) → Edge

# Modificações dinâmicas
graph.block_edge(edge_id)
graph.unblock_edge(edge_id)
graph.remove_edge(edge_id)

# Eventos
graph.trigger_random_collapse(probability) → List[edge_ids]
graph.spawn_random_monsters(probability) → List[vertex_ids]
```

### 3.3.2 Módulo `core/algorithms.py` - Algoritmos de Grafos

**Responsabilidade**: Implementação dos algoritmos de busca e pathfinding

**Funções Principais**:

```python
# Busca em Largura
bfs(graph, start_id, max_depth) → Dict[vertex_id, distance]

# Caminho Mínimo de Dijkstra  
dijkstra(graph, start_id, end_id) → (distances, predecessors)

# Pathfinding A*
a_star(graph, start_id, goal_id) → (path, cost)

# Utilitários
find_reachable_vertices(graph, start_id) → Set[vertex_ids]
find_critical_edges(graph, start_id, end_id) → List[edge_ids]
reconstruct_path(predecessors, start, end) → List[vertex_ids]
```

Veremos cada algoritmo em detalhes na próxima seção.

### 3.3.3 Módulo `core/grid_map.py` - Sistema de Grid

**Responsabilidade**: Converter grafo abstrato em grid visual jogável

**Processo de Conversão**:
1. Cada vértice → Câmara 2x2 no grid
2. Arestas → Túneis 1x1 conectando câmaras
3. Manhattan pathfinding para criar túneis
4. Obstáculos são distribuídos nas câmaras

```python
class GridMap:
    width: int = 25
    height: int = 25
    tile_size: int = 50  # pixels
    tiles: List[List[TileType]]
    
    def create_from_graph(self, graph):
        # Posicionar câmaras 2x2
        # Criar túneis 1x1
        # Distribuir obstáculos
    
    def can_move_to(self, x, y) → bool
    def get_vertex_at_position(self, x, y) → vertex_id
```

### 3.3.4 Módulo `core/game_state.py` - Gerenciador Global

**Responsabilidade**: Coordenação de todos sistemas do jogo

```python
class GameState:
    # Componentes
    graph: Graph
    grid_map: GridMap
    players: List[Player]
    deck: List[Card]
    
    # Estado
    turn_number: int
    game_mode: GameMode  # EXPLORATION, COMBAT, VICTORY, DEFEAT
    game_over: bool
    
    # Sistemas
    event_manager: EventManager
    monster_system: MonsterSystem
    combat_manager: CombatManager
    
    # Métodos principais
    def update(delta_time)           # Loop principal
    def move_player(player_id, edge_id)
    def trigger_combat(player, monster)
    def check_victory()
```

---

Continua..."""
    
    return doc

if __name__ == "__main__":
    print("🚀 Gerando documentação completa em português...")
    doc_content = generate_full_documentation()
    
    # Salvar em arquivo
    with open('docs/DOCUMENTACAO_COMPLETA.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ Documentação criada: {len(doc_content)} caracteres")
    print(f"📄 Arquivo: docs/DOCUMENTACAO_COMPLETA.md")
