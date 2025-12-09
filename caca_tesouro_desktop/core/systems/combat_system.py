# core/systems/combat_system.py
import random
from typing import List, Dict, Any, Optional
from ..combat import CombatSystem as LegacyCombat
from ..player import Player
from ..obstacles import Monster

class TickCombatInstance:
    """
    Tick-based simultaneous-combat instance.

    - player and monster have separate cooldowns (seconds).
    - when ready, they enqueue an attack for that tick; all attacks that happen
      during the same tick are applied simultaneously (so both can kill each other).
    - tick() advances the internal timers by delta seconds and resolves attacks.
    """
    def __init__(self, player: Player, monster: Monster):
        self.player = player
        self.monster = monster

        # per-actor attack timers and cooldowns
        # Start fully charged for immediate action!
        self.player_cooldown = getattr(player, "attack_cooldown", 1.0)
        self.player_timer = self.player_cooldown

        self.monster_cooldown = max(0.4, 1.5 - (getattr(monster, "speed", 1) * 0.05))
        self.monster_timer = self.monster_cooldown * 0.5 # Monster starts half-charged (fairness)

        # bookkeeping
        self.turns = 0
        self.max_turns = 120
        self.ended = False

        # transient per-tick logs (pumped to GameState each manager.update)
        self.tick_log: List[str] = []

        # final combat_log stored in result (kept minimal here; manager prints tick_log)
        self.combined_log: List[str] = []

    def tick(self, delta: float):
        """Advance combat by delta seconds and resolve any ready attacks."""
        if self.ended:
            return
        
        # Clear tick log from previous tick
        self.tick_log.clear()

        # Advance internal timers
        self.player_timer += delta
        self.monster_timer += delta

        # actions that will be resolved simultaneously this tick
        actions: List[tuple] = []  # tuples: (who_str, raw_damage, is_crit)

        # player ready to attack?
        if self.player.is_alive and self.player_timer >= self.player_cooldown:
            self.player_timer = 0.0
            
            # Check stamina - cada ataque custa 5 pontos de stamina
            attack_stamina_cost = 5
            if self.player.stamina >= attack_stamina_cost:
                self.player.consume_stamina(attack_stamina_cost)
                
                is_crit = LegacyCombat.check_critical_hit(getattr(self.player, "critical_chance", 0.0))
                raw_dmg = LegacyCombat.calculate_damage(self.player.get_effective_attack(), self.monster.defense, is_crit)
                actions.append(("player", raw_dmg, is_crit))
                self.tick_log.append(f"⚔️ {self.player.name} atacou ({'CRIT' if is_crit else 'hit'}) e causou {raw_dmg} dano bruto (-{attack_stamina_cost} stamina)")
            else:
                self.tick_log.append(f"⚠️ {self.player.name} sem stamina para atacar! ({int(self.player.stamina)}/{attack_stamina_cost})")

        # monster ready to attack?
        if self.monster.is_alive() and self.monster_timer >= self.monster_cooldown:
            self.monster_timer = 0.0
            is_crit = LegacyCombat.check_critical_hit(getattr(self.monster, "critical_chance", 0.0) if hasattr(self.monster, "critical_chance") else 0.1)
            raw_dmg = LegacyCombat.calculate_damage(self.monster.attack, self.player.get_effective_defense(), is_crit)
            actions.append(("monster", raw_dmg, is_crit))
            self.tick_log.append(f"🗡️ {self.monster.monster_type.value.title()} atacou ({'CRIT' if is_crit else 'hit'}) e causou {raw_dmg} dano bruto")

        # If there are actions this tick, apply them simultaneously
        if actions:
            damage_to_player = 0
            damage_to_monster = 0
            for who, dmg, crit in actions:
                if who == "player":
                    damage_to_monster += dmg
                else:
                    damage_to_player += dmg

            # Apply damage to player
            if damage_to_player:
                actual = self.player.take_damage(damage_to_player)
                self.tick_log.append(f"➡️ {self.player.name} recebeu {actual} dano (HP: {self.player.hp}/{self.player.max_hp})")

            # Apply damage to monster
            if damage_to_monster:
                actual_m = self.monster.take_damage(damage_to_monster)
                self.tick_log.append(f"➡️ {self.monster.monster_type.value.title()} recebeu {actual_m} dano (HP: {self.monster.hp}/{self.monster.max_hp})")

            self.turns += 1

        # End conditions (check after applying simultaneous damage)
        if not self.player.is_alive:
            self.ended = True
            self.tick_log.append(f"💀 {self.player.name} foi derrotado!")
            return  # Stop immediately
        if not self.monster.is_alive():
            self.ended = True
            self.tick_log.append(f"🏆 {self.player.name} derrotou {self.monster.monster_type.value.title()}!")
            # collect rewards into combined_log later via get_result
            return  # Stop immediately

        if self.turns >= self.max_turns:
            self.ended = True
            return  # Stop immediately
            self.tick_log.append(f"⏱️ Combate excedeu {self.max_turns} ticks (empate).")

    def get_result(self) -> Dict[str, Any]:
        """Return a summarized result compatible with CombatResult (partial)."""
        from ..combat import CombatResult
        res = CombatResult()
        res.turns_taken = self.turns

        # merge tick_log into result log (manager will also print tick_log in real time)
        res.combat_log = self.tick_log.copy() + self.combined_log.copy()
        res.player_died = not self.player.is_alive
        res.player_won = self.monster and (not self.monster.is_alive())

        if res.player_won:
            res.exp_gained = getattr(self.monster, "exp_reward", 0)
            res.gold_gained = self.monster.get_reward_gold() if hasattr(self.monster, "get_reward_gold") else 0
            res.items_gained = self.monster.get_reward_items() if hasattr(self.monster, "get_reward_items") else []

        return res


