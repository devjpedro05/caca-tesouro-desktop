"""
Obstacles and Enemies System
Includes monsters, environmental obstacles, and interaction mechanics
"""
import random
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .game_state import GameState

# ============================================
# MONSTERS / ENEMIES
# ============================================

class MonsterType(Enum):
    """Types of monsters"""
    GOBLIN = "goblin"
    ORC = "orc"
    CAVE_SPIRIT = "cave_spirit"
    STONE_GOLEM = "stone_golem"
    GIANT_BAT = "giant_bat"
    SLIME = "slime"

class Monster:
    """Base class for all monsters"""
    def __init__(self, monster_type: MonsterType, level: int = 1):
        self.monster_type = monster_type
        self.level = level
        
        # Base stats (will be modified by type and level)
        self.max_hp = 30
        self.hp = 30
        self.attack = 5
        self.defense = 2
        self.speed = 5
        
        # Special attributes
        self.surprise_attack_chance = 0.1
        self.flee_chance = 0.2
        
        # Rewards
        self.gold_reward = (10, 30)
        self.exp_reward = 20
        self.item_drop_chance = 0.3
        self.possible_drops = ["potion", "key"]
        
        # Apply type-specific stats
        self._apply_type_stats()
        
        # Scale by level
        self._scale_by_level()
    
    def _apply_type_stats(self):
        """Apply stats based on monster type"""
        if self.monster_type == MonsterType.GOBLIN:
            self.max_hp = 25
            self.attack = 6
            self.defense = 1
            self.speed = 8
            self.surprise_attack_chance = 0.25
            self.gold_reward = (5, 15)
            self.exp_reward = 15
        
        elif self.monster_type == MonsterType.ORC:
            self.max_hp = 50
            self.attack = 12
            self.defense = 5
            self.speed = 3
            self.surprise_attack_chance = 0.05
            self.gold_reward = (20, 40)
            self.exp_reward = 35
        
        elif self.monster_type == MonsterType.CAVE_SPIRIT:
            self.max_hp = 30
            self.attack = 8
            self.defense = 0
            self.speed = 10
            self.surprise_attack_chance = 0.3
            self.flee_chance = 0.4
            self.gold_reward = (10, 25)
            self.exp_reward = 25
            self.possible_drops = ["gem", "rune"]
        
        elif self.monster_type == MonsterType.STONE_GOLEM:
            self.max_hp = 80
            self.attack = 10
            self.defense = 10
            self.speed = 1
            self.surprise_attack_chance = 0.0
            self.flee_chance = 0.0
            self.gold_reward = (30, 60)
            self.exp_reward = 50
            self.possible_drops = ["gem", "key", "armor_shard"]
        
        elif self.monster_type == MonsterType.GIANT_BAT:
            self.max_hp = 20
            self.attack = 7
            self.defense = 1
            self.speed = 12
            self.surprise_attack_chance = 0.35
            self.gold_reward = (5, 10)
            self.exp_reward = 12
        
        elif self.monster_type == MonsterType.SLIME:
            self.max_hp = 40
            self.attack = 4
            self.defense = 3
            self.speed = 2
            self.surprise_attack_chance = 0.0
            self.gold_reward = (8, 20)
            self.exp_reward = 18
            self.possible_drops = ["potion", "slime_core"]
        
        self.hp = self.max_hp
    
    def _scale_by_level(self):
        """Scale stats by monster level"""
        multiplier = 1.0 + (self.level - 1) * 0.3
        self.max_hp = int(self.max_hp * multiplier)
        self.hp = self.max_hp
        self.attack = int(self.attack * multiplier)
        self.defense = int(self.defense * multiplier)
        self.exp_reward = int(self.exp_reward * multiplier)
        self.gold_reward = (int(self.gold_reward[0] * multiplier), 
                           int(self.gold_reward[1] * multiplier))
    
    def take_damage(self, amount: int) -> int:
        """Take damage, returns actual damage taken"""
        damage = max(1, amount - self.defense)
        self.hp = max(0, self.hp - damage)
        return damage
    
    def is_alive(self) -> bool:
        """Check if monster is still alive"""
        return self.hp > 0
    
    def get_reward_gold(self) -> int:
        """Get random gold reward"""
        return random.randint(self.gold_reward[0], self.gold_reward[1])
    
    def get_reward_items(self) -> list:
        """Get random item drops"""
        drops = []
        if random.random() < self.item_drop_chance:
            drops.append(random.choice(self.possible_drops))
        return drops
    
    def __repr__(self):
        return f"{self.monster_type.value.title()} Lv{self.level} (HP:{self.hp}/{self.max_hp})"

