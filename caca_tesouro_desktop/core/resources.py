"""
Resource Management System
Handles all game resources including gold, gems, keys, tools, potions, and special items
"""
import random
from enum import Enum
from typing import Dict, List, Optional

class ResourceType(Enum):
    """Types of resources in the game"""
    # Currency
    GOLD = "gold"
    GEMS = "gems"
    
    # Keys and access items
    KEY = "key"
    MASTER_KEY = "master_key"
    
    # Tools
    PICKAXE = "pickaxe"
    ROPE = "rope"
    EXPLOSIVES = "explosives"
    TORCH = "torch"
    TRAP_DETECTOR = "trap_detector"
    
    # Potions
    HEALTH_POTION = "health_potion"
    STAMINA_POTION = "stamina_potion"
    STRENGTH_POTION = "strength_potion"
    DEFENSE_POTION = "defense_potion"
    HEAT_RESISTANCE_POTION = "heat_resistance_potion"
    
    # Special items
    RUNE = "rune"
    SLIME_CORE = "slime_core"
    ARMOR_SHARD = "armor_shard"
    GAS_MASK = "gas_mask"
    TREASURE_MAP = "treasure_map"

class Resource:
    """Represents a resource with metadata"""
    def __init__(self, resource_type: ResourceType, quantity: int = 1):
        self.resource_type = resource_type
        self.quantity = quantity
        self.name = self._get_name()
        self.description = self._get_description()
        self.value = self._get_value()  # Gold value
        self.is_consumable = self._is_consumable()
        self.is_stackable = self._is_stackable()
    
    def _get_name(self) -> str:
        """Get display name"""
        names = {
            ResourceType.GOLD: "Ouro",
            ResourceType.GEMS: "Gemas",
            ResourceType.KEY: "Chave",
            ResourceType.MASTER_KEY: "Chave Mestra",
            ResourceType.PICKAXE: "Picareta",
            ResourceType.ROPE: "Corda",
            ResourceType.EXPLOSIVES: "Explosivos",
            ResourceType.TORCH: "Tocha",
            ResourceType.TRAP_DETECTOR: "Detector de Armadilhas",
            ResourceType.HEALTH_POTION: "Poção de Vida",
            ResourceType.STAMINA_POTION: "Poção de Stamina",
            ResourceType.STRENGTH_POTION: "Poção de Força",
            ResourceType.DEFENSE_POTION: "Poção de Defesa",
            ResourceType.HEAT_RESISTANCE_POTION: "Poção de Resistência ao Calor",
            ResourceType.RUNE: "Runa Mágica",
            ResourceType.SLIME_CORE: "Núcleo de Slime",
            ResourceType.ARMOR_SHARD: "Fragmento de Armadura",
            ResourceType.GAS_MASK: "Máscara de Gás",
            ResourceType.TREASURE_MAP: "Mapa do Tesouro"
        }
        return names.get(self.resource_type, self.resource_type.value)
    
    def _get_description(self) -> str:
        """Get item description"""
        descriptions = {
            ResourceType.GOLD: "Moeda de ouro",
            ResourceType.GEMS: "Gemas preciosas",
            ResourceType.KEY: "Chave simples para portas trancadas",
            ResourceType.MASTER_KEY: "Chave que abre qualquer porta",
            ResourceType.PICKAXE: "Ferramenta para quebrar paredes",
            ResourceType.ROPE: "Corda para atravessar buracos",
            ResourceType.EXPLOSIVES: "Explosivos para destruir obstáculos",
            ResourceType.TORCH: "Ilumina áreas escuras",
            ResourceType.TRAP_DETECTOR: "Detecta armadilhas ocultas",
            ResourceType.HEALTH_POTION: "Restaura 50 HP",
            ResourceType.STAMINA_POTION: "Restaura 50 stamina",
            ResourceType.STRENGTH_POTION: "Aumenta ataque por 3 turnos",
            ResourceType.DEFENSE_POTION: "Aumenta defesa por 3 turnos",
            ResourceType.HEAT_RESISTANCE_POTION: "Protege contra calor extremo",
            ResourceType.RUNE: "Runa mágica com poder desconhecido",
            ResourceType.SLIME_CORE: "Núcleo de slime (material de craft)",
            ResourceType.ARMOR_SHARD: "Fragmento de armadura antiga",
            ResourceType.GAS_MASK: "Protege contra gases tóxicos",
            ResourceType.TREASURE_MAP: "Revela localização do tesouro"
        }
        return descriptions.get(self.resource_type, "Item desconhecido")
    
    def _get_value(self) -> int:
        """Get gold value of item"""
        values = {
            ResourceType.GOLD: 1,
            ResourceType.GEMS: 10,
            ResourceType.KEY: 15,
            ResourceType.MASTER_KEY: 100,
            ResourceType.PICKAXE: 25,
            ResourceType.ROPE: 10,
            ResourceType.EXPLOSIVES: 30,
            ResourceType.TORCH: 5,
            ResourceType.TRAP_DETECTOR: 40,
            ResourceType.HEALTH_POTION: 20,
            ResourceType.STAMINA_POTION: 15,
            ResourceType.STRENGTH_POTION: 25,
            ResourceType.DEFENSE_POTION: 25,
            ResourceType.HEAT_RESISTANCE_POTION: 30,
            ResourceType.RUNE: 50,
            ResourceType.SLIME_CORE: 15,
            ResourceType.ARMOR_SHARD: 35,
            ResourceType.GAS_MASK: 45,
            ResourceType.TREASURE_MAP: 75
        }
        return values.get(self.resource_type, 10)
    
    def _is_consumable(self) -> bool:
        """Check if item is consumable"""
        consumables = {
            ResourceType.HEALTH_POTION, ResourceType.STAMINA_POTION,
            ResourceType.STRENGTH_POTION, ResourceType.DEFENSE_POTION,
            ResourceType.HEAT_RESISTANCE_POTION, ResourceType.EXPLOSIVES,
            ResourceType.TORCH, ResourceType.ROPE
        }
        return self.resource_type in consumables
    
    def _is_stackable(self) -> bool:
        """Check if item is stackable"""
        non_stackable = {ResourceType.PICKAXE, ResourceType.TRAP_DETECTOR, 
                        ResourceType.GAS_MASK, ResourceType.MASTER_KEY}
        return self.resource_type not in non_stackable

