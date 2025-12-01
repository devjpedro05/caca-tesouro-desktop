from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtCore import Qt, QRectF, QPointF

class BoardView(QGraphicsView):
    def __init__(self, game_state, parent=None):
        super().__init__(parent)
        self.game_state = game_state
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.NoDrag)
        
        # Define objectName para estilização QSS
        self.setObjectName("BoardView")
        
        # Mapping to keep track of items
        self.vertex_items = {} # vertex_id -> QGraphicsEllipseItem
        self.edge_items = {}   # edge_id -> QGraphicsLineItem
        
        self.main_window = None
        
        self.refresh()

    def refresh(self):
        """Draw static map only once or on major events."""
        self.scene.clear()

        # draw grid (static)
        self._draw_grid()

        # draw caves, walls, obstacles (static)
        self._draw_obstacles()

        # dynamic layers created empty now
        self._ensure_dynamic_layers()

        # draw treasure (static)
        self._draw_treasure()

        # initial dynamic draw
        self._refresh_dynamic_layers()


    def _draw_graph(self):
        # Draw edges first so they are behind vertices
        for edge in self.game_state.graph.edges.values():
            v1 = self.game_state.graph.vertices[edge.v1_id]
            v2 = self.game_state.graph.vertices[edge.v2_id]
            
            # Draw tunnel path
            line = QGraphicsLineItem(v1.x, v1.y, v2.x, v2.y)
            
            pen = QPen()
            pen.setWidth(12)
            pen.setCapStyle(Qt.RoundCap)
            if edge.blocked:
                pen.setColor(QColor("#8B4513"))  # Brown for blocked
                pen.setStyle(Qt.DashLine)
            else:
                pen.setColor(QColor("#5a4a3a"))  # Dark stone
                
            line.setPen(pen)
            line.setZValue(0)
            self.scene.addItem(line)
            
            # Inner path
            inner_line = QGraphicsLineItem(v1.x, v1.y, v2.x, v2.y)
            inner_pen = QPen()
            inner_pen.setWidth(8)
            inner_pen.setCapStyle(Qt.RoundCap)
            inner_pen.setColor(QColor("#3a2a1a"))
            inner_line.setPen(inner_pen)
            inner_line.setZValue(0.5)
            self.scene.addItem(inner_line)
            self.edge_items[edge.id] = line
            
            # Draw weight with coin-style background
            mid_x = (v1.x + v2.x) / 2
            mid_y = (v1.y + v2.y) / 2
            
            # Gold coin background for weight
            weight_bg = QGraphicsEllipseItem(mid_x - 18, mid_y - 18, 36, 36)
            from PySide6.QtGui import QRadialGradient
            coin_gradient = QRadialGradient(mid_x, mid_y - 5, 20)
            coin_gradient.setColorAt(0, QColor("#FFD700"))
            coin_gradient.setColorAt(0.6, QColor("#DAA520"))
            coin_gradient.setColorAt(1, QColor("#B8860B"))
            weight_bg.setBrush(QBrush(coin_gradient))
            weight_bg.setPen(QPen(QColor("#8B6914"), 2))
            weight_bg.setZValue(1)
            self.scene.addItem(weight_bg)
            
            text = QGraphicsTextItem(str(edge.weight))
            text.setFont(QFont("Georgia", 12, QFont.Bold))
            text.setDefaultTextColor(QColor("#4a2a0a"))
            text.setPos(mid_x - text.boundingRect().width()/2, mid_y - text.boundingRect().height()/2)
            text.setZValue(2)
            self.scene.addItem(text)

        # Draw vertices with stone room styling
        for v in self.game_state.graph.vertices.values():
            radius = 30
            
            # Outer stone border
            outer = QGraphicsEllipseItem(v.x - radius - 4, v.y - radius - 4, (radius+4)*2, (radius+4)*2)
            from PySide6.QtGui import QRadialGradient
            border_gradient = QRadialGradient(v.x, v.y, radius + 4)
            border_gradient.setColorAt(0, QColor("#5a4a3a"))
            border_gradient.setColorAt(1, QColor("#3a2a1a"))
            outer.setBrush(QBrush(border_gradient))
            outer.setPen(QPen(Qt.NoPen))
            outer.setZValue(2)
            self.scene.addItem(outer)
            
            # Inner room
            ellipse = QGraphicsEllipseItem(v.x - radius, v.y - radius, radius*2, radius*2)
            
            # Stone room gradient
            gradient = QRadialGradient(v.x, v.y - radius/3, radius * 1.2)
            gradient.setColorAt(0, QColor("#4a4035"))
            gradient.setColorAt(0.7, QColor("#2a2015"))
            gradient.setColorAt(1, QColor("#1a1410"))
            
            ellipse.setBrush(QBrush(gradient))
            ellipse.setPen(QPen(QColor("#6a5a4a"), 2))
            ellipse.setZValue(3)
            self.scene.addItem(ellipse)
            self.vertex_items[v.id] = ellipse
            
            # Name with parchment background
            name_text = QGraphicsTextItem(v.name)
            name_text.setFont(QFont("Georgia", 9, QFont.Bold))
            name_text.setDefaultTextColor(QColor("#2C1810"))
            name_text.setPos(v.x - name_text.boundingRect().width()/2, v.y + radius + 10)
            
            # Parchment-style background for name
            name_bg = self.scene.addRect(
                name_text.sceneBoundingRect().adjusted(-5, -2, 5, 2),
                QPen(QColor("#8B7355"), 1),
                QBrush(QColor("#F4E4C1"))
            )
            name_bg.setZValue(3)
            name_text.setZValue(4)
            self.scene.addItem(name_text)

    def _draw_players(self):
        import os
        from .frame_animated_sprite import FrameAnimatedSprite
        
        print(f"🎨 Drawing {len(self.game_state.players)} players")
        
        offset_map = {} # vertex_id -> count of players there
        
        for player in self.game_state.players:
            print(f"👤 Processing player: {player.name} (color: {player.color}, vertex: {player.current_vertex_id})")
            
            v_id = player.current_vertex_id
            v = self.game_state.graph.vertices.get(v_id)
            if not v:
                print(f"⚠️ Vertex {v_id} not found for player {player.name}")
                continue
                
            count = offset_map.get(v_id, 0)
            offset_map[v_id] = count + 1
            
            # Offset players slightly if they are on the same vertex
            offset_x = (count * 45) - 22
            offset_y = (count * 45) - 22
            
            # ⭐ Load animated sprite from frames directory
            frames_dir = None
            if player.color == "#FF0000":  # Red player
                frames_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "themes", "Player_Vermelho")
                print(f"🔴 Loading red frames from: {frames_dir}")
            elif player.color == "#0000FF":  # Blue player
                frames_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "themes", "Player_Azul")
                print(f"🔵 Loading blue frames from: {frames_dir}")
            
            if frames_dir and os.path.exists(frames_dir):
                # Create animated sprite from individual frames
                sprite = FrameAnimatedSprite(frames_dir)
                
                # Center sprite properly
                # Frames are scaled 0.08x, adjust positioning
                sprite.setPos(v.x + offset_x - 20, v.y + offset_y - 25)
                sprite.setZValue(5)
                
                # Add shadow (smaller to match sprite)
                shadow = QGraphicsEllipseItem(v.x + offset_x - 12, v.y + offset_y + 8, 24, 8)
                shadow.setBrush(QBrush(QColor(0, 0, 0, 80)))
                shadow.setPen(QPen(Qt.NoPen))
                shadow.setZValue(4)
                self.scene.addItem(shadow)
                
                self.scene.addItem(sprite)
                print(f"✅ Added sprite at ({v.x + offset_x}, {v.y + offset_y})")
            else:
                print(f"⚠️ Frames directory not found, using fallback circle")
                # Fallback to simple circle if frames not found
                radius = 12
                from PySide6.QtGui import QRadialGradient
                p_item = QGraphicsEllipseItem(v.x + offset_x - radius, v.y + offset_y - radius, radius*2, radius*2)
                
                gradient = QRadialGradient(v.x + offset_x, v.y + offset_y - radius/2, radius * 1.5)
                color = QColor(player.color)
                gradient.setColorAt(0, color.lighter(130))
                gradient.setColorAt(1, color)
                
                p_item.setBrush(QBrush(gradient))
                p_item.setPen(QPen(QColor("#2C3E50"), 2))
                p_item.setZValue(5)
                self.scene.addItem(p_item)


    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.isAccepted():
            return
            
        # Get items under mouse
        pos = self.mapToScene(event.pos())
        items = self.scene.items(pos)
        
        if not items:
            return
            
        # Check if it's a vertex or edge
        target_edge_id = None
        
        # Priority: Vertex > Edge
        # First check for vertices
        for item in items:
            for v_id, ellipse in self.vertex_items.items():
                if item == ellipse:
                    # Check if this vertex is a neighbor of current player
                    p = self.game_state.current_player
                    if not p:
                        break
                        
                    # Find edge connecting current pos to this vertex
                    edge = self.game_state.graph.get_edge(p.current_vertex_id, v_id)
                    if edge:
                        target_edge_id = edge.id
                    break
            if target_edge_id is not None:
                break
        
        # If no vertex found, check for edges
        if target_edge_id is None:
            for item in items:
                for e_id, line in self.edge_items.items():
                    if item == line:
                        target_edge_id = e_id
                        break
                if target_edge_id is not None:
                    break
        
        # Try to move
        if target_edge_id is not None:
            p = self.game_state.current_player
            if p:
                self.game_state.move_player(p.id, target_edge_id)
                # Always refresh to show logs (success or failure)
                if self.main_window:
                    self.main_window.refresh_all()
                else:
                    self.refresh()
        else:
            # If we clicked a vertex but found no edge, it means it's not a neighbor
            # Let's check if we clicked a vertex at all to give feedback
            for item in items:
                for v_id, ellipse in self.vertex_items.items():
                    if item == ellipse:
                        self.game_state.log("Movimento inválido: Você só pode mover para vértices vizinhos.")
                        if self.main_window:
                            self.main_window.refresh_all()
                        return

    def _draw_treasure(self):
        t_id = self.game_state.treasure_vertex_id
        if t_id is not None:
            v = self.game_state.graph.vertices.get(t_id)
            if v:
                # Glow effect background
                glow = QGraphicsEllipseItem(v.x - 35, v.y - 55, 70, 70)
                from PySide6.QtGui import QRadialGradient
                gradient = QRadialGradient(v.x, v.y - 20, 40)
                gradient.setColorAt(0, QColor(255, 215, 0, 100))
                gradient.setColorAt(1, QColor(255, 215, 0, 0))
                glow.setBrush(QBrush(gradient))
                glow.setPen(QPen(Qt.NoPen))
                glow.setZValue(2)
                self.scene.addItem(glow)
                
                # Treasure icon
                text = QGraphicsTextItem("💰")
                font = QFont("Segoe UI Emoji", 28)
                text.setFont(font)
                text.setPos(v.x - text.boundingRect().width()/2, v.y - 45)
                text.setZValue(4)
                self.scene.addItem(text)

    def _ensure_dynamic_layers(self):
        if hasattr(self, "_dyn_players"):
            return

        self._dyn_players = self.scene.createItemGroup([])
        self._dyn_monsters = self.scene.createItemGroup([])
        self._dyn_fog = self.scene.createItemGroup([])

