# 🏰 Caça ao Tesouro em Redes de Túneis

Jogo de tabuleiro desktop educacional desenvolvido em Python com PySide6, focado em exploração de dungeons medievais com sistema de grid, combate e coleta de tesouros.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Sobre o Projeto

Jogo de aventura em dungeon com sistema de grid 25x25, onde dois jogadores exploram câmaras medievais, enfrentam monstros, coletam tesouros e utilizam cartas estratégicas para progredir.

### ✨ Características Principais

- 🗺️ **Mapa de Câmaras**: Grid 25x25 com 6 câmaras interconectadas
- 👥 **2 Jogadores**: Controles independentes (WASD e Setas)
- 🎮 **Movimento Suave**: Animações fluidas com QPropertyAnimation
- 👹 **Obstáculos Interativos**: Monstros, portas, baús e armadilhas
- 🎨 **Sprites Animados**: Personagens com animações de idle e caminhada
- ⚔️ **Sistema de Combate**: Batalhas por turnos com monstros
- 🎴 **Sistema de Cartas**: Cartas estratégicas de diferentes níveis
- 🎒 **Inventário**: Gerenciamento de itens e recursos
- 🏆 **Objetivo**: Encontrar o tesouro na câmara final

## 🎮 Controles

### Player Vermelho
- **↑↓←→**: Movimento (Setas)

### Player Azul
- **WASD**: Movimento

### Interação
- Ao encontrar obstáculo, diálogo aparece automaticamente
- Escolha entre: Atacar, Usar Item, Usar Carta, ou Fugir

## 🚀 Como Executar

### Pré-requisitos

```bash
Python 3.8+
PySide6
```

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/caca-tesouro-desktop.git
cd caca-tesouro-desktop
```

2. Instale as dependências:
```bash
pip install PySide6
```

3. Execute o jogo:
```bash
cd caca_tesouro_desktop
python -m ui.main_qt
```

## 🏗️ Estrutura do Projeto

```
caca_tesouro_desktop/
├── core/                      # Lógica do jogo
│   ├── algorithms.py         # Algoritmos de grafo (BFS, DFS, Dijkstra)
│   ├── cards.py              # Sistema de cartas
│   ├── combat.py             # Sistema de combate
│   ├── game_state.py         # Estado global do jogo
│   ├── graph.py              # Estrutura de grafo
│   ├── grid_map.py           # Sistema de grid 25x25
│   ├── obstacle_manager.py   # Gerenciamento de obstáculos
│   └── player.py             # Classe do jogador
├── ui/                        # Interface gráfica
│   ├── board_view.py         # Visualização do tabuleiro (legado)
│   ├── grid_board_view.py    # Visualização em grid
│   ├── frame_animated_sprite.py  # Sprites animados
│   ├── interaction_dialog.py # Diálogo de interação
│   ├── main_window.py        # Janela principal
│   ├── side_panel.py         # Painel lateral
│   └── main_qt.py            # Ponto de entrada
├── assets/                    # Recursos visuais
│   ├── themes/               # Temas e sprites
│   ├── monster.png           # Sprite de monstro
│   ├── door_locked.png       # Sprite de porta
│   ├── chest.png             # Sprite de baú
│   └── ...                   # Texturas de tiles
└── tests/                     # Testes unitários
```

## 🎯 Funcionalidades Implementadas

### ✅ Fase 1: Estrutura do Mapa
- [x] Grid 25x25 tiles
- [x] 6 câmaras conectadas por corredores
- [x] Starts separados para cada jogador
- [x] Sistema de texturas medievais

### ✅ Fase 2: Obstáculos Visuais
- [x] Sprites de monstros, portas e baús
- [x] Sistema ObstacleManager
- [x] Renderização com z-index correto
- [x] 8+ obstáculos distribuídos

### ✅ Fase 3: Sistema de Interação
- [x] Detecção de colisão
- [x] Diálogo de interação (Attack/Item/Card/Flee)
- [x] Ações funcionais (derrota monstros, destranca portas)
- [x] Integração com log do jogo

### 🚧 Em Desenvolvimento
- [ ] Integração completa com sistema de combate
- [ ] Diálogo de seleção de inventário
- [ ] Diálogo de seleção de cartas
- [ ] Sistema de loot para baús
- [ ] Detecção e desarme de armadilhas

## 🗺️ Câmaras do Jogo

1. **Start Vermelho** (5, 5) - Início do jogador vermelho
2. **Start Azul** (5, 19) - Início do jogador azul
3. **Câmara Central** (13, 13) - 2 monstros guardiões
4. **Câmara do Tesouro** (20, 13) - Porta trancada + tesouro final
5. **Câmara de Armadilhas** (20, 5) - 3 armadilhas perigosas
6. **Câmara de Recursos** (20, 19) - Baú com itens úteis

## 🎨 Recursos Visuais

- **Texturas**: Pedra, terra, paredes medievais
- **Sprites**: Personagens animados (8 frames cada)
- **Obstáculos**: Monstros, portas, baús renderizados
- **Animações**: Movimento suave (200ms) com easing

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **PySide6**: Framework de interface gráfica
- **QGraphicsView**: Sistema de renderização 2D
- **QPropertyAnimation**: Animações suaves
- **Enum**: Tipos de tiles e obstáculos
- **Dataclasses**: Estruturas de dados

## 📚 Conceitos Educacionais

O jogo foi desenvolvido com propósitos educacionais, abordando:

- **Grafos**: Representação de túneis como grafo
- **Algoritmos**: BFS, DFS, Dijkstra para pathfinding
- **Estruturas de Dados**: Listas, dicionários, filas
- **Programação Orientada a Objetos**: Classes, herança, encapsulamento
- **Padrões de Design**: Observer, Strategy, State
- **Interface Gráfica**: Qt/PySide6

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fork o projeto
2. Criar uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abrir um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido como projeto educacional de jogo de tabuleiro desktop.

## 🙏 Agradecimentos

- PySide6 pela excelente framework de UI
- Comunidade Python pelo suporte
- Sprites e texturas geradas com IA

---

**Status do Projeto**: 🟢 Em Desenvolvimento Ativo

**Última Atualização**: Novembro 2025
