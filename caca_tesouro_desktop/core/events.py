"""
Random Events System
Positive, negative, and neutral events that can occur during gameplay
"""
import random
from enum import Enum
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .game_state import GameState
    from .player import Player

class EventType(Enum):
    """Types of random events"""
    # Positive events
    FIND_GOLD = "find_gold"
    MYSTERIOUS_HEALING = "mysterious_healing"
    FIND_CARD = "find_card"
    TUNNEL_REINFORCEMENT = "tunnel_reinforcement"
    LUCKY_FIND = "lucky_find"
    DIVINE_BLESSING = "divine_blessing"
    
    # Negative events
    TUNNEL_COLLAPSE = "tunnel_collapse"
    TOXIC_GAS = "toxic_gas"
    AMBUSH = "ambush"
    RESOURCE_THEFT = "resource_theft"
    CURSE = "curse"
    EARTHQUAKE = "earthquake"
    
    # Neutral events
    STRANGE_ECHO = "strange_echo"
    DISTANT_ROAR = "distant_roar"
    MYSTERIOUS_LIGHT = "mysterious_light"
    ANCIENT_INSCRIPTION = "ancient_inscription"

class RandomEvent:
    """Represents a random event"""
    def __init__(self, event_type: EventType, probability: float = 0.1):
        self.event_type = event_type
        self.probability = probability
        self.description = ""
        self.is_positive = self._determine_polarity()
    
    def _determine_polarity(self) -> bool:
        """Determine if event is positive"""
        positive_events = {
            EventType.FIND_GOLD, EventType.MYSTERIOUS_HEALING,
            EventType.FIND_CARD, EventType.TUNNEL_REINFORCEMENT,
            EventType.LUCKY_FIND, EventType.DIVINE_BLESSING
        }
        return self.event_type in positive_events
    
    def trigger(self, player: 'Player', game_state: 'GameState') -> Tuple[bool, str]:
        """
        Trigger the event
        Returns (occurred, message)
        """
        # Check probability
        if random.random() > self.probability:
            return False, ""
        
        message = ""
        
        # ===== POSITIVE EVENTS =====
        
        if self.event_type == EventType.FIND_GOLD:
            amount = random.randint(20, 50)
            player.add_gold(amount)
            message = f"✨ Você encontrou {amount} ouro escondido nas rochas!"
        
        elif self.event_type == EventType.MYSTERIOUS_HEALING:
            heal_amount = random.randint(20, 40)
            healed = player.heal(heal_amount)
            message = f"💚 Uma energia misteriosa cura suas feridas! (+{healed} HP)"
        
        elif self.event_type == EventType.FIND_CARD:
            from .cards import Card, CardType
            card_types = list(CardType)
            card_type = random.choice(card_types)
            card = Card(game_state._next_card_id, card_type, random.randint(1, 3))
            game_state._next_card_id += 1
            
            if len(player.hand_cards) < player.max_hand_size:
                player.hand_cards.append(card)
                message = f"🃏 Você encontrou uma carta: {card.type.value}!"
            else:
                message = f"🃏 Você encontrou uma carta mas sua mão está cheia!"
        
        elif self.event_type == EventType.TUNNEL_REINFORCEMENT:
            # Reinforce a random tunnel connected to player
            edges = game_state.graph.get_edges_from_vertex(player.current_vertex_id)
            if edges:
                edge = random.choice(edges)
                edge.reinforce()
                message = f"🔨 Um dos túneis próximos foi misteriosamente reforçado!"
            else:
                return False, ""
        
        elif self.event_type == EventType.LUCKY_FIND:
            items = ["health_potion", "stamina_potion", "key", "rope", "gem"]
            item = random.choice(items)
            quantity = random.randint(1, 2)
            player.add_item(item, quantity)
            message = f"🍀 Sorte! Você encontrou {quantity}x {item}!"
        
        elif self.event_type == EventType.DIVINE_BLESSING:
            from .player import Buff, BuffType
            buff_types = [BuffType.ATTACK_BOOST, BuffType.DEFENSE_BOOST, 
                         BuffType.REGENERATION]
            buff_type = random.choice(buff_types)
            buff = Buff(buff_type, 5, 5, "Bênção Divina")
            player.add_buff(buff)
            message = f"✨ Bênção Divina! {buff_type.value} por 5 turnos!"
        
        # ===== NEGATIVE EVENTS =====
        
        elif self.event_type == EventType.TUNNEL_COLLAPSE:
            # Collapse a random tunnel
            edges = [e for e in game_state.graph.edges.values() if not e.blocked]
            if edges:
                edge = random.choice(edges)
                edge.blocked = True
                message = f"💥 DESABAMENTO! Um túnel colapsou (Túnel {edge.id})"
            else:
                return False, ""
        
        elif self.event_type == EventType.TOXIC_GAS:
            damage = random.randint(10, 25)
            actual_damage = player.take_damage(damage)
            
            from .player import Buff, BuffType
            poison = Buff(BuffType.POISON, 5, 3, "Gás Tóxico")
            player.add_buff(poison)
            
            message = f"☠️ Gás tóxico! Você perdeu {actual_damage} HP e está envenenado!"
        
        elif self.event_type == EventType.AMBUSH:
            # Spawn a monster at current location
            from .obstacles import Monster, MonsterType
            monster_types = list(MonsterType)
            monster_type = random.choice(monster_types)
            monster = Monster(monster_type, player.level)
            
            # Trigger combat
            from .combat import CombatSystem
            result = CombatSystem.execute_combat(player, monster)
            
            message = f"⚠️ EMBOSCADA! {monster}\n"
            message += CombatSystem.get_combat_summary(result)
        
        elif self.event_type == EventType.RESOURCE_THEFT:
            # Lose random resources
            stolen_gold = min(player.gold, random.randint(10, 30))
            player.gold -= stolen_gold
            
            message = f"🦹 Ladrão! Você perdeu {stolen_gold} ouro"
            
            # Maybe lose an item too
            if player.inventory and random.random() < 0.5:
                item = random.choice(list(player.inventory.keys()))
                player.remove_item(item, 1)
                message += f" e 1x {item}"
            
            message += "!"
        
        elif self.event_type == EventType.CURSE:
            from .player import Buff, BuffType
            curse_types = [BuffType.WEAKNESS, BuffType.SLOW, BuffType.POISON]
            curse_type = random.choice(curse_types)
            curse = Buff(curse_type, 3, 4, "Maldição")
            player.add_buff(curse)
            message = f"😈 MALDIÇÃO! {curse_type.value} por 4 turnos!"
        
        elif self.event_type == EventType.EARTHQUAKE:
            # Damage multiple tunnels
            edges = list(game_state.graph.edges.values())
            num_damaged = random.randint(2, 5)
            damaged_edges = random.sample(edges, min(num_damaged, len(edges)))
            
            collapsed = 0
            for edge in damaged_edges:
                edge.damage_stability(30)
                if edge.attempt_collapse():
                    collapsed += 1
            
            message = f"🌋 TERREMOTO! {collapsed} túneis colapsaram!"
        
        # ===== NEUTRAL EVENTS =====
        
        elif self.event_type == EventType.STRANGE_ECHO:
            # Reveal nearby vertices
            from .algorithms import bfs
            distances = bfs(game_state.graph, player.current_vertex_id, max_depth=2)
            message = f"📡 Eco estranho revela {len(distances)} áreas próximas"
        
        elif self.event_type == EventType.DISTANT_ROAR:
            # Hint about nearby monsters
            nearby_monsters = []
            for v_id, vertex in game_state.graph.vertices.items():
                if vertex.has_monster and v_id != player.current_vertex_id:
                    from .algorithms import dijkstra
                    distances, _ = dijkstra(game_state.graph, player.current_vertex_id, v_id)
                    if distances.get(v_id, float('inf')) <= 3:
                        nearby_monsters.append(vertex.name)
            
            if nearby_monsters:
                message = f"🦁 Você ouve rugidos distantes... Monstros próximos em: {', '.join(nearby_monsters[:3])}"
            else:
                message = f"🦁 Você ouve rugidos distantes, mas não consegue localizar a origem"
        
        elif self.event_type == EventType.MYSTERIOUS_LIGHT:
            # Reveal treasure direction
            from .algorithms import dijkstra
            distances, predecessors = dijkstra(game_state.graph, player.current_vertex_id, 
                                              game_state.treasure_vertex_id)
            
            if game_state.treasure_vertex_id in predecessors:
                next_vertex = game_state.treasure_vertex_id
                current = game_state.treasure_vertex_id
                while predecessors.get(current) != player.current_vertex_id:
                    current = predecessors[current]
                    if current == player.current_vertex_id:
                        break
                    next_vertex = current
                
                vertex_name = game_state.graph.vertices[next_vertex].name
                message = f"💡 Uma luz misteriosa aponta para: {vertex_name}"
            else:
                message = f"💡 Uma luz misteriosa brilha, mas você não entende seu significado"
        
        elif self.event_type == EventType.ANCIENT_INSCRIPTION:
            # Random hint or lore
            hints = [
                "📜 'Os corajosos serão recompensados'",
                "📜 'Cuidado com as sombras'",
                "📜 'O tesouro aguarda os dignos'",
                "📜 'Nem tudo que brilha é ouro'",
                "📜 'A escuridão esconde segredos'",
                "📜 'Confie em sua intuição'",
                "📜 'O caminho mais curto nem sempre é o melhor'"
            ]
            message = random.choice(hints)
        
        else:
            return False, ""
        
        self.description = message
        return True, message

