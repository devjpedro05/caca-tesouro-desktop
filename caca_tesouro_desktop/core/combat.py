"""
Combat System
Turn-based combat with damage calculation, critical hits, dodges, and flee mechanics
"""
import random
from typing import Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from .obstacles import Monster

class CombatResult:
    """Stores the result of a combat encounter"""
    def __init__(self):
        self.player_won = False
        self.player_fled = False
        self.player_died = False
        self.turns_taken = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.exp_gained = 0
        self.gold_gained = 0
        self.items_gained = []
        self.combat_log = []
    
    def add_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)

class CombatSystem:
    """Handles all combat mechanics"""
    
    @staticmethod
    def calculate_damage(attacker_attack: int, defender_defense: int, 
                        is_critical: bool = False) -> int:
        """
        Calculate damage dealt
        Formula: (attack - defense) * variance * critical_multiplier
        """
        base_damage = max(1, attacker_attack - defender_defense)
        
        # Add variance (±20%)
        variance = random.uniform(0.8, 1.2)
        damage = int(base_damage * variance)
        
        # Critical hit multiplier
        if is_critical:
            damage = int(damage * 2.0)
        
        return max(1, damage)
    
    @staticmethod
    def check_critical_hit(critical_chance: float) -> bool:
        """Check if attack is a critical hit"""
        return random.random() < critical_chance
    
    @staticmethod
    def check_dodge(dodge_chance: float) -> bool:
        """Check if attack is dodged"""
        return random.random() < dodge_chance
    
    @staticmethod
    def check_flee(player_speed: int, monster_speed: int, base_flee_chance: float = 0.5) -> bool:
        """
        Check if player successfully flees
        Chance increases if player is faster than monster
        """
        speed_factor = player_speed / max(1, monster_speed)
        flee_chance = base_flee_chance * speed_factor
        flee_chance = min(0.9, max(0.1, flee_chance))  # Clamp between 10% and 90%
        return random.random() < flee_chance
    
    @staticmethod
    def execute_combat(player: 'Player', monster: 'Monster', 
                      auto_combat: bool = True) -> CombatResult:
        """
        Execute a full combat encounter
        
        Args:
            player: The player
            monster: The monster
            auto_combat: If True, combat is automatic. If False, would need turn-by-turn input
        
        Returns:
            CombatResult with all combat information
        """
        result = CombatResult()
        result.add_log(f"⚔️ Combate iniciado: {player.name} vs {monster}")
        
        turn = 0
        max_turns = 50  # Prevent infinite combat
        
        # Determine who goes first (higher speed goes first)
        player_speed = 10  # Base player speed (could be a player attribute)
        player_goes_first = player_speed >= monster.speed
        
        if player_goes_first:
            result.add_log(f"⚡ {player.name} ataca primeiro!")
        else:
            result.add_log(f"⚡ {monster.monster_type.value.title()} ataca primeiro!")
        
        # Check for surprise attack
        if not player_goes_first and random.random() < monster.surprise_attack_chance:
            result.add_log(f"😱 ATAQUE SURPRESA!")
            damage = CombatSystem.calculate_damage(monster.attack, player.get_effective_defense())
            actual_damage = player.take_damage(damage)
            result.damage_taken += actual_damage
            result.add_log(f"💥 {monster.monster_type.value.title()} causou {actual_damage} de dano!")
        
        # Main combat loop
        while turn < max_turns and player.is_alive and monster.is_alive():
            turn += 1
            result.add_log(f"\n--- Turno {turn} ---")
            
            # Player turn
            if player.is_alive:
                # Check for critical hit
                is_crit = CombatSystem.check_critical_hit(player.critical_chance)
                
                # Calculate damage
                damage = CombatSystem.calculate_damage(
                    player.get_effective_attack(),
                    monster.defense,
                    is_crit
                )
                
                # Apply damage
                actual_damage = monster.take_damage(damage)
                result.damage_dealt += actual_damage
                
                if is_crit:
                    result.add_log(f"💥 CRÍTICO! {player.name} causou {actual_damage} de dano!")
                else:
                    result.add_log(f"⚔️ {player.name} causou {actual_damage} de dano")
                
                result.add_log(f"   {monster.monster_type.value.title()}: {monster.hp}/{monster.max_hp} HP")
                
                if not monster.is_alive():
                    break
            
            # Monster turn
            if monster.is_alive():
                # Check if monster flees
                if random.random() < monster.flee_chance:
                    result.add_log(f"🏃 {monster.monster_type.value.title()} fugiu!")
                    result.player_won = True
                    break
                
                # Check if player dodges
                if CombatSystem.check_dodge(player.dodge_chance):
                    result.add_log(f"💨 {player.name} desviou do ataque!")
                else:
                    # Monster attacks
                    is_crit = CombatSystem.check_critical_hit(0.1)  # 10% crit for monsters
                    
                    damage = CombatSystem.calculate_damage(
                        monster.attack,
                        player.get_effective_defense(),
                        is_crit
                    )
                    
                    actual_damage = player.take_damage(damage)
                    result.damage_taken += actual_damage
                    
                    if is_crit:
                        result.add_log(f"💥 CRÍTICO! {monster.monster_type.value.title()} causou {actual_damage} de dano!")
                    else:
                        result.add_log(f"🗡️ {monster.monster_type.value.title()} causou {actual_damage} de dano")
                    
                    result.add_log(f"   {player.name}: {player.hp}/{player.max_hp} HP")
                    
                    if not player.is_alive:
                        break
        
        # Combat ended - determine outcome
        result.turns_taken = turn
        
        if not player.is_alive:
            result.player_died = True
            result.add_log(f"\n💀 {player.name} foi derrotado!")
        
        elif not monster.is_alive():
            result.player_won = True
            result.add_log(f"\n🏆 Vitória! {monster.monster_type.value.title()} derrotado!")
            
            # Award experience
            result.exp_gained = monster.exp_reward
            exp_messages = player.gain_experience(result.exp_gained)
            result.add_log(f"✨ Ganhou {result.exp_gained} XP")
            for msg in exp_messages:
                result.add_log(msg)
            
            # Award gold
            result.gold_gained = monster.get_reward_gold()
            player.add_gold(result.gold_gained)
            result.add_log(f"💰 Ganhou {result.gold_gained} ouro")
            
            # Award items
            result.items_gained = monster.get_reward_items()
            for item in result.items_gained:
                player.add_item(item)
                result.add_log(f"📦 Ganhou: {item}")
            
            # Update player stats
            player.monsters_killed += 1
        
        else:
            result.add_log(f"\n⏱️ Combate excedeu {max_turns} turnos (empate)")
        
        return result
    
    @staticmethod
    def attempt_flee(player: 'Player', monster: 'Monster') -> Tuple[bool, str]:
        """
        Attempt to flee from combat
        Returns (success, message)
        """
        player_speed = 10  # Base speed (could be player attribute)
        
        if CombatSystem.check_flee(player_speed, monster.speed):
            return True, f"🏃 Você fugiu de {monster.monster_type.value.title()}!"
        else:
            # Failed to flee, monster gets a free attack
            damage = CombatSystem.calculate_damage(monster.attack, player.get_effective_defense())
            actual_damage = player.take_damage(damage)
            return False, f"❌ Falha ao fugir! {monster.monster_type.value.title()} atacou causando {actual_damage} de dano"
    
    @staticmethod
    def get_combat_summary(result: CombatResult) -> str:
        """Get a formatted summary of combat"""
        summary = "\n".join(result.combat_log)
        summary += f"\n\n📊 Resumo do Combate:"
        summary += f"\n   Turnos: {result.turns_taken}"
        summary += f"\n   Dano causado: {result.damage_dealt}"
        summary += f"\n   Dano recebido: {result.damage_taken}"
        
        if result.player_won:
            summary += f"\n   ✅ Vitória!"
            summary += f"\n   XP ganho: {result.exp_gained}"
            summary += f"\n   Ouro ganho: {result.gold_gained}"
            if result.items_gained:
                summary += f"\n   Itens: {', '.join(result.items_gained)}"
        elif result.player_died:
            summary += f"\n   ❌ Derrota"
        elif result.player_fled:
            summary += f"\n   🏃 Fugiu"
        
        return summary
