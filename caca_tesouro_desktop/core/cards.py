"""
Complete Card System with Validation, Effects, and Evolution
"""
import random
from enum import Enum
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState
    from .player import Player

class CardType(Enum):
    """Types of cards available in the game"""
    DESABAMENTO = "desabamento"  # Collapse - blocks a tunnel
    CORDA = "corda"  # Rope - reduces passage weight or bypasses obstacles
    ECO = "eco"  # Echo - reveals routes and nearby enemies
    EXPLOSIVO = "explosivo"  # Explosive - destroys walls and unblocks tunnels
    CURA = "cura"  # Heal - restores HP
    TELEPORTE = "teleporte"  # Teleport - move to adjacent vertex instantly
    ESCUDO = "escudo"  # Shield - temporary defense boost
    VISAO = "visao"  # Vision - reveals treasure location
    REFORCO = "reforco"  # Reinforcement - strengthens a tunnel
    ARMADILHA = "armadilha"  # Trap - sets a trap for other players

class CardRarity(Enum):
    """Card rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"

class Card:
    """
    Represents a card with effects, costs, and validation
    """
    def __init__(self, id: int, card_type: CardType, value: int = 0, level: int = 1):
        self.id = id
        self.type = card_type
        self.value = value  # Magnitude of effect
        self.level = level  # Card evolution level (1-3)
        
        # Costs
        self.action_point_cost = self._calculate_ap_cost()
        self.stamina_cost = self._calculate_stamina_cost()
        self.gold_cost = 0  # Some cards may cost gold to use
        
        # Failure chance
        self.failure_chance = self._calculate_failure_chance()
        
        # Rarity
        self.rarity = self._determine_rarity()
        
        # Description
        self.description = self._generate_description()
    
    def _calculate_ap_cost(self) -> int:
        """Calculate action point cost based on card type and level"""
        base_costs = {
            CardType.DESABAMENTO: 1,
            CardType.CORDA: 1,
            CardType.ECO: 1,
            CardType.EXPLOSIVO: 2,
            CardType.CURA: 1,
            CardType.TELEPORTE: 2,
            CardType.ESCUDO: 1,
            CardType.VISAO: 1,
            CardType.REFORCO: 1,
            CardType.ARMADILHA: 2
        }
        base = base_costs.get(self.type, 1)
        return max(0, base - (self.level - 1))  # Higher level = lower cost
    
    def _calculate_stamina_cost(self) -> int:
        """Calculate stamina cost"""
        base_costs = {
            CardType.DESABAMENTO: 10,
            CardType.CORDA: 5,
            CardType.ECO: 15,
            CardType.EXPLOSIVO: 20,
            CardType.CURA: 10,
            CardType.TELEPORTE: 25,
            CardType.ESCUDO: 10,
            CardType.VISAO: 20,
            CardType.REFORCO: 15,
            CardType.ARMADILHA: 15
        }
        return base_costs.get(self.type, 10)
    
    def _calculate_failure_chance(self) -> float:
        """Calculate chance of card failing"""
        base_chances = {
            CardType.DESABAMENTO: 0.05,
            CardType.CORDA: 0.0,
            CardType.ECO: 0.0,
            CardType.EXPLOSIVO: 0.15,  # Explosives can fail
            CardType.CURA: 0.0,
            CardType.TELEPORTE: 0.1,
            CardType.ESCUDO: 0.0,
            CardType.VISAO: 0.05,
            CardType.REFORCO: 0.05,
            CardType.ARMADILHA: 0.1
        }
        base = base_chances.get(self.type, 0.0)
        return max(0.0, base - (self.level - 1) * 0.05)  # Higher level = lower failure
    
    def _determine_rarity(self) -> CardRarity:
        """Determine card rarity"""
        if self.type in [CardType.CORDA, CardType.ECO]:
            return CardRarity.COMMON
        elif self.type in [CardType.DESABAMENTO, CardType.CURA, CardType.ESCUDO]:
            return CardRarity.UNCOMMON
        elif self.type in [CardType.EXPLOSIVO, CardType.REFORCO, CardType.ARMADILHA]:
            return CardRarity.RARE
        else:  # TELEPORTE, VISAO
            return CardRarity.EPIC
    
    def _generate_description(self) -> str:
        """Generate card description"""
        descriptions = {
            CardType.DESABAMENTO: f"Bloqueia um túnel (Nível {self.level})",
            CardType.CORDA: f"Reduz peso de passagem em {self.value} (Nível {self.level})",
            CardType.ECO: f"Revela rotas e inimigos próximos (Nível {self.level})",
            CardType.EXPLOSIVO: f"Destrói obstáculos e desbloqueia túneis (Nível {self.level})",
            CardType.CURA: f"Restaura {20 + self.value * 10} HP (Nível {self.level})",
            CardType.TELEPORTE: f"Move instantaneamente para vértice adjacente (Nível {self.level})",
            CardType.ESCUDO: f"Aumenta defesa em {5 + self.value * 2} por {2 + self.level} turnos (Nível {self.level})",
            CardType.VISAO: f"Revela localização do tesouro (Nível {self.level})",
            CardType.REFORCO: f"Reforça um túnel contra colapsos (Nível {self.level})",
            CardType.ARMADILHA: f"Coloca armadilha em um vértice (Nível {self.level})"
        }
        return descriptions.get(self.type, "Carta desconhecida")
    
    def can_use(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        """
        Check if player can use this card
        Returns (can_use, reason_if_not)
        """
        # Check action points
        if player.action_points < self.action_point_cost:
            return False, f"Requer {self.action_point_cost} pontos de ação"
        
        # Check stamina
        if player.stamina < self.stamina_cost:
            return False, f"Requer {self.stamina_cost} stamina"
        
        # Check gold
        if player.gold < self.gold_cost:
            return False, f"Requer {self.gold_cost} ouro"
        
        # Card-specific checks
        if self.type == CardType.CURA:
            if player.hp >= player.max_hp:
                return False, "HP já está no máximo"
        
        elif self.type == CardType.TELEPORTE:
            neighbors = game_state.graph.neighbors(player.current_vertex_id)
            if not neighbors:
                return False, "Nenhum vértice adjacente disponível"
        
        return True, ""
    
    def validate_targets(self, player: 'Player', game_state: 'GameState', 
                        target_edge_id: Optional[int] = None,
                        target_vertex_id: Optional[int] = None) -> tuple[bool, str]:
        """
        Validate targets for cards that require them
        Returns (valid, reason_if_not)
        """
        if self.type in [CardType.DESABAMENTO, CardType.CORDA, CardType.EXPLOSIVO, CardType.REFORCO]:
            if target_edge_id is None:
                return False, "Requer um túnel como alvo"
            if target_edge_id not in game_state.graph.edges:
                return False, "Túnel inválido"
            
            edge = game_state.graph.edges[target_edge_id]
            
            # Check if edge is connected to player's current vertex
            if player.current_vertex_id not in (edge.v1_id, edge.v2_id):
                return False, "Túnel deve estar conectado à sua posição atual"
            
            # Specific validations
            if self.type == CardType.DESABAMENTO and edge.blocked:
                return False, "Túnel já está bloqueado"
            
            if self.type == CardType.EXPLOSIVO and not edge.blocked:
                return False, "Túnel não está bloqueado"
        
        elif self.type in [CardType.TELEPORTE, CardType.ARMADILHA]:
            if target_vertex_id is None:
                return False, "Requer um vértice como alvo"
            if target_vertex_id not in game_state.graph.vertices:
                return False, "Vértice inválido"
            
            if self.type == CardType.TELEPORTE:
                # Check if target is adjacent
                neighbors = [n[0] for n in game_state.graph.neighbors(player.current_vertex_id)]
                if target_vertex_id not in neighbors:
                    return False, "Vértice deve ser adjacente"
        
        return True, ""
    
    def apply(self, player: 'Player', game_state: 'GameState',
             target_edge_id: Optional[int] = None,
             target_vertex_id: Optional[int] = None) -> tuple[bool, str]:
        """
        Apply card effect
        Returns (success, message)
        """
        # Check if can use
        can_use, reason = self.can_use(player, game_state)
        if not can_use:
            return False, reason
        
        # Validate targets
        valid, reason = self.validate_targets(player, game_state, target_edge_id, target_vertex_id)
        if not valid:
            return False, reason
        
        # Consume resources
        player.consume_action_points(self.action_point_cost)
        player.consume_stamina(self.stamina_cost)
        player.spend_gold(self.gold_cost)
        
        # Check for failure
        if random.random() < self.failure_chance:
            return False, f"❌ {self.type.value.upper()} falhou!"
        
        # Apply effect
        message = ""
        
        if self.type == CardType.DESABAMENTO:
            edge = game_state.graph.edges[target_edge_id]
            edge.blocked = True
            message = f"💥 Túnel {target_edge_id} bloqueado por desabamento!"
        
        elif self.type == CardType.CORDA:
            edge = game_state.graph.edges[target_edge_id]
            old_weight = edge.weight
            reduction = self.value + self.level
            edge.weight = max(1, edge.weight - reduction)
            message = f"🪢 Peso do túnel {target_edge_id} reduzido de {old_weight} para {edge.weight}"
        
        elif self.type == CardType.ECO:
            from .algorithms import bfs
            distances = bfs(game_state.graph, player.current_vertex_id, max_depth=3 + self.level)
            nearby_monsters = []
            for v_id in distances.keys():
                vertex = game_state.graph.vertices[v_id]
                if vertex.has_monster:
                    nearby_monsters.append((v_id, vertex.name, vertex.monster_type))
            
            message = f"📡 ECO revelou {len(distances)} vértices próximos"
            if nearby_monsters:
                message += f"\n⚠️ Monstros detectados: {', '.join([f'{name} ({mtype})' for _, name, mtype in nearby_monsters])}"
        
        elif self.type == CardType.EXPLOSIVO:
            edge = game_state.graph.edges[target_edge_id]
            edge.blocked = False
            # Chance of damaging player
            if random.random() < 0.2:
                damage = random.randint(5, 15)
                player.take_damage(damage)
                message = f"💣 Túnel {target_edge_id} desbloqueado! Você sofreu {damage} de dano pela explosão"
            else:
                message = f"💣 Túnel {target_edge_id} desbloqueado com sucesso!"
        
        elif self.type == CardType.CURA:
            heal_amount = 20 + self.value * 10 + self.level * 5
            healed = player.heal(heal_amount)
            message = f"💚 Curado {healed} HP"
        
        elif self.type == CardType.TELEPORTE:
            old_vertex = game_state.graph.vertices[player.current_vertex_id].name
            player.current_vertex_id = target_vertex_id
            new_vertex = game_state.graph.vertices[target_vertex_id].name
            message = f"✨ Teleportado de {old_vertex} para {new_vertex}"
        
        elif self.type == CardType.ESCUDO:
            from .player import Buff, BuffType
            duration = 2 + self.level
            magnitude = 5 + self.value * 2
            buff = Buff(BuffType.DEFENSE_BOOST, magnitude, duration, "Escudo mágico")
            player.add_buff(buff)
            message = f"🛡️ Defesa aumentada em {magnitude} por {duration} turnos"
        
        elif self.type == CardType.VISAO:
            treasure_vertex = game_state.graph.vertices[game_state.treasure_vertex_id]
            message = f"👁️ O tesouro está em: {treasure_vertex.name}!"
        
        elif self.type == CardType.REFORCO:
            edge = game_state.graph.edges[target_edge_id]
            edge.reinforce()
            message = f"🔨 Túnel {target_edge_id} reforçado contra colapsos"
        
        elif self.type == CardType.ARMADILHA:
            vertex = game_state.graph.vertices[target_vertex_id]
            # Add trap obstacle (would need obstacles module)
            message = f"🪤 Armadilha colocada em {vertex.name}"
        
        player.cards_played += 1
        return True, message
    
    def evolve(self) -> bool:
        """
        Evolve card to next level (max level 3)
        Returns True if evolved, False if already max level
        """
        if self.level >= 3:
            return False
        
        self.level += 1
        self.action_point_cost = self._calculate_ap_cost()
        self.failure_chance = self._calculate_failure_chance()
        self.description = self._generate_description()
        return True
    
    def __repr__(self):
        return f"Card({self.type.value}, Lv{self.level}, {self.rarity.value})"