class EventManager:
    """Manages random events in the game"""
    
    def __init__(self):
        self.events = self._create_events()
    
    def _create_events(self) -> list:
        """Create all possible events with probabilities"""
        return [
            # Positive (lower probability)
            RandomEvent(EventType.FIND_GOLD, 0.15),
            RandomEvent(EventType.MYSTERIOUS_HEALING, 0.08),
            RandomEvent(EventType.FIND_CARD, 0.10),
            RandomEvent(EventType.TUNNEL_REINFORCEMENT, 0.05),
            RandomEvent(EventType.LUCKY_FIND, 0.12),
            RandomEvent(EventType.DIVINE_BLESSING, 0.03),
            
            # Negative (moderate probability)
            RandomEvent(EventType.TUNNEL_COLLAPSE, 0.10),
            RandomEvent(EventType.TOXIC_GAS, 0.08),
            RandomEvent(EventType.AMBUSH, 0.12),
            RandomEvent(EventType.RESOURCE_THEFT, 0.07),
            RandomEvent(EventType.CURSE, 0.05),
            RandomEvent(EventType.EARTHQUAKE, 0.03),
            
            # Neutral (higher probability)
            RandomEvent(EventType.STRANGE_ECHO, 0.15),
            RandomEvent(EventType.DISTANT_ROAR, 0.12),
            RandomEvent(EventType.MYSTERIOUS_LIGHT, 0.10),
            RandomEvent(EventType.ANCIENT_INSCRIPTION, 0.20)
        ]
    
    def trigger_random_event(self, player: 'Player', game_state: 'GameState') -> Tuple[bool, str]:
        """
        Attempt to trigger a random event
        Returns (occurred, message)
        """
        # Shuffle events to randomize which one might trigger
        events = self.events.copy()
        random.shuffle(events)
        
        for event in events:
            occurred, message = event.trigger(player, game_state)
            if occurred:
                return True, message
        
        return False, ""
    
    def trigger_specific_event(self, event_type: EventType, player: 'Player', 
                              game_state: 'GameState') -> Tuple[bool, str]:
        """Trigger a specific event type"""
        event = RandomEvent(event_type, 1.0)  # 100% probability
        return event.trigger(player, game_state)