# ============================================
# OBSTACLES
# ============================================

class ObstacleType(Enum):
    """Types of obstacles"""
    WALL = "wall"
    HOLE = "hole"
    GAS_CLOUD = "gas_cloud"
    LOCKED_DOOR = "locked_door"
    TRAP = "trap"
    ROCKFALL = "rockfall"
    TREASURE_CHEST = "treasure_chest"
    LAVA_POOL = "lava_pool"

class Obstacle:
    """Base class for obstacles"""
    def __init__(self, obstacle_type: ObstacleType):
        self.obstacle_type = obstacle_type
        self.is_passable = True
        self.is_destructible = False
        self.is_active = True
        self.hp = 0  # For destructible obstacles
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        """
        Interact with obstacle
        Returns (success, message)
        """
        return True, ""
    
    def can_pass(self, player: 'Player') -> tuple[bool, str]:
        """
        Check if player can pass this obstacle
        Returns (can_pass, reason_if_not)
        """
        return self.is_passable, ""
    
    def destroy(self) -> tuple[bool, str]:
        """
        Attempt to destroy obstacle
        Returns (destroyed, message)
        """
        if not self.is_destructible:
            return False, "Este obstáculo não pode ser destruído"
        return True, "Obstáculo destruído!"

class WallObstacle(Obstacle):
    """Breakable wall"""
    def __init__(self, hp: int = 30):
        super().__init__(ObstacleType.WALL)
        self.is_passable = False
        self.is_destructible = True
        self.hp = hp
        self.max_hp = hp
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item("pickaxe"):
            damage = random.randint(10, 20)
            self.hp -= damage
            if self.hp <= 0:
                self.is_passable = True
                self.is_active = False
                return True, f"💥 Parede destruída! ({damage} dano)"
            return True, f"🔨 Parede danificada: {self.hp}/{self.max_hp} HP restantes"
        return False, "Você precisa de uma picareta para quebrar esta parede"
    
    def destroy(self) -> tuple[bool, str]:
        self.hp = 0
        self.is_passable = True
        self.is_active = False
        return True, "Parede explodida!"

class HoleObstacle(Obstacle):
    """Hole that requires rope to cross"""
    def __init__(self):
        super().__init__(ObstacleType.HOLE)
        self.is_passable = False
    
    def can_pass(self, player: 'Player') -> tuple[bool, str]:
        if player.has_item("rope"):
            return True, ""
        return False, "Você precisa de uma corda para atravessar este buraco"
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item("rope"):
            player.remove_item("rope")
            self.is_passable = True
            return True, "🪢 Você usou uma corda para atravessar o buraco"
        return False, "Você precisa de uma corda"

class GasObstacle(Obstacle):
    """Toxic gas cloud"""
    def __init__(self, damage_per_turn: int = 5, duration: int = 3):
        super().__init__(ObstacleType.GAS_CLOUD)
        self.is_passable = True
        self.damage_per_turn = damage_per_turn
        self.duration = duration
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item("gas_mask"):
            return True, "😷 Sua máscara de gás protegeu você"
        
        damage = player.take_damage(self.damage_per_turn)
        from .player import Buff, BuffType
        poison_buff = Buff(BuffType.POISON, self.damage_per_turn, self.duration, "Gás tóxico")
        player.add_buff(poison_buff)
        return True, f"☠️ Você inalou gás tóxico! Perdeu {damage} HP e está envenenado"

