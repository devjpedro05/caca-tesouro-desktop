"""
Player System with Complete Attributes, Inventory, and Status Management
"""
from enum import Enum
from typing import List, Dict, Optional
from dataclasses import dataclass, field

class BuffType(Enum):
    """Types of temporary buffs/debuffs"""
    ATTACK_BOOST = "attack_boost"
    DEFENSE_BOOST = "defense_boost"
    SPEED_BOOST = "speed_boost"
    REGENERATION = "regeneration"
    POISON = "poison"
    WEAKNESS = "weakness"
    SLOW = "slow"
    INVULNERABILITY = "invulnerability"
    INVISIBILITY = "invisibility"
    CONFUSION = "confusion"

@dataclass
class Buff:
    """Represents a temporary buff or debuff"""
    buff_type: BuffType
    magnitude: int  # Strength of the effect
    duration: int  # Turns remaining
    description: str = ""
    
    def tick(self) -> bool:
        """Decrease duration by 1, returns True if buff expired"""
        self.duration -= 1
        return self.duration <= 0

class Player:
    """
    Represents a player with complete RPG-style attributes
    """
    def __init__(self, id: int, name: str, color: str, start_vertex_id: int):
        # Basic info
        self.id = id
        self.name = name
        self.color = color  # Hex string or QColor name
        self.current_vertex_id = start_vertex_id
        
        # Combat stats
        self.max_hp = 100
        self.hp = 100
        self.attack = 10
        self.defense = 5
        self.critical_chance = 0.1  # 10% chance
        self.dodge_chance = 0.1  # 10% chance
        
        # Resources
        self.stamina = 100
        self.max_stamina = 100
        self.action_points = 3  # Actions per turn
        self.max_action_points = 3
        
        # Progression
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        
        # Economy
        self.gold = 0
        self.total_cost = 0  # Total movement cost (for scoring)
        
        # Inventory
        self.hand_cards = []  # List of Card objects
        self.max_hand_size = 7
        self.inventory = {}  # item_type -> quantity
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        
        # Status
        self.buffs: List[Buff] = []
        self.is_alive = True
        self.is_stunned = False
        self.turns_stunned = 0
        
        # Statistics
        self.monsters_killed = 0
        self.treasures_found = 0
        self.distance_traveled = 0
        self.cards_played = 0
    
    def take_damage(self, amount: int) -> int:
        """
        Take damage, accounting for defense and buffs
        Returns actual damage taken
        """
        # Apply defense
        damage = max(1, amount - self.defense)
        
        # Check for invulnerability
        if self.has_buff(BuffType.INVULNERABILITY):
            return 0
        
        # Apply weakness debuff
        if self.has_buff(BuffType.WEAKNESS):
            damage = int(damage * 1.5)
        
        # Apply damage
        self.hp = max(0, self.hp - damage)
        
        if self.hp <= 0:
            self.is_alive = False
        
        return damage
    
    def heal(self, amount: int) -> int:
        """
        Heal HP, returns actual amount healed
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def restore_stamina(self, amount: int) -> int:
        """
        Restore stamina, returns actual amount restored
        """
        old_stamina = self.stamina
        self.stamina = min(self.max_stamina, self.stamina + amount)
        return self.stamina - old_stamina
    
    def consume_stamina(self, amount: int) -> bool:
        """
        Consume stamina, returns True if successful
        """
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    
    def consume_action_points(self, amount: int = 1) -> bool:
        """
        Consume action points, returns True if successful
        """
        if self.action_points >= amount:
            self.action_points -= amount
            return True
        return False
    
    def reset_action_points(self):
        """Reset action points to maximum (called at start of turn)"""
        self.action_points = self.max_action_points
        self.stamina = min(self.max_stamina, self.stamina + 20)  # Restore some stamina
    
    def add_buff(self, buff: Buff):
        """Add a buff/debuff to the player"""
        # Check if buff already exists, if so, refresh duration
        for existing_buff in self.buffs:
            if existing_buff.buff_type == buff.buff_type:
                existing_buff.duration = max(existing_buff.duration, buff.duration)
                existing_buff.magnitude = max(existing_buff.magnitude, buff.magnitude)
                return
        
        self.buffs.append(buff)
    
    def has_buff(self, buff_type: BuffType) -> bool:
        """Check if player has a specific buff"""
        return any(b.buff_type == buff_type for b in self.buffs)
    
    def get_buff(self, buff_type: BuffType) -> Optional[Buff]:
        """Get a specific buff if it exists"""
        for buff in self.buffs:
            if buff.buff_type == buff_type:
                return buff
        return None
    
    def tick_buffs(self) -> List[str]:
        """
        Update all buffs (called each turn)
        Returns list of messages about expired buffs
        """
        messages = []
        expired = []
        
        for buff in self.buffs:
            # Apply per-turn effects
            if buff.buff_type == BuffType.REGENERATION:
                healed = self.heal(buff.magnitude)
                if healed > 0:
                    messages.append(f"{self.name} regenerou {healed} HP")
            
            elif buff.buff_type == BuffType.POISON:
                damage = self.take_damage(buff.magnitude)
                messages.append(f"{self.name} sofreu {damage} de dano por veneno")
            
            # Tick duration
            if buff.tick():
                expired.append(buff)
                messages.append(f"{self.name}: {buff.buff_type.value} expirou")
        
        # Remove expired buffs
        for buff in expired:
            self.buffs.remove(buff)
        
        return messages
    
    def add_item(self, item_type: str, quantity: int = 1):
        """Add item to inventory"""
        self.inventory[item_type] = self.inventory.get(item_type, 0) + quantity
    
    def remove_item(self, item_type: str, quantity: int = 1) -> bool:
        """
        Remove item from inventory
        Returns True if successful, False if not enough items
        """
        current = self.inventory.get(item_type, 0)
        if current >= quantity:
            self.inventory[item_type] = current - quantity
            if self.inventory[item_type] <= 0:
                del self.inventory[item_type]
            return True
        return False
    
    def has_item(self, item_type: str, quantity: int = 1) -> bool:
        """Check if player has enough of an item"""
        return self.inventory.get(item_type, 0) >= quantity
    
    def add_gold(self, amount: int):
        """Add gold to player"""
        self.gold += amount
    
    def spend_gold(self, amount: int) -> bool:
        """
        Spend gold
        Returns True if successful, False if not enough gold
        """
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def gain_experience(self, amount: int) -> List[str]:
        """
        Gain experience, returns list of level-up messages
        """
        messages = []
        self.experience += amount
        
        while self.experience >= self.experience_to_next_level:
            self.level_up()
            messages.append(f"🎉 {self.name} subiu para o nível {self.level}!")
        
        return messages
    
    def level_up(self):
        """Level up the player"""
        self.level += 1
        self.experience -= self.experience_to_next_level
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Stat increases
        self.max_hp += 10
        self.hp = self.max_hp  # Full heal on level up
        self.attack += 2
        self.defense += 1
        self.max_stamina += 10
        self.stamina = self.max_stamina
        
        # Occasionally increase max AP
        if self.level % 3 == 0:
            self.max_action_points += 1
            self.action_points = self.max_action_points
    
    def get_effective_attack(self) -> int:
        """Get attack value including buffs"""
        attack = self.attack
        
        if self.has_buff(BuffType.ATTACK_BOOST):
            buff = self.get_buff(BuffType.ATTACK_BOOST)
            attack += buff.magnitude
        
        if self.has_buff(BuffType.WEAKNESS):
            attack = int(attack * 0.7)
        
        return max(1, attack)
    
    def get_effective_defense(self) -> int:
        """Get defense value including buffs"""
        defense = self.defense
        
        if self.has_buff(BuffType.DEFENSE_BOOST):
            buff = self.get_buff(BuffType.DEFENSE_BOOST)
            defense += buff.magnitude
        
        return max(0, defense)
    
    def can_act(self) -> bool:
        """Check if player can take actions this turn"""
        if not self.is_alive:
            return False
        if self.is_stunned and self.turns_stunned > 0:
            return False
        return True
    
    def stun(self, turns: int):
        """Stun the player for a number of turns"""
        self.is_stunned = True
        self.turns_stunned = turns
    
    def update_stun(self):
        """Update stun status (called each turn)"""
        if self.is_stunned:
            self.turns_stunned -= 1
            if self.turns_stunned <= 0:
                self.is_stunned = False
                self.turns_stunned = 0
    
    def get_status_summary(self) -> Dict[str, any]:
        """Get a summary of player status for UI"""
        return {
            "name": self.name,
            "level": self.level,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "attack": self.get_effective_attack(),
            "defense": self.get_effective_defense(),
            "gold": self.gold,
            "action_points": self.action_points,
            "max_action_points": self.max_action_points,
            "buffs": [f"{b.buff_type.value} ({b.duration})" for b in self.buffs],
            "is_alive": self.is_alive,
            "is_stunned": self.is_stunned
        }
    
    def __repr__(self):
        return f"Player({self.name}, Lv{self.level}, HP:{self.hp}/{self.max_hp}, pos={self.current_vertex_id})"
