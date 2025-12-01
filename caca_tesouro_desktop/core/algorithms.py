"""
Pathfinding and Graph Algorithms
Includes BFS, Dijkstra, A*, and utility functions for route detection
"""
import heapq
from typing import Dict, List, Tuple, Optional, Set
from .graph import Graph, Vertex, Edge

def bfs(graph: Graph, start_vertex_id: int, max_depth: Optional[int] = None) -> Dict[int, int]:
    """
    Breadth-First Search - returns distances (in number of edges) from start vertex
    
    Args:
        graph: The graph to search
        start_vertex_id: Starting vertex ID
        max_depth: Maximum depth to search (None for unlimited)
    
    Returns:
        Dictionary mapping vertex_id -> distance (in edges)
    """
    if start_vertex_id not in graph.vertices:
        return {}
    
    distances = {start_vertex_id: 0}
    queue = [(start_vertex_id, 0)]
    visited = {start_vertex_id}
    
    while queue:
        current_id, current_dist = queue.pop(0)
        
        if max_depth is not None and current_dist >= max_depth:
            continue
        
        for neighbor_id, edge in graph.neighbors(current_id):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                new_dist = current_dist + 1
                distances[neighbor_id] = new_dist
                queue.append((neighbor_id, new_dist))
    
    return distances

def dijkstra(graph: Graph, start_vertex_id: int, end_vertex_id: Optional[int] = None) -> Tuple[Dict[int, int], Dict[int, int]]:
    """
    Dijkstra's algorithm - finds shortest paths considering edge weights
    
    Args:
        graph: The graph to search
        start_vertex_id: Starting vertex ID
        end_vertex_id: Optional target vertex (if None, computes to all vertices)
    
    Returns:
        Tuple of (distances dict, predecessors dict)
        - distances: vertex_id -> minimum cost to reach from start
        - predecessors: vertex_id -> previous vertex in shortest path
    """
    if start_vertex_id not in graph.vertices:
        return {}, {}
    
    distances = {v_id: float('inf') for v_id in graph.vertices}
    distances[start_vertex_id] = 0
    predecessors = {}
    
    # Priority queue: (distance, vertex_id)
    pq = [(0, start_vertex_id)]
    visited = set()
    
    while pq:
        current_dist, current_id = heapq.heappop(pq)
        
        if current_id in visited:
            continue
        
        visited.add(current_id)
        
        # Early termination if we reached the target
        if end_vertex_id is not None and current_id == end_vertex_id:
            break
        
        # Skip if we found a better path already
        if current_dist > distances[current_id]:
            continue
        
        for neighbor_id, edge in graph.neighbors(current_id):
            new_dist = current_dist + edge.weight
            
            if new_dist < distances[neighbor_id]:
                distances[neighbor_id] = new_dist
                predecessors[neighbor_id] = current_id
                heapq.heappush(pq, (new_dist, neighbor_id))
    
    return distances, predecessors

def reconstruct_path(predecessors: Dict[int, int], start_id: int, end_id: int) -> List[int]:
    """
    Reconstruct the path from start to end using predecessors dict from Dijkstra
    
    Returns:
        List of vertex IDs forming the path (empty if no path exists)
    """
    if end_id not in predecessors and end_id != start_id:
        return []
    
    path = []
    current = end_id
    
    while current != start_id:
        path.append(current)
        if current not in predecessors:
            return []  # No path exists
        current = predecessors[current]
    
    path.append(start_id)
    path.reverse()
    return path

def heuristic_distance(graph: Graph, v1_id: int, v2_id: int) -> float:
    """
    Euclidean distance heuristic for A* algorithm
    """
    v1 = graph.vertices.get(v1_id)
    v2 = graph.vertices.get(v2_id)
    
    if not v1 or not v2:
        return float('inf')
    
    dx = v1.x - v2.x
    dy = v1.y - v2.y
    return (dx * dx + dy * dy) ** 0.5