class ResourceManager:
    """Manages resource drops, probabilities, and rewards"""
    
    @staticmethod
    def generate_exploration_reward() -> Dict[str, int]:
        """Generate random reward for exploring a vertex"""
        rewards = {}
        
        # Gold (common)
        if random.random() < 0.6:
            rewards["gold"] = random.randint(5, 20)
        
        # Gems (uncommon)
        if random.random() < 0.2:
            rewards["gems"] = random.randint(1, 5)
        
        # Random item (rare)
        if random.random() < 0.15:
            items = ["key", "rope", "health_potion", "stamina_potion"]
            item = random.choice(items)
            rewards[item] = 1
        
        return rewards
    
    @staticmethod
    def generate_monster_loot(monster_level: int) -> Dict[str, int]:
        """Generate loot from defeating a monster"""
        loot = {}
        
        # Gold (guaranteed)
        base_gold = 10 + monster_level * 5
        loot["gold"] = random.randint(base_gold, base_gold * 2)
        
        # Gems (chance increases with level)
        gem_chance = 0.2 + monster_level * 0.05
        if random.random() < gem_chance:
            loot["gems"] = random.randint(1, 3 + monster_level)
        
        # Random item drop
        if random.random() < 0.3:
            possible_items = [
                "health_potion", "stamina_potion", "key",
                "rope", "explosives", "rune"
            ]
            item = random.choice(possible_items)
            loot[item] = 1
        
        # Rare drop (higher level = better chance)
        rare_chance = 0.05 + monster_level * 0.02
        if random.random() < rare_chance:
            rare_items = ["armor_shard", "master_key", "treasure_map", "trap_detector"]
            item = random.choice(rare_items)
            loot[item] = 1
        
        return loot
    
    @staticmethod
    def generate_treasure_chest_loot(chest_quality: str = "normal") -> Dict[str, int]:
        """
        Generate loot for treasure chest
        chest_quality: "poor", "normal", "rich", "legendary"
        """
        loot = {}
        
        if chest_quality == "poor":
            loot["gold"] = random.randint(10, 30)
            if random.random() < 0.5:
                loot["health_potion"] = 1
        
        elif chest_quality == "normal":
            loot["gold"] = random.randint(30, 80)
            loot["gems"] = random.randint(1, 5)
            items = ["health_potion", "stamina_potion", "rope", "key"]
            for _ in range(random.randint(1, 2)):
                loot[random.choice(items)] = loot.get(random.choice(items), 0) + 1
        
        elif chest_quality == "rich":
            loot["gold"] = random.randint(80, 150)
            loot["gems"] = random.randint(5, 15)
            items = ["health_potion", "stamina_potion", "strength_potion", 
                    "defense_potion", "explosives", "key", "rune"]
            for _ in range(random.randint(2, 4)):
                loot[random.choice(items)] = loot.get(random.choice(items), 0) + 1
        
        elif chest_quality == "legendary":
            loot["gold"] = random.randint(200, 500)
            loot["gems"] = random.randint(15, 30)
            loot["master_key"] = 1
            loot["treasure_map"] = 1
            rare_items = ["armor_shard", "trap_detector", "gas_mask", "rune"]
            for item in rare_items:
                if random.random() < 0.7:
                    loot[item] = random.randint(1, 3)
        
        return loot
    
    @staticmethod
    def use_potion(player, potion_type: ResourceType) -> tuple[bool, str]:
        """
        Use a potion on a player
        Returns (success, message)
        """
        if not player.has_item(potion_type.value):
            return False, f"Você não tem {potion_type.value}"
        
        message = ""
        
        if potion_type == ResourceType.HEALTH_POTION:
            healed = player.heal(50)
            message = f"💚 Poção de vida usada! Curado {healed} HP"
        
        elif potion_type == ResourceType.STAMINA_POTION:
            restored = player.restore_stamina(50)
            message = f"⚡ Poção de stamina usada! Restaurado {restored} stamina"
        
        elif potion_type == ResourceType.STRENGTH_POTION:
            from .player import Buff, BuffType
            buff = Buff(BuffType.ATTACK_BOOST, 5, 3, "Poção de Força")
            player.add_buff(buff)
            message = "💪 Poção de força usada! Ataque aumentado por 3 turnos"
        
        elif potion_type == ResourceType.DEFENSE_POTION:
            from .player import Buff, BuffType
            buff = Buff(BuffType.DEFENSE_BOOST, 5, 3, "Poção de Defesa")
            player.add_buff(buff)
            message = "🛡️ Poção de defesa usada! Defesa aumentada por 3 turnos"
        
        else:
            return False, "Poção desconhecida"
        
        player.remove_item(potion_type.value)
        return True, message
    
    @staticmethod
    def get_drop_probabilities() -> Dict[str, float]:
        """Get probability table for random drops"""
        return {
            "gold": 0.6,
            "gems": 0.2,
            "health_potion": 0.3,
            "stamina_potion": 0.25,
            "key": 0.15,
            "rope": 0.2,
            "explosives": 0.1,
            "torch": 0.25,
            "pickaxe": 0.08,
            "trap_detector": 0.05,
            "strength_potion": 0.12,
            "defense_potion": 0.12,
            "heat_resistance_potion": 0.08,
            "rune": 0.1,
            "slime_core": 0.15,
            "armor_shard": 0.07,
            "gas_mask": 0.06,
            "master_key": 0.02,
            "treasure_map": 0.03
        }
