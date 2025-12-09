# 📚 DOCUMENTAÇÃO COMPLETA DO PROJETO CAÇA AO TESOURO

## Documentação Técnica e Didática - Aplicação de Algoritmos de Grafos em Jogos

**Autor**: Projeto Educacional  
**Data**: Dezembro 2024  
**Linguagem**: Python 3.8+  
**Framework**: PySide6  
**Linhas de Código**: ~3,800 (core) + ~2,000 (UI) = 5,800 linhas

---

## 📋 SUMÁRIO

1. [Introdução ao Projeto](#1-introdução-ao-projeto)
2. [Fundamentos de Teoria dos Grafos](#2-fundamentos-de-teoria-dos-grafos)
3. [Arquitetura do Sistema](#3-arquitetura-do-sistema)
4. [Algoritmos de Grafos Implementados](#4-algoritmos-de-grafos-implementados)
5. [Sistema de Mapas e Grid](#5-sistema-de-mapas-e-grid)
6. [Mecânicas do Jogo](#6-mecânicas-do-jogo)
7. [Fluxo de Gameplay Completo](#7-fluxo-de-gameplay-completo)
8. [Implementação Técnica Detalhada](#8-implementação-técnica-detalhada)
9. [Exemplos Práticos](#9-exemplos-práticos)
10. [Conclusão](#10-conclusão)

---

# 1. INTRODUÇÃO AO PROJETO

## 1.1 Visão Geral

O **Caça ao Tesouro Desktop** é um jogo educacional desenvolvido em Python que demonstra a aplicação prática de **algoritmos de grafos** em um ambiente de exploração de dungeons medievais. 

O projeto foi criado com o objetivo de ensinar conceitos avançados de ciência da computação de forma interativa e divertida, transformando algoritmos abstratos em mecânicas de jogo tangíveis.

### Por Que Grafos em Jogos?

Grafos são uma das estruturas de dados mais poderosas e versáteis em computação. Eles são usados em:

- **Jogos**: Pathfinding, navegação de IA, sistemas de quests
- **Redes Sociais**: Grafos de amizade, recomendações
- **Mapas e GPS**: Navegação, rotas otimizadas
- **Compiladores**: Análise de dependências
- **Inteligência Artificial**: Árvores de decisão, redes neurais

Este projeto mostra como esses mesmos algoritmos que otimizam o GPS do seu celular podem criar experiências de jogo imersivas.

## 1.2 Objetivos Educacionais

### O Que Você Vai Aprender

1. **Teoria dos Grafos Aplicada**
   - Como modelar problemas reais usando grafos
   - Diferença entre grafos direcionados e não-direcionados
   - Grafos ponderados vs não-ponderados
   - Listas de adjacência vs matrizes de adjacência

2. **Algoritmos de Busca**
   - **BFS (Busca em Largura)**: Exploração nível por nível
   - **DFS (Busca em Profundidade)**: Exploração exaustiva
   - **Dijkstra**: Caminho de custo mínimo
   - **A\* (A-Star)**: Pathfinding heurístico

3. **Estruturas de Dados**
   - Filas (Queue) para BFS
   - Pilhas (Stack) para DFS
   - Heaps (Fila de Prioridade) para Dijkstra e A*
   - Dicionários para memoização

4. **Programação Orientada a Objetos**
   - Classes e Herança
   - Encapsulamento
   - Design Patterns (Strategy, Observer, State)

5. **Desenvolvimento de Jogos**
   - Loops de jogo
   - Sistemas de combate
   - Gerenciamento de estado
   - Interface gráfica com Qt

## 1.3 Características Principais do Jogo

### Gameplay

**Modo de Jogo**:
- 2 jogadores locais (Vermelho e Azul)
- Exploração simultânea de dungeon
- Primeiro a encontrar o tesouro vence

**Mapa**:
- Grid visual 25×25 tiles
- 6 câmaras interconectadas (vértices do grafo)
- 12 túneis de conexão (arestas do grafo)
- Fog of War (áreas não exploradas ficam escuras)

**Sistema de Movimento**:
- Controles: WASD (Azul) e Setas (Vermelho)
- Custo de movimento baseado em stamina
- Animações suaves de transição

**Sistema de Combate**:
- Batalhas por turnos
- 6 tipos de monstros com stats diferentes
- Fórmula de dano balanceada
- Sistema de experiência e level-up

**Sistema de Cartas** (usa algoritmos de grafos):
- 10 tipos de cartas estratégicas
- ECO: usa BFS para revelar área
- VISÃO: usa Dijkstra para mostrar caminho até tesouro
- TELEPORTE: usa A* para movimento instantâneo
- DESABAMENTO: bloqueia arestas do grafo
- E muito mais...

**Recursos e Progressão**:
- HP (Health Points): Vida do jogador
- Stamina: Energia para movimento
- Ouro: Moeda do jogo
- Inventário: Itens colecionáveis
- Experiência e Níveis

### Tecnologias

**Backend (Lógica)**:
- Python 3.8+
- Algoritmos implementados do zero (sem bibliotecas externas)
- ~3,800 linhas de código Python puro

**Frontend (Interface)**:
- PySide6 (Qt for Python)
- QGraphicsView para renderização 2D
- QPropertyAnimation para animações suaves
- ~2,000 linhas de código UI

**Estruturas de Dados**:
- Dicionários (hash maps)
- Heaps (heapq)
- Filas (deque)
- Sets para conjuntos

## 1.4 Fluxo Básico do Jogo

```
INÍCIO
  ↓
Criar Grafo (7 vértices, 12 arestas)
  ↓
Converter Grafo → Grid Visual 25×25
  ↓
Posicionar 2 Jogadores (vértices 0 e 1)
  ↓
Distribuir 4 Monstros
  ↓
Colocar Tesouro (vértice 6)
  ↓
Dar 3 Cartas Iniciais
  ↓
LOOP DO JOGO:
  ├→ Jogador move (usa algoritmo de pathfinding)
  ├→ Processa eventos (combate, baús, armadilhas)
  ├→ Atualiza UI (animações, status)
  └→ Verifica vitória
    ↓
  Se encontrou tesouro → FIM (VITÓRIA!)
```

---

# 2. FUNDAMENTOS DE TEORIA DOS GRAFOS

## 2.1 O Que É Um Grafo?

Um **grafo** é uma estrutura matemática usada para representar relações entre objetos.

### Definição Formal

```
G = (V, E)

Onde:
- V = conjunto de vértices (nodes)
- E = conjunto de arestas (edges) que conectam vértices
```

### Componentes

1. **Vértices (V)**: Representam entidades/locais
   - Também chamados: nós, pontos
   - Exemplo: cidades, pessoas, câmaras

2. **Arestas (E)**: Representam conexões
   - Também chamadas: arcos, links
   - Exemplo: estradas, amizades, túneis
   - Podem ter **peso** (custo/distância)

### Exemplo Simples

```
Grafo de Amizades:

    Alice ---- Bob
      |         |
    Carol ---- Dave

V = {Alice, Bob, Carol, Dave}
E = {(Alice,Bob), (Alice,Carol), (Bob,Dave), (Carol,Dave)}
```

## 2.2 Tipos de Grafos

### 2.2.1 Grafo Direcionado vs Não-Direcionado

**Não-Direcionado** (usado no nosso jogo):
```
A ←→ B  

Se existe aresta (A,B), também existe (B,A)
Pode mover em ambas direções
```

**Direcionado**:
```
A → B  

Aresta (A,B) existe, mas (B,A) não
Movimento unidirecional
```

### 2.2.2 Grafo Ponderado vs Não-Ponderado

**Ponderado** (usado no nosso jogo):
```
A --[peso:5]-- B

Cada aresta tem um valor associado (custo, distância, tempo)
```

**Não-Ponderado**:
```
A --------- B

Todas arestas têm peso implícito = 1
```

### 2.2.3 Grafo Conexo vs Desconexo

**Conexo** (estado inicial do jogo):
```
Todo vértice é alcançável a partir de qualquer outro
```

**Desconexo** (pode acontecer com desabamentos):
```
Existem vértices isolados ou grupos separados
```

## 2.3 Representações de Grafos

### 2.3.1 Lista de Adjacência ✅ (Usada no Projeto)

Armazena para cada vértice uma lista de seus vizinhos:

```python
# Exemplo do jogo
adj = {
    0: [1, 2],           # v0 conecta a v1 e v2
    1: [0, 2, 3, 4],     # v1 conecta a v0, v2, v3, v4
    2: [0, 1, 4, 5],     # v2 conecta a v0, v1, v4, v5
    3: [1, 4, 6],        # v3 conecta a v1, v4, v6
    4: [1, 2, 3, 5, 6],  # v4 conecta a v1, v2, v3, v5, v6
    5: [2, 4, 6],        # v5 conecta a v2, v4, v6
    6: [3, 4, 5]         # v6 conecta a v3, v4, v5
}
```

**Vantagens**:
- Espaço: O(V + E) - Apenas conexões reais
- Iterar vizinhos: O(grau do vértice)
- Ideal para grafos esparsos (poucas arestas)

**Desvantagens**:
- Verificar se aresta existe: O(grau)

### 2.3.2 Matriz de Adjacência

Matriz V×V onde célula [i][j] indica se existe aresta:

```python
# Matriz 7×7 para nosso grafo
#     0  1  2  3  4  5  6
# 0 [ 0  1  1  0  0  0  0 ]
# 1 [ 1  0  1  1  1  0  0 ]
# 2 [ 1  1  0  0  1  1  0 ]
# 3 [ 0  1  0  0  1  0  1 ]
# 4 [ 0  1  1  1  0  1  1 ]
# 5 [ 0  0  1  0  1  0  1 ]
# 6 [ 0  0  0  1  1  1  0 ]
```

**Vantagens**:
- Verificar aresta: O(1)
- Simples de implementar

**Desvantagens**:
- Espaço: O(V²) - Desperdiça memória
- Iterar vizinhos: O(V)

### 2.3.3 Comparação para Nosso Jogo

Nosso grafo: 7 vértices, 12 arestas

| Aspecto | Lista | Matriz |
|---------|-------|--------|
| Espaço | 7 + 12×2 = 31 | 7×7 = 49 |
| Eficiência | ✅ Melhor | ❌ 37% desperdício |
| Acesso vizinhos | O(~3) | O(7) |

**Decisão**: Lista de adjacência (mais eficiente para grafos esparsos)

## 2.4 Aplicação no Jogo: Dungeon Como Grafo

### 2.4.1 Mapeamento Conceitual

No Caça ao Tesouro, o dungeon inteiro é um grafo:

**Vértices = Câmaras**
- Locais que o jogador pode ocupar
- Atributos:
  - Nome (ex: "Entrada", "Câmara do Tesouro")
  - Bioma (caverna, lago, ruínas)
  - Recursos (ouro, poções)
  - Monstros
  - Perigos ambientais

**Arestas = Túneis**
- Conexões que permitem movimento
- Atributos:
  - Peso = custo de movimento (stamina gasta)
  - Tipo (normal, instável, secreto)
  - Estado (aberto, bloqueado)
  - Estabilidade (chance de colapso)

### 2.4.2 Grafo do Jogo - Estrutura Completa

```
VÉRTICES (7 câmaras):

v0: "Entrada" 
    - Posição Grid: (9, 2)
    - Bioma: Caverna
    - Spawn: Jogador Vermelho

v1: "Caverna Azul"
    - Posição Grid: (3, 6)
    - Bioma: Caverna de Cristal
    - Spawn: Jogador Azul

v2: "Salão dos Ecos"
    - Posição Grid: (2, 11)
    - Bioma: Caverna
    - Monstro: Goblin (nível 1)

v3: "Túnel Escuro"
    - Posição Grid: (9, 15)
    - Bioma: Caverna
    - Perigo: Escuridão total

v4: "Ponte de Pedra"
    - Posição Grid: (15, 6)
    - Bioma: Caverna
    - Monstro: Goblin (nível 1)

v5: "Lago Subterrâneo"
    - Posição Grid: (9, 9)
    - Bioma: Lago Subterrâneo
    - Monstro: Goblin (nível 1)

v6: "Câmara do Tesouro" 
    - Posição Grid: (9, 18)
    - Bioma: Ruínas Antigas
    - Monstro: Orc (nível 1) - Boss!
    - Objetivo: TESOURO!
```

```
ARESTAS (12 túneis):

e0:  v0 ←[peso:3]→ v1  (Túnel da Entrada)
e1:  v0 ←[peso:4]→ v2  (Corredor Sul)
e2:  v1 ←[peso:2]→ v3  (Passagem Escura)
e3:  v1 ←[peso:5]→ v4  (Caminho Longo)
e4:  v2 ←[peso:3]→ v4  (Ponte de Pedra)
e5:  v2 ←[peso:4]→ v5  (Passagem do Lago)
e6:  v3 ←[peso:6]→ v6  (Passagem Secreta)
e7:  v4 ←[peso:2]→ v6  (Caminho Direto)
e8:  v5 ←[peso:5]→ v6  (Túnel do Lago)
e9:  v1 ←[peso:2]→ v2  (Passagem Estreita)
e10: v3 ←[peso:3]→ v4  (Túnel Auxiliar)
e11: v4 ←[peso:2]→ v5  (Corredorzinho)
```

### 2.4.3 Visualização ASCII do Grafo

```
                    v0 (Entrada)
                   /  \
                [3]    [4]
                /        \
              v1          v2
             /|\         /|\
          [2]| [5]    [3]| [4]
           / |   \    / |   \
         v3 [2]   v4 [2]  v5
          \      /  \     /
          [6]  [2]  [2] [5]
            \  /      \ /
              v6 (TESOURO)
```

### 2.4.4 Exemplo de Caminho

**Pergunta**: Qual o caminho mais curto de v0 (Entrada) até v6 (Tesouro)?

**Possíveis caminhos**:
1. v0 → v1 → v4 → v6: custo = 3 + 5 + 2 = **10**
2. v0 → v2 → v4 → v6: custo = 4 + 3 + 2 = **9** ✅ MELHOR
3. v0 → v1 → v3 → v6: custo = 3 + 2 + 6 = **11**

**Algoritmo de Dijkstra** encontra automaticamente: v0 → v2 → v4 → v6 (custo 9)

## 2.5 Propriedades do Grafo do Jogo

### 2.5.1 Características Estáticas

- **Tipo**: Não-direcionado, ponderado, conexo
- **Ordem**: |V| = 7 vértices
- **Tamanho**: |E| = 12 arestas
- **Densidade**: 2|E|/(|V|(|V|-1)) = 24/42 ≈ 0.57 (grafo moderadamente denso)
- **Grau médio**: 2|E|/|V| = 24/7 ≈ 3.4 vizinhos por vértice

### 2.5.2 Características Dinâmicas

Durante o jogo, o grafo pode mudar:

**Bloqueio de Arestas**:
- Desabamentos naturais (probabilidade baseada em estabilidade)
- Carta "Desabamento" (jogador bloqueia túnel)
- Colisão durante movimento

**Desbloqueio de Arestas**:
- Carta "Explosivo" (remove bloqueio)
- Usar picareta em obstáculos

**Modificação de Pesos**:
- Carta "Corda" (reduz peso do túnel)
- Passagens descobertas podem ter custo menor

**Remoção de Vértices**:
- Não ocorre neste jogo
- Poderia representar câmaras colapsadas

## 2.6 Por Que Grafos São Perfeitos Para Dungeons?

### 2.6.1 Vantagens

1. **Modelagem Natural**:
   - Câmaras = vértices
   - Túneis = arestas
   - Intuitivo e direto

2. **Algoritmos Prontos**:
   - BFS para exploração
   - Dijkstra para pathfinding
   - A* para IA de monstros

3. **Flexibilidade**:
   - Fácil adicionar/remover conexões
   - Modificar pesos dinamicamente
   - Escalar para dungeons maiores

4. **Performance**:
   - Algoritmos otimizados (O(E log V))
   - Estruturas de dados eficientes
   - Escalável para mapas grandes

### 2.6.2 Alternativas (e por que não usamos)

**Grid Puro** (matriz 2D):
- ❌ Limitado a movimentos ortogonais/diagonais
- ❌ Difícil representar conexões não-adjacentes
- ❌ Desperdiça memória com células vazias
- ✅ Simples de visualizar

**Waypoints** (pontos de navegação):
- ✅ Flexível para ambientes 3D
- ❌ Requer cálculo de visibilidade
- ❌ Mais complexo de implementar

**Grafo** (nossa escolha):
- ✅ Flexível e eficiente
- ✅ Algoritmos bem estabelecidos
- ✅ Fácil de modificar dinamicamente
- ✅ Escalável

---


# 3. ARQUITETURA DO SISTEMA

## 3.1 Visão Geral dos Módulos

O projeto está organizado em camadas bem definidas:

```
┌─────────────────────────────────────┐
│         UI LAYER (PySide6)          │
│   - Renderização visual             │
│   - Entrada do usuário              │
│   - Animações                       │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│      GAME STATE (Orquestrador)      │
│   - Coordena todos sistemas         │
│   - Mantém estado global            │
└────────────────┬────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐  ┌──▼───┐  ┌────▼────┐
│  Graph  │  │Player│  │ Combat  │
│ System  │  │System│  │ System  │
└────┬────┘  └──┬───┘  └────┬────┘
     │          │           │
┌────▼──────────▼───────────▼────┐
│     CORE ALGORITHMS (Grafos)    │
│   - BFS, Dijkstra, A*          │
│   - Pathfinding                 │
└─────────────────────────────────┘
```

## 3.2 Módulos Principais

### core/graph.py (345 linhas)
**Responsabilidade**: Estrutura de grafos

**Classes**:
- `Vertex`: Representa câmaras
- `Edge`: Representa túneis
- `Graph`: Grafo completo do dungeon

### core/algorithms.py (474 linhas)  
**Responsabilidade**: Algoritmos de busca

**Funções**:
- `bfs()`: Busca em largura
- `dijkstra()`: Caminho de custo mínimo
- `a_star()`: Pathfinding com heurística

### core/player.py (353 linhas)
**Responsabilidade**: Sistema de jogador

**Features**:
- Atributos (HP, Stamina, Attack, Defense)
- Inventário
- Sistema de buffs/debuffs
- Progressão (XP, níveis)

### core/combat.py (267 linhas)
**Responsabilidade**: Sistema de combate

**Features**:
- Cálculo de dano
- Turnos de combate
- Críticos e esquivas
- Rewards (XP, ouro, itens)

### core/cards.py (318 linhas)
**Responsabilidade**: Sistema de cartas

**10 Tipos de Cartas**:
- ECO (usa BFS)
- VISÃO (usa Dijkstra)
- TELEPORTE (usa A*)
- E mais 7 tipos...

### core/game_state.py (666 linhas)
**Responsabilidade**: Coordenador central

**Gerencia**:
- Loop principal do jogo
- Todos os sistemas
- Estado global
- Eventos

---

# 4. ALGORITMOS DE GRAFOS IMPLEMENTADOS

## 4.1 BFS (Busca em Largura)

### 4.1.1 Conceito

**BFS** explora o grafo **nível por nível**, visitando todos vizinhos antes de avançar.

### 4.1.2 Pseudocódigo

```
BFS(grafo, início):
    criar fila vazia
    adicionar início à fila
    marcar início como visitado
    
    enquanto fila não vazia:
        remover vértice v da fila
        
        para cada vizinho w de v:
            se w não foi visitado:
                marcar w como visitado
                adicionar w à fila
                distância[w] = distância[v] + 1
```

### 4.1.3 Implementação Real no Projeto

```python
def bfs(graph: Graph, start_vertex_id: int, max_depth: Optional[int] = None):
    """
    Busca em Largura - retorna distâncias em número de arestas
    
    Complexidade: O(V + E)
    Espaço: O(V)
    """
    if start_vertex_id not in graph.vertices:
        return {}
    
    distances = {start_vertex_id: 0}
    queue = [(start_vertex_id, 0)]
    visited = {start_vertex_id}
    
    while queue:
        current_id, current_dist = queue.pop(0)
        
        # Limite de profundidade (otimização)
        if max_depth is not None and current_dist >= max_depth:
            continue
        
        # Explorar todos vizinhos
        for neighbor_id, edge in graph.neighbors(current_id):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                new_dist = current_dist + 1
                distances[neighbor_id] = new_dist
                queue.append((neighbor_id, new_dist))
    
    return distances
```

### 4.1.4 Aplicações no Jogo

**1. Carta ECO** - Revela Área Próxima

```python
# Jogador usa carta ECO nível 2
max_range = 3 + card.level  # 3 + 2 = 5 níveis
distances = bfs(graph, player.current_vertex_id, max_depth=max_range)

# Revela todas câmaras até 5 arestas de distância
for vertex_id in distances.keys():
    vertex = graph.vertices[vertex_id]
    vertex.explored = True  # Marcar como explorado
    if vertex.has_monster:
        show_warning(f"Monstro detectado em {vertex.name}!")
```

**2. Sistema de Alcance** - Área de Efeito

```python
# Calcular alcance de habilidade de área
def get_area_of_effect(center, radius):
    positions = bfs(graph, center, max_depth=radius)
    return list(positions.keys())

# Usar em spell de área
affected_chambers = get_area_of_effect(player_pos, spell_range=2)
for chamber in affected_chambers:
    apply_damage_to_monsters_in(chamber)
```

**3. IA Simples de Monstros**

```python
# Monstro detecta jogador próximo
distances = bfs(graph, monster.position, max_depth=5)
if player.position in distances:
    distance = distances[player.position]
    if distance <= 2:
        monster.aggro = True  # Entrar em modo ataque
```

### 4.1.5 Visualização Passo a Passo

```
Grafo:     v0 --- v1 --- v3
            |      |
           v2 --- v4

BFS a partir de v0:

Passo 1: Iniciar em v0
  Fila: []
  Visitados: {v0}
  Distâncias: {v0: 0}

Passo 2: Processar v0, adicionar vizinhos
  Fila: [(v1,1), (v2,1)]
  Visitados: {v0, v1, v2}
  Distâncias: {v0:0, v1:1, v2:1}

Passo 3: Processar v1, adicionar vizinhos
  Fila: [(v2,1), (v3,2), (v4,2)]
  Visitados: {v0, v1, v2, v3, v4}
  Distâncias: {v0:0, v1:1, v2:1, v3:2, v4:2}

Passo 4: Processar v2
  Fila: [(v3,2), (v4,2)]
  (v4 já visitado, não adiciona)

Resultado Final:
  v0: 0 arestas
  v1: 1 aresta
  v2: 1 aresta
  v3: 2 arestas
  v4: 2 arestas
```

### 4.1.6 Complexidade

- **Tempo**: O(V + E)
  - Visita cada vértice uma vez: O(V)
  - Examina cada aresta uma vez: O(E)
  - Total: O(V + E)

- **Espaço**: O(V)
  - Fila: no máximo V elementos
  - Set de visitados: V elementos
  - Dicionário de distâncias: V elementos

**No nosso jogo** (V=7, E=12):
- Tempo: O(7 + 12) = O(19) ≈ constante
- Muito eficiente!

---

## 4.2 Algoritmo de Dijkstra

### 4.2.1 Conceito

**Dijkstra** encontra o **caminho de custo mínimo** considerando os **pesos das arestas**.

**Diferença do BFS**:
- BFS: conta número de arestas (todos pesos = 1)
- Dijkstra: soma pesos reais das arestas

### 4.2.2 Pseudocódigo

```
Dijkstra(grafo, início):
    para cada vértice v:
        distância[v] = infinito
        anterior[v] = null
    
    distância[início] = 0
    criar fila de prioridade Q
    adicionar (0, início) a Q
    
    enquanto Q não vazia:
        (dist, u) = remover mínimo de Q
        
        para cada vizinho v de u:
            alt = distância[u] + peso(u, v)
            se alt < distância[v]:
                distância[v] = alt
                anterior[v] = u
                adicionar (alt, v) a Q
    
    retornar distância, anterior
```

### 4.2.3 Implementação Real

```python
import heapq

def dijkstra(graph: Graph, start_vertex_id: int, end_vertex_id: Optional[int] = None):
    """
    Algoritmo de Dijkstra - caminho de custo mínimo
    
    Args:
        graph: Grafo a explorar
        start_vertex_id: Vértice inicial
        end_vertex_id: Vértice destino (opcional, para terminação antecipada)
    
    Returns:
        (distances, predecessors)
        - distances: dict mapeando vertex_id -> custo mínimo
        - predecessors: dict mapeando vertex_id -> vértice anterior no caminho
    
    Complexidade: O((V + E) log V) com heap binário
    """
    if start_vertex_id not in graph.vertices:
        return {}, {}
    
    # Inicializar distâncias
    distances = {v_id: float('inf') for v_id in graph.vertices}
    distances[start_vertex_id] = 0
    predecessors = {}
    
    # Fila de prioridade (min-heap): (distância, vertex_id)
    pq = [(0, start_vertex_id)]
    visited = set()
    
    while pq:
        current_dist, current_id = heapq.heappop(pq)
        
        # Pular se já visitou (pode ter duplicatas no heap)
        if current_id in visited:
            continue
        
        visited.add(current_id)
        
        # Terminação antecipada se alcançou destino
        if end_vertex_id is not None and current_id == end_vertex_id:
            break
        
        # Pular se encontrou caminho melhor
        if current_dist > distances[current_id]:
            continue
        
        # Explorar vizinhos
        for neighbor_id, edge in graph.neighbors(current_id):
            # Calcular novo custo
            new_dist = current_dist + edge.weight
            
            # Se encontrou caminho melhor
            if new_dist < distances[neighbor_id]:
                distances[neighbor_id] = new_dist
                predecessors[neighbor_id] = current_id
                heapq.heappush(pq, (new_dist, neighbor_id))
    
    return distances, predecessors
```

### 4.2.4 Reconstruir Caminho

```python
def reconstruct_path(predecessors, start_id, end_id):
    """
    Reconstrói caminho usando predecessores
    """
    if end_id not in predecessors and end_id != start_id:
        return []  # Sem caminho
    
    path = []
    current = end_id
    
    # Voltar do fim ao início
    while current != start_id:
        path.append(current)
        if current not in predecessors:
            return []  # Caminho inválido
        current = predecessors[current]
    
    path.append(start_id)
    path.reverse()
    return path
```

### 4.2.5 Aplicações no Jogo

**1. Carta VISÃO** - Mostra Caminho até Tesouro

```python
def apply_vision_card(player, game_state):
    treasure_id = game_state.treasure_vertex_id
    
    # Calcular melhor caminho
    distances, predecessors = dijkstra(
        game_state.graph, 
        player.current_vertex_id, 
        treasure_id
    )
    
    # Reconstruir caminho
    path = reconstruct_path(predecessors, player.current_vertex_id, treasure_id)
    total_cost = distances[treasure_id]
    
    treasure_name = game_state.graph.vertices[treasure_id].name
    
    # Mostrar informação
    message = f"🔮 VISÃO REVELADA!\n"
    message += f"Tesouro está em: {treasure_name}\n"
    message += f"Distância: {total_cost} de custo\n"
    message += f"Caminho: {' → '.join([game_state.graph.vertices[v].name for v in path])}"
    
    return message
```

**2. Sistema de Navegação** - Sugestão de Rota

```python
def suggest_best_route(player, target):
    # Calcular caminho ótimo
    distances, predecessors = dijkstra(graph, player.position, target)
    path = reconstruct_path(predecessors, player.position, target)
    
    # Destacar no mapa
    for vertex_id in path:
        highlight_chamber(vertex_id, color="gold")
    
    return path, distances[target]
```

**3. Comparar Múltiplos Destinos**

```python
# Jogador quer ir ao baú mais próximo
chests = [v_id for v_id, v in graph.vertices.items() if v.has_treasure_chest]

best_chest = None
best_cost = float('inf')

for chest_id in chests:
    distances, _ = dijkstra(graph, player.position, chest_id)
    cost = distances[chest_id]
    
    if cost < best_cost:
        best_cost = cost
        best_chest = chest_id

print(f"Baú mais próximo: {graph.vertices[best_chest].name} (custo: {best_cost})")
```

### 4.2.6 Exemplo Visual Completo

```
Grafo com pesos:

     v0
    / \
  [3] [4]
  /     \
 v1     v2
  |  X  /
 [2]  [3]
  |  /
  v3

Executar Dijkstra de v0 para v3:

INICIALIZAÇÃO:
  dist = {v0:0, v1:∞, v2:∞, v3:∞}
  pred = {}
  PQ = [(0, v0)]

ITERAÇÃO 1: Processar v0 (dist=0)
  Vizinhos: v1 (peso 3), v2 (peso 4)
  - v1: 0+3=3 < ∞ → dist[v1]=3, pred[v1]=v0
  - v2: 0+4=4 < ∞ → dist[v2]=4, pred[v2]=v0
  PQ = [(3,v1), (4,v2)]

ITERAÇÃO 2: Processar v1 (dist=3)
  Vizinhos: v3 (peso 2)
  - v3: 3+2=5 < ∞ → dist[v3]=5, pred[v3]=v1
  PQ = [(4,v2), (5,v3)]

ITERAÇÃO 3: Processar v2 (dist=4)
  Vizinhos: v3 (peso 3)
  - v3: 4+3=7 > 5 → NÃO atualiza
  PQ = [(5,v3)]

ITERAÇÃO 4: Processar v3 (dist=5)
  Destino alcançado! PARAR

RESULTADO:
  Caminho: v0 → v1 → v3
  Custo total: 5
  Predecessores: {v1:v0, v2:v0, v3:v1}
```

### 4.2.7 Otimizações Implementadas

**1. Terminação Antecipada**
```python
if end_vertex_id is not None and current_id == end_vertex_id:
    break  # Parar quando alcançar destino
```

**2. Evitar Duplicatas**
```python
if current_id in visited:
    continue  # Pular vértices já processados
```

**3. Heap Binário** 
```python
import heapq
# O(log V) para inserção/remoção
# Muito mais rápido que lista ordenada: O(V)
```

### 4.2.8 Complexidade

- **Tempo**: O((V + E) log V)
  - Para cada vértice (V vezes):
    - Remover do heap: O(log V)
  - Para cada aresta (E vezes):
    - Inserir no heap: O(log V)
  - Total: V log V + E log V = (V + E) log V

- **Espaço**: O(V)
  - Heap: no máximo V elementos
  - Dicionários: V entradas cada

**No nosso jogo** (V=7, E=12):
- Tempo: O(19 log 7) ≈ O(53) operações
- Ainda muito eficiente!

---

## 4.3 Algoritmo A* (A-Star)

### 4.3.1 Conceito

**A*** é Dijkstra com **heurística** - usa estimativa de distância ao objetivo para guiar a busca.

**Função de Custo**:
- **g(n)**: Custo real do início até n
- **h(n)**: Estimativa heurística de n até objetivo
- **f(n) = g(n) + h(n)**: Prioridade total

### 4.3.2 Heurística: Distância Euclidiana

```python
def heuristic_distance(graph, v1_id, v2_id):
    """
    Distância em linha reta (euclidiana) entre dois vértices
    
    Esta é uma heurística ADMISSÍVEL:
    - Nunca superestima o custo real
    - Garante solução ótima
    """
    v1 = graph.vertices[v1_id]
    v2 = graph.vertices[v2_id]
    
    dx = v1.x - v2.x
    dy = v1.y - v2.y
    return (dx * dx + dy * dy) ** 0.5
```

### 4.3.3 Implementação Completa

```python
def a_star(graph, start_vertex_id, goal_vertex_id):
    """
    Algoritmo A* - pathfinding com heurística
    
    Returns:
        (path, cost) - caminho e custo total
    
    Complexidade: O(E log V) em média (com boa heurística)
    """
    if start_vertex_id not in graph.vertices or goal_vertex_id not in graph.vertices:
        return [], float('inf')
    
    # Fila de prioridade: (f_score, vertex_id)
    open_set = [(0, start_vertex_id)]
    came_from = {}
    
    # g_score: custo real do início
    g_score = {v_id: float('inf') for v_id in graph.vertices}
    g_score[start_vertex_id] = 0
    
    # f_score: g + heurística
    f_score = {v_id: float('inf') for v_id in graph.vertices}
    f_score[start_vertex_id] = heuristic_distance(graph, start_vertex_id, goal_vertex_id)
    
    visited = set()
    
    while open_set:
        current_f, current_id = heapq.heappop(open_set)
        
        if current_id in visited:
            continue
        
        # Chegou ao objetivo!
        if current_id == goal_vertex_id:
            # Reconstruir caminho
            path = []
            current = goal_vertex_id
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_vertex_id)
            path.reverse()
            return path, g_score[goal_vertex_id]
        
        visited.add(current_id)
        
        # Explorar vizinhos
        for neighbor_id, edge in graph.neighbors(current_id):
            tentative_g = g_score[current_id] + edge.weight
            
            if tentative_g < g_score[neighbor_id]:
                # Encontrou caminho melhor
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                f = tentative_g + heuristic_distance(graph, neighbor_id, goal_vertex_id)
                f_score[neighbor_id] = f
                heapq.heappush(open_set, (f, neighbor_id))
    
    return [], float('inf')  # Sem caminho
```

### 4.3.4 Comparação: Dijkstra vs A*

| Aspecto | Dijkstra | A* |
|---------|----------|-----|
| Exploração | Expande em todas direções | Direciona para objetivo |
| Vértices visitados | Muitos | Menos (com boa heurística) |
| Velocidade | Mais lento | Mais rápido |
| Otimalidade | Sempre ótimo | Ótimo se heurística admissível |
| Usa heurística | Não | Sim |
| Melhor para | Todos pares | Origem-destino específico |

### 4.3.5 Aplicações no Jogo

**1. IA de Monstros** - Perseguir Jogador

```python
class MonsterAI:
    def decide_movement(self, monster, player, graph):
        # Usar A* para encontrar caminho eficiente
        path, cost = a_star(graph, monster.position, player.position)
        
        if len(path) > 1:
            # Mover para próxima posição no caminho
            next_position = path[1]
            return next_position
        
        return None  # Sem caminho válido
```

**2. Carta TELEPORTE** - Movimento Inteligente

```python
def apply_teleport_card(player, target_id, graph):
    # Verificar se é adjacente
    neighbors = [n[0] for n in graph.neighbors(player.current_vertex_id)]
    
    if target_id not in neighbors:
        return False, "Deve teleportar para câmara adjacente"
    
    # Usar A* para validar (redundante aqui, mas mostra uso)
    path, cost = a_star(graph, player.current_vertex_id, target_id)
    
    # Teleportar
    player.current_vertex_id = target_id
    return True, f"Teleportado para {graph.vertices[target_id].name}!"
```

**3. Sugestão de Rota Otimizada**

```python
def suggest_optimal_route_to_treasure(player, game_state):
    treasure_id = game_state.treasure_vertex_id
    
    # A* é mais eficiente que Dijkstra para objetivo específico
    path, cost = a_star(game_state.graph, player.position, treasure_id)
    
    # Mostrar rota otimizada
    route_description = " → ".join([game_state.graph.vertices[v].name for v in path])
    
    return {
        "path": path,
        "cost": cost,
        "description": route_description,
        "estimated_stamina": cost * 2
    }
```

### 4.3.6 Exemplo Visual: Dijkstra vs A*

```
Grafo:        v0 --- v1 --- v2 --- [TESOURO]
               |      |
              v3 --- v4

Objetivo: v0 → TESOURO

DIJKSTRA:
  Explora TODOS vértices alcançáveis
  Ordem: v0 → v1, v3 → v4, v2 → TESOURO
  Vértices visitados: 6

A* com heurística:
  Foca na direção do tesouro
  Ordem: v0 → v1 → v2 → TESOURO
  Vértices visitados: 4
  
  Pula v3 e v4 porque heurística mostra que 
  estão na direção OPOSTA ao tesouro!
```

### 4.3.7 Propriedades da Heurística

**Admissível**: Nunca superestima o custo real
```
h(n) ≤ custo_real(n, objetivo)

Nossa heurística (distância euclidiana) é admissível porque:
- Distância em linha reta ≤ Distância por caminhos
```

**Consistente**: Satisfaz desigualdade triangular
```
h(n) ≤ custo(n, n') + h(n')

Garante que A* expande cada nó apenas uma vez
```

### 4.3.8 Complexidade

- **Tempo**: O(E log V) em média
  - Com heurística ruim: O((V + E) log V) (igual Dijkstra)
  - Com heurística boa: muito melhor na prática

- **Espaço**: O(V)

**No nosso jogo**:
- Heurística euclidiana funciona bem
- Mapas pequenos (V=7) → diferença mínima
- Em mapas maiores (V>100), A* brilha!

---


# 5. MECÂNICAS DO JOGO - VISÃO COMPLETA

## 5.1 Sistema de Combate

**Fórmula de Dano**:
```python
dano = ataque * (1 - defesa*0.02) * variância
crítico = dano * 2
```

**6 Tipos de Monstros**:
- Goblin: Rápido, pouco HP
- Orc: Forte, defensivo
- Cave Spirit: Evasivo
- Stone Golem: Tanque
- Giant Bat: Ataque surpresa
- Slime: Regenerativo

## 5.2 Sistema de Cartas (10 tipos)

1. **ECO** (usa BFS): Revela câmaras próximas
2. **VISÃO** (usa Dijkstra): Mostra caminho até tesouro
3. **TELEPORTE** (usa A*): Movimento instantâneo
4. **DESABAMENTO**: Bloqueia túnel
5. **EXPLOSIVO**: Desbloqueia túnel
6. **CORDA**: Reduz peso de túnel
7. **CURA**: Restaura HP
8. **ESCUDO**: Aumenta defesa
9. **REFORÇO**: Fortalece túnel
10. **ARMADILHA**: Coloca armadilha

---

# 6. FLUXO DE GAMEPLAY DETALHADO

## 6.1 Inicialização

```
1. Criar Grafo (7 vértices, 12 arestas)
2. Converter para Grid 25×25
3. Posicionar Jogadores (v0 e v1)
4. Spawnar 4 Monstros
5. Colocar Tesouro (v6)
6. Distribuir 3 cartas iniciais
```

## 6.2 Loop Principal

```
ENQUANTO jogo ativo:
  1. Atualizar (60 FPS)
     - Regenerar stamina
     - Processar combates
     - Atualizar animações
  
  2. Processar Input
     - WASD / Setas: Movimento
     - Espaço: Interagir
     - 1-5: Usar carta
  
  3. Validar Movimento
     - Verificar stamina
     - Verificar túnel aberto
     - Usar algoritmos (BFS/Dijkstra/A*)
  
  4. Executar Ação
     - Mover no grafo
     - Animar no grid
     - Processar eventos
  
  5. Verificar Vitória
     - Player na posição do tesouro?
```

---

# 7. EXEMPLOS PRÁTICOS

## 7.1 Exemplo Completo de Partida

```
TURNO 1 - Jogador Vermelho:
  Posição: v0 (Entrada)
  Ação: Mover para v1
  Algoritmo: BFS calcula vizinhos
  Custo: 3 stamina
  Evento: Encontrou 10 ouro

TURNO 2 - Jogador Azul:
  Posição: v1
  Ação: Usar carta ECO (nível 1)
  Algoritmo: BFS(v1, max_depth=3)
  Resultado: Revelou v0, v2, v3, v4
  Info: Detectou Goblin em v4!

TURNO 3 - Jogador Vermelho:
  Posição: v1
  Ação: Mover para v4
  Algoritmo: Dijkstra(v1, v4)
  Custo: 5 stamina
  Evento: COMBATE com Goblin!
  
COMBATE:
  T1: Vermelho ataca → 18 dano
  T2: Goblin ataca → 8 dano
  T3: Vermelho CRÍTICO → 32 dano
  Resultado: Vitória! +15 XP, +12 ouro

TURNO 4 - Jogador Vermelho:
  Posição: v4
  Ação: Usar carta VISÃO
  Algoritmo: Dijkstra(v4, v6)
  Resultado: "Tesouro em v6, custo 2"
  
TURNO 5 - Jogador Vermelho:
  Ação: Mover para v6
  Algoritmo: A*(v4, v6)
  Custo: 2 stamina
  Resultado: VITÓRIA! Encontrou o tesouro!
```

## 7.2 Comparação de Algoritmos no Jogo

| Situação | BFS | Dijkstra | A* |
|----------|-----|----------|-----|
| Revelar área | ✅ Perfeito | ❌ Excessivo | ❌ Excessivo |
| Caminho até tesouro | ❌ Ignora pesos | ✅ Ótimo | ✅ Mais rápido |
| IA de monstro | ✅ Simples | ✅ Bom | ✅ Melhor |
| Detectar alcance | ✅ Perfeito | ❌ Excessivo | ❌ Excessivo |

---

# 8. CONCLUSÃO

## 8.1 O Que Aprendemos

Este projeto demonstra que **algoritmos de grafos** são ferramentas poderosas e práticas:

1. **BFS**: Exploração em largura, perfeito para área de efeito
2. **Dijkstra**: Caminho de custo mínimo, ideal para navegação
3. **A***: Pathfinding inteligente, ótimo para IA

## 8.2 Aplicações Reais

Os mesmos algoritmos usados neste jogo são aplicados em:

- **Google Maps**: Dijkstra/A* para rotas
- **Redes Sociais**: BFS para "pessoas que você pode conhecer"
- **Jogos AAA**: A* para IA de NPCs
- **Inteligência Artificial**: Grafos de conhecimento

## 8.3 Estatísticas do Projeto

- **Linhas de Código**: ~5,800
- **Módulos Core**: 13 arquivos
- **Módulos UI**: 11 arquivos
- **Algoritmos**: BFS, Dijkstra, A*, DFS
- **Complexidade**: O(E log V) no pior caso
- **Tempo de Desenvolvimento**: Projeto educacional

## 8.4 Próximos Passos

### Para Estender o Projeto:

1. **Mais Algoritmos**:
   - Floyd-Warshall (todos pares)
   - Bellman-Ford (pesos negativos)
   - Prim/Kruskal (árvores geradoras)

2. **Mapas Procedurais**:
   - Gerar grafos aleatórios
   - Garantir conectividade
   - Balanceamento automático

3. **Multiplayer Online**:
   - Sincronizar estados
   - Resolver conflitos
   - Latência e predição

4. **IA Avançada**:
   - Aprendizado por reforço
   - Árvores de comportamento
   - Redes neurais para decisões

## 8.5 Recursos de Estudo

### Livros:
- "Introduction to Algorithms" - Cormen et al.
- "Algorithms" - Sedgewick & Wayne
- "Programming Game AI by Example" - Mat Buckland

### Sites:
- [VisuAlgo](https://visualgo.net) - Visualização de algoritmos
- [GeeksforGeeks](https://geeksforgeeks.org/graph-data-structure-and-algorithms/) - Tutoriais
- [Red Blob Games](https://redblobgames.com) - Pathfinding interativo

### Vídeos:
- MIT OpenCourseWare - Algoritmos
- William Fiset - Algoritmos de Grafos
- Sebastian Lague - Pathfinding

---

# 9. APÊNDICES

## 9.1 Glossário Técnico

- **Grafo**: Estrutura de vértices e arestas
- **Vértice**: Nó do grafo
- **Aresta**: Conexão entre vértices
- **Peso**: Custo de uma aresta
- **Caminho**: Sequência de vértices conectados
- **Ciclo**: Caminho que volta ao início
- **Grafo Conexo**: Todos vértices alcançáveis
- **Grau**: Número de arestas de um vértice
- **Heurística**: Estimativa que guia busca
- **Fila de Prioridade**: Estrutura com mínimo/máximo eficiente

## 9.2 Complexidades Resumidas

| Algoritmo | Tempo | Espaço |
|-----------|-------|--------|
| BFS | O(V + E) | O(V) |
| DFS | O(V + E) | O(V) |
| Dijkstra | O((V+E) log V) | O(V) |
| A* | O(E log V) | O(V) |
| Floyd-Warshall | O(V³) | O(V²) |

## 9.3 Estrutura de Arquivos Completa

```
caca_tesouro_desktop/
├── core/
│   ├── algorithms.py      (474 linhas)
│   ├── cards.py          (318 linhas)
│   ├── combat.py         (267 linhas)
│   ├── events.py         (303 linhas)
│   ├── game_state.py     (666 linhas)
│   ├── graph.py          (345 linhas)
│   ├── grid_map.py       (188 linhas)
│   ├── obstacles.py      (392 linhas)
│   ├── player.py         (353 linhas)
│   └── resources.py      (298 linhas)
├── ui/
│   ├── main_qt.py
│   ├── main_window.py
│   ├── grid_board_view.py
│   └── [8 outros arquivos UI]
├── docs/
│   └── DOCUMENTACAO_COMPLETA.md  (este arquivo!)
└── README.md
```

---

# PALAVRAS FINAIS

Este projeto demonstra que **teoria e prática andam juntas**.

Cada algoritmo estudado na sala de aula tem aplicação real. Cada estrutura de dados resolve problemas concretos. Cada linha de código ensina algo novo.

**Grafos estão em toda parte** - desde o mapa no seu celular até as recomendações de amigos nas redes sociais. Dominar algoritmos de grafos abre portas para resolver problemas complexos de forma elegante e eficiente.

Este jogo é apenas o começo. Use este conhecimento para criar projetos ainda mais incríveis!

---

**Fim da Documentação**

**Versão**: 1.0  
**Data**: Dezembro 2024  
**Autor**: Projeto Educacional Caça ao Tesouro  
**Tecnologias**: Python 3.8+, PySide6  
**Algoritmos**: BFS, Dijkstra, A*, e mais  

---

© 2024 - Projeto Educacional de Algoritmos de Grafos