def a_star(graph: Graph, start_vertex_id: int, goal_vertex_id: int) -> Tuple[List[int], int]:
    """
    A* pathfinding algorithm - finds optimal path using heuristic
    
    Args:
        graph: The graph to search
        start_vertex_id: Starting vertex ID
        goal_vertex_id: Goal vertex ID
    
    Returns:
        Tuple of (path as list of vertex IDs, total cost)
        Returns ([], inf) if no path exists
    """
    if start_vertex_id not in graph.vertices or goal_vertex_id not in graph.vertices:
        return [], float('inf')
    
    # Priority queue: (f_score, vertex_id)
    # f_score = g_score + heuristic
    open_set = [(0, start_vertex_id)]
    came_from = {}
    
    g_score = {v_id: float('inf') for v_id in graph.vertices}
    g_score[start_vertex_id] = 0
    
    f_score = {v_id: float('inf') for v_id in graph.vertices}
    f_score[start_vertex_id] = heuristic_distance(graph, start_vertex_id, goal_vertex_id)
    
    visited = set()
    
    while open_set:
        current_f, current_id = heapq.heappop(open_set)
        
        if current_id in visited:
            continue
        
        if current_id == goal_vertex_id:
            # Reconstruct path
            path = []
            current = goal_vertex_id
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start_vertex_id)
            path.reverse()
            return path, g_score[goal_vertex_id]
        
        visited.add(current_id)
        
        for neighbor_id, edge in graph.neighbors(current_id):
            tentative_g = g_score[current_id] + edge.weight
            
            if tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = current_id
                g_score[neighbor_id] = tentative_g
                f_score[neighbor_id] = tentative_g + heuristic_distance(graph, neighbor_id, goal_vertex_id)
                heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
    
    return [], float('inf')  # No path found

def find_reachable_vertices(graph: Graph, start_vertex_id: int) -> Set[int]:
    """
    Find all vertices reachable from start vertex
    
    Returns:
        Set of reachable vertex IDs
    """
    if start_vertex_id not in graph.vertices:
        return set()
    
    reachable = {start_vertex_id}
    queue = [start_vertex_id]
    
    while queue:
        current_id = queue.pop(0)
        
        for neighbor_id, edge in graph.neighbors(current_id):
            if neighbor_id not in reachable:
                reachable.add(neighbor_id)
                queue.append(neighbor_id)
    
    return reachable

def find_unreachable_vertices(graph: Graph, start_vertex_id: int) -> Set[int]:
    """
    Find all vertices NOT reachable from start vertex
    
    Returns:
        Set of unreachable vertex IDs
    """
    reachable = find_reachable_vertices(graph, start_vertex_id)
    all_vertices = set(graph.vertices.keys())
    return all_vertices - reachable

def is_path_blocked(graph: Graph, start_id: int, end_id: int) -> bool:
    """
    Check if there is NO path between two vertices
    
    Returns:
        True if path is blocked, False if path exists
    """
    distances, _ = dijkstra(graph, start_id, end_id)
    return distances.get(end_id, float('inf')) == float('inf')

def find_all_paths_dfs(graph: Graph, start_id: int, end_id: int, 
                       max_length: int = 20) -> List[List[int]]:
    """
    Find all paths between two vertices using DFS (limited by max_length)
    
    Args:
        graph: The graph to search
        start_id: Starting vertex ID
        end_id: Goal vertex ID
        max_length: Maximum path length to consider
    
    Returns:
        List of paths, where each path is a list of vertex IDs
    """
    if start_id not in graph.vertices or end_id not in graph.vertices:
        return []
    
    all_paths = []
    
    def dfs(current_id: int, path: List[int], visited: Set[int]):
        if len(path) > max_length:
            return
        
        if current_id == end_id:
            all_paths.append(path.copy())
            return
        
        for neighbor_id, edge in graph.neighbors(current_id):
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                path.append(neighbor_id)
                dfs(neighbor_id, path, visited)
                path.pop()
                visited.remove(neighbor_id)
    
    dfs(start_id, [start_id], {start_id})
    return all_paths

def find_critical_edges(graph: Graph, start_id: int, end_id: int) -> List[int]:
    """
    Find critical edges - edges whose removal would disconnect start from end
    
    Returns:
        List of critical edge IDs
    """
    # First check if path exists
    if is_path_blocked(graph, start_id, end_id):
        return []
    
    critical = []
    
    for edge_id, edge in graph.edges.items():
        if edge.blocked:
            continue
        
        # Temporarily block this edge
        original_state = edge.blocked
        edge.blocked = True
        
        # Check if path still exists
        if is_path_blocked(graph, start_id, end_id):
            critical.append(edge_id)
        
        # Restore edge
        edge.blocked = original_state
    
    return critical