class CombatManager:
    """Keep track of active tick-based combats (if any)."""
    def __init__(self, game_state):
        self.gs = game_state
        self.active_instances: List[TickCombatInstance] = []
        self.on_damage_callback = None  # func(x, y, amount, target_type)
        self.on_death_callback = None   # func(unit, type)

    def start_combat(self, player: Player, monster: Monster) -> TickCombatInstance:
        inst = TickCombatInstance(player, monster)
        self.active_instances.append(inst)
        # Log is already done in game_state.start_combat, no need to duplicate
        return inst

    def update(self, delta_time: float):
        """Tick all active combats and finalize finished ones. Called each frame with delta seconds."""
        finished: List[TickCombatInstance] = []

        for inst in list(self.active_instances):
            try:
                inst.tick(delta_time)
            except Exception as e:
                # Log but keep system alive
                self.gs.log(f"[ERROR] TickCombatInstance.tick: {e}")

            # Emit per-tick logs immediately so UI shows action flow
            if getattr(inst, "tick_log", None):
                for msg in inst.tick_log:
                    self.gs.log(msg)
                    
                    # DETECT DAMAGE FOR VISUAL POPUPS
                    # Parse msg to trigger callback
                    # "➡️ Player recebeu 6 dano"
                    # "➡️ Goblin recebeu 15 dano"
                    if "recebeu" in msg and "dano" in msg:
                        try:
                            parts = msg.split()
                            damage = int([p for p in parts if p.isdigit()][0])
                            
                            # Determine target and position
                            target_type = "player" if inst.player.name in msg else "monster"
                            
                            # Get position from player or monster
                            # Assuming they are at same vertex/grid pos
                            # We need grid coordinates. Player has current_vertex_id.
                            # We can get grid pos from graph/grid_map via game_state
                            
                            # This is tricky without direct access to grid_map here.
                            # But we can pass it via callback or look it up.
                            if self.on_damage_callback:
                                # We need to find where they are.
                                # Use player's current vertex to find grid pos?
                                # Let the callback handle the lookup if we pass the entity.
                                self.on_damage_callback(inst.player, inst.monster, damage, target_type)
                                
                        except Exception as e:
                            print(f"[DEBUG] Error parsing damage log: {e}")

                # keep tick_log in result as well (get_result uses a copy)
                # but clear it to avoid repeated logging next frame
                inst.combined_log.extend(inst.tick_log)
                inst.tick_log.clear()

            # If combat ended, finalize (give rewards, persist final logs)
            if inst.ended:
                res = inst.get_result()

                if res.player_won:
                    # Marcar para mostrar recompensas depois (evitar múltiplos diálogos)
                    if not hasattr(inst, '_rewards_shown'):
                        inst._rewards_shown = True
                        
                        self.gs.log(f"🏆 {inst.player.name} venceu o combate!")
                        
                        # Coletar informações de recompensas
                        inst.rewards_summary = []
                        
                        # award XP/gold/items (some methods may return messages)
                        try:
                            inst.player.gain_experience(res.exp_gained)
                            inst.rewards_summary.append(f"⭐ {res.exp_gained} XP")
                        except Exception:
                            pass
                        try:
                            inst.player.add_gold(res.gold_gained)
                            inst.rewards_summary.append(f"💰 {res.gold_gained} Ouro")
                        except Exception:
                            pass
                        
                        # Recompensas baseadas no nível do monstro
                        monster_level = getattr(inst.monster, 'level', 1)
                        
                        # Adicionar poções de cura baseadas no nível
                        health_potions = monster_level
                        for _ in range(health_potions):
                            inst.player.add_item({"name": "Poção de Cura", "id": "health_potion", "type": "consumable", "heal": 20})
                        inst.rewards_summary.append(f"💊 {health_potions}x Poção de Cura")
                        self.gs.log(f"💊 Ganhou {health_potions}x Poção de Cura")
                        
                        # Adicionar escudo se nível >= 2
                        if monster_level >= 2:
                            shield_level = min(monster_level - 1, 3)  # Max shield level 3
                            inst.player.add_item({"name": f"Escudo Nível {shield_level}", "id": f"shield_lv{shield_level}", "type": "equipment", "defense": shield_level * 5})
                            inst.rewards_summary.append(f"🛡️ Escudo Nível {shield_level} (+{shield_level * 5} def)")
                            self.gs.log(f"🛡️ Ganhou Escudo Nível {shield_level}")
                        
                        # Adicionar poções de stamina se nível >= 3
                        if monster_level >= 3:
                            stamina_potions = monster_level - 2
                            for _ in range(stamina_potions):
                                inst.player.add_item({"name": "Poção de Stamina", "id": "stamina_potion", "type": "consumable", "stamina": 30})
                            inst.rewards_summary.append(f"⚡ {stamina_potions}x Poção de Stamina")
                            self.gs.log(f"⚡ Ganhou {stamina_potions}x Poção de Stamina")
                        
                        # Items originais do resultado
                        for it in getattr(res, "items_gained", []):
                            try:
                                inst.player.add_item(it)
                            except Exception:
                                pass
                            self.gs.log(f"📦 Ganhou item: {it}")

                if res.player_died:
                    inst.player.is_alive = False
                    self.gs.log(f"💀 {inst.player.name} morreu em combate!")

                # Don't print combat_log here - it was already logged in real-time above
                # Printing it again would duplicate all combat messages

                finished.append(inst)

        # Remove finished instances
        for f in finished:
            if f in self.active_instances:
                self.active_instances.remove(f)
                
            # Handle death cleanup and callbacks
            if f.ended:
                res = f.get_result()
                
                if res.player_died:
                    if self.on_death_callback:
                        self.on_death_callback(f.player, "player")
                
                if res.player_won:
                    # Monster died
                    if self.on_death_callback:
                        self.on_death_callback(f.monster, "monster")
                    
                    # Forçar atualização da UI antes de mostrar diálogo
                    self._force_ui_update()
                    
                    # Mostrar diálogo de recompensas (apenas uma vez)
                    if hasattr(f, 'rewards_summary') and f.rewards_summary:
                        self._show_rewards_dialog(f.player, f.rewards_summary)
                    
                    # Forçar atualização da UI após diálogo
                    self._force_ui_update()
                    
                    # Cleanup static obstacle if it exists
                    # We need to find if this monster corresponds to an obstacle
                    if hasattr(self.gs, 'grid_map') and hasattr(self.gs.grid_map, 'obstacle_manager'):
                        # Try to match by grid position if available
                        grid_pos = getattr(f.monster, 'grid_pos', None)
                        if grid_pos:
                            obs = self.gs.grid_map.obstacle_manager.get_obstacle(grid_pos)
                            if obs and obs.obstacle_type.value == "monster":
                                obs.is_active = False
                                print(f"[COMBAT] Obstáculo monstro em {grid_pos} removido/desativado.")
                    
                    # Cleanup legacy list
                    if f.monster in self.gs.monsters:
                        self.gs.monsters.remove(f.monster)
    
    def _force_ui_update(self):
        """Forçar atualização da interface do usuário"""
        from PySide6.QtWidgets import QApplication
        
        # Processar eventos pendentes
        QApplication.processEvents()
        
        # Se houver um main_window, forçar refresh
        if hasattr(self.gs, 'main_window') and self.gs.main_window:
            try:
                self.gs.main_window.refresh_all()
            except Exception as e:
                print(f"[DEBUG] Erro ao forçar refresh da UI: {e}")
    
    def _show_rewards_dialog(self, player, rewards_summary):
        """Mostrar diálogo com recompensas ganhas"""
        from PySide6.QtWidgets import QMessageBox, QApplication
        
        if not rewards_summary:
            return
        
        # Criar mensagem formatada
        title = f"🏆 Vitória - {player.name}!"
        message = "Recompensas obtidas:\n\n" + "\n".join(rewards_summary)
        
        # Criar e configurar message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        # Aplicar estilo
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 13px;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 8px 16px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #888888;
            }
        """)
        
        msg_box.exec()
        # Forçar atualização da UI após fechar o diálogo
        QApplication.processEvents()