class LockedDoorObstacle(Obstacle):
    """Locked door requiring key"""
    def __init__(self, key_type: str = "key"):
        super().__init__(ObstacleType.LOCKED_DOOR)
        self.is_passable = False
        self.is_destructible = True
        self.key_type = key_type
        self.hp = 40
    
    def can_pass(self, player: 'Player') -> tuple[bool, str]:
        if player.has_item(self.key_type):
            return True, ""
        return False, f"Porta trancada! Você precisa de: {self.key_type}"
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item(self.key_type):
            player.remove_item(self.key_type)
            self.is_passable = True
            self.is_active = False
            return True, f"🔓 Porta destrancada com {self.key_type}!"
        return False, f"Você precisa de: {self.key_type}"

class TrapObstacle(Obstacle):
    """Trap that damages player"""
    def __init__(self, damage: int = 15, stun_turns: int = 0):
        super().__init__(ObstacleType.TRAP)
        self.is_passable = True
        self.damage = damage
        self.stun_turns = stun_turns
        self.triggered = False
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if self.triggered:
            return True, ""
        
        # Check if player detects trap
        if player.has_item("trap_detector") or random.random() < 0.3:
            return True, "⚠️ Você detectou uma armadilha e a evitou!"
        
        self.triggered = True
        damage = player.take_damage(self.damage)
        message = f"🪤 ARMADILHA! Você sofreu {damage} de dano"
        
        if self.stun_turns > 0:
            player.stun(self.stun_turns)
            message += f" e ficou atordoado por {self.stun_turns} turnos"
        
        return True, message

class RockfallObstacle(Obstacle):
    """Rockfall blocking passage"""
    def __init__(self):
        super().__init__(ObstacleType.ROCKFALL)
        self.is_passable = False
        self.is_destructible = True
        self.hp = 50
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item("explosives"):
            player.remove_item("explosives")
            self.is_passable = True
            self.is_active = False
            # Chance of taking damage from explosion
            if random.random() < 0.3:
                damage = player.take_damage(random.randint(5, 15))
                return True, f"💣 Rochas explodidas! Você sofreu {damage} de dano"
            return True, "💣 Rochas explodidas com sucesso!"
        return False, "Você precisa de explosivos para remover estas rochas"

class TreasureChestObstacle(Obstacle):
    """Treasure chest with rewards"""
    def __init__(self, gold: int = 0, items: list = None):
        super().__init__(ObstacleType.TREASURE_CHEST)
        self.is_passable = True
        self.opened = False
        self.gold = gold if gold > 0 else random.randint(20, 100)
        self.items = items if items else self._generate_random_items()
        self.is_trapped = random.random() < 0.2
    
    def _generate_random_items(self) -> list:
        """Generate random items for chest"""
        possible_items = ["potion", "key", "rope", "gem", "explosives", "pickaxe"]
        num_items = random.randint(1, 3)
        return [random.choice(possible_items) for _ in range(num_items)]
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if self.opened:
            return False, "Baú vazio (já foi aberto)"
        
        message = ""
        
        # Check for trap
        if self.is_trapped:
            if player.has_item("trap_detector") or random.random() < 0.2:
                message = "⚠️ Você desarmou a armadilha do baú!\n"
            else:
                damage = player.take_damage(random.randint(10, 20))
                message = f"🪤 O baú estava armadilhado! Você sofreu {damage} de dano\n"
        
        # Give rewards
        player.add_gold(self.gold)
        message += f"💰 Você encontrou {self.gold} ouro!\n"
        
        for item in self.items:
            player.add_item(item)
            message += f"📦 Você encontrou: {item}\n"
        
        player.treasures_found += 1
        self.opened = True
        
        return True, message.strip()

class LavaPoolObstacle(Obstacle):
    """Lava pool that damages player"""
    def __init__(self, damage: int = 20):
        super().__init__(ObstacleType.LAVA_POOL)
        self.is_passable = True
        self.damage = damage
    
    def can_pass(self, player: 'Player') -> tuple[bool, str]:
        if player.has_item("heat_resistance_potion"):
            return True, ""
        return True, "⚠️ Atravessar a lava causará dano!"
    
    def interact(self, player: 'Player', game_state: 'GameState') -> tuple[bool, str]:
        if player.has_item("heat_resistance_potion"):
            player.remove_item("heat_resistance_potion")
            return True, "🧪 Poção de resistência ao calor protegeu você da lava"
        
        damage = player.take_damage(self.damage)
        return True, f"🔥 Você atravessou a lava e sofreu {damage} de dano!"
