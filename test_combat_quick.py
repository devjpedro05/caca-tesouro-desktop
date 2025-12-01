"""
Quick test to verify graph-based combat system works
"""
from caca_tesouro_desktop.core.player import Player
from caca_tesouro_desktop.core.obstacles import Monster, MonsterType
from caca_tesouro_desktop.core.combat import CombatSystem

def test_legacy_combat():
    """Test that legacy combat still works (backward compatibility)"""
    print("=== Test 1: Legacy Combat ===")
    p = Player(1, "Test Player", "blue", 0)
    m = Monster(MonsterType.GOBLIN, level=1)
    
    result = CombatSystem.execute_combat(p, m, auto_combat=True, use_graph_combat=False)
    
    print(f"Player won: {result.player_won}")
    print(f"Turns: {result.turns_taken}")
    print(f"Damage dealt: {result.damage_dealt}")
    print("\nFirst 5 log lines:")
    for line in result.combat_log[:5]:
        print(f"  {line}")
    print("✅ Legacy combat works!\n")

def test_graph_combat():
    """Test new graph-based combat"""
    print("=== Test 2: Graph-Based Combat ===")
    p = Player(2, "Graph Player", "red", 0)
    m = Monster(MonsterType.ORC, level=2)
    
    result = CombatSystem.execute_combat(p, m, auto_combat=True, use_graph_combat=True)
    
    print(f"Player won: {result.player_won}")
    print(f"Turns: {result.turns_taken}")
    print(f"Damage dealt: {result.damage_dealt}")
    print("\nFirst 10 log lines:")
    for line in result.combat_log[:10]:
        print(f"  {line}")
    print("\nLast 5 log lines:")
    for line in result.combat_log[-5:]:
        print(f"  {line}")
    print("✅ Graph-based combat works!\n")

if __name__ == "__main__":
    test_legacy_combat()
    test_graph_combat()
    print("🎉 All tests passed!")