def calculate_path_cost(graph: Graph, path: List[int]) -> int:
    """
    Calculate total cost of a path
    
    Args:
        graph: The graph
        path: List of vertex IDs forming the path
    
    Returns:
        Total cost (sum of edge weights)
    """
    if len(path) < 2:
        return 0
    
    total_cost = 0
    for i in range(len(path) - 1):
        edge = graph.get_edge(path[i], path[i + 1])
        if edge:
            total_cost += edge.weight
        else:
            return float('inf')  # Invalid path
    
    return total_cost

# ============================================
# COMBAT-SPECIFIC ALGORITHMS
# ============================================

def bfs_combat_distance(graph: Graph, start_id: int, end_id: int) -> int:
    """
    Calculate shortest distance (in edges) between two positions in combat graph
    Optimized for small combat graphs (5-7 nodes)
    
    Args:
        graph: Combat graph
        start_id: Starting position ID
        end_id: Target position ID
    
    Returns:
        Distance in edges, or float('inf') if unreachable
    """
    if start_id == end_id:
        return 0
    
    if start_id not in graph.vertices or end_id not in graph.vertices:
        return float('inf')
    
    distances = bfs(graph, start_id)
    return distances.get(end_id, float('inf'))

def dijkstra_combat_path(graph: Graph, start_id: int, end_id: int) -> Tuple[List[int], int]:
    """
    Find shortest path in combat graph considering edge weights (movement cost)
    
    Args:
        graph: Combat graph
        start_id: Starting position ID
        end_id: Target position ID
    
    Returns:
        Tuple of (path as list of vertex IDs, total cost)
        Returns ([], inf) if no path exists
    """
    if start_id not in graph.vertices or end_id not in graph.vertices:
        return [], float('inf')
    
    if start_id == end_id:
        return [start_id], 0
    
    distances, predecessors = dijkstra(graph, start_id, end_id)
    
    if distances.get(end_id, float('inf')) == float('inf'):
        return [], float('inf')
    
    path = reconstruct_path(predecessors, start_id, end_id)
    cost = distances[end_id]
    
    return path, cost

def get_positions_at_distance(graph: Graph, center_id: int, distance: int, 
                              max_distance: Optional[int] = None) -> List[int]:
    """
    Get all positions at exactly 'distance' edges from center
    Useful for determining attack range in combat
    
    Args:
        graph: Combat graph
        center_id: Center position ID
        distance: Exact distance to find
        max_distance: Maximum distance to search (optimization)
    
    Returns:
        List of vertex IDs at exact distance
    """
    if center_id not in graph.vertices:
        return []
    
    search_depth = max_distance if max_distance else distance
    distances = bfs(graph, center_id, max_depth=search_depth)
    
    return [v_id for v_id, dist in distances.items() if dist == distance]

def get_positions_within_range(graph: Graph, center_id: int, max_distance: int) -> List[int]:
    """
    Get all positions within max_distance edges from center
    Useful for area-of-effect abilities in combat
    
    Args:
        graph: Combat graph
        center_id: Center position ID
        max_distance: Maximum distance (inclusive)
    
    Returns:
        List of vertex IDs within range (including center)
    """
    if center_id not in graph.vertices:
        return []
    
    distances = bfs(graph, center_id, max_depth=max_distance)
    return list(distances.keys())

def is_position_reachable(graph: Graph, start_id: int, end_id: int, 
                         max_cost: int) -> bool:
    """
    Check if a position is reachable within a maximum movement cost
    Used to determine if entity can move to target position this turn
    
    Args:
        graph: Combat graph
        start_id: Starting position ID
        end_id: Target position ID
        max_cost: Maximum movement cost available (e.g., remaining AP)
    
    Returns:
        True if reachable within cost, False otherwise
    """
    if start_id == end_id:
        return True
    
    _, cost = dijkstra_combat_path(graph, start_id, end_id)
    return cost <= max_cost

def find_closest_position(graph: Graph, start_id: int, 
                         target_positions: List[int]) -> Tuple[int, int]:
    """
    Find the closest target position from start
    Useful for AI decision making in combat
    
    Args:
        graph: Combat graph
        start_id: Starting position ID
        target_positions: List of potential target positions
    
    Returns:
        Tuple of (closest_position_id, distance)
        Returns (-1, inf) if no valid targets
    """
    if not target_positions:
        return -1, float('inf')
    
    distances = bfs(graph, start_id)
    
    closest_id = -1
    min_distance = float('inf')
    
    for target_id in target_positions:
        dist = distances.get(target_id, float('inf'))
        if dist < min_distance:
            min_distance = dist
            closest_id = target_id
    
    return closest_id, min_distance

