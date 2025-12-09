from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt

class InventoryDialog(QDialog):
    """Dialog to show player inventory"""
    def __init__(self, player, game_state=None, parent=None):
        super().__init__(parent)
        self.player = player
        self.game_state = game_state
        self.selected_item = None
        self.setWindowTitle(f"🎒 Inventário de {player.name}")
        self.setMinimumSize(400, 500)
        
        # Set dialog stylesheet for light text
        self.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 5px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        lbl_title = QLabel(f"Itens de {self.player.name}")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_selected)
        layout.addWidget(self.list_widget)
        
        # Item details label
        self.lbl_details = QLabel("Selecione um item para ver detalhes")
        self.lbl_details.setWordWrap(True)
        self.lbl_details.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.lbl_details)
        
        # Populate
        self.populate_items()
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        self.btn_use = QPushButton("✨ Utilizar Item")
        self.btn_use.setEnabled(False)
        self.btn_use.clicked.connect(self.use_item)
        btn_layout.addWidget(self.btn_use)
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def populate_items(self):
        """Populate the list with items"""
        self.list_widget.clear()
        self.items_data = []  # Store actual item data
        
        if not self.player.inventory:
            self.list_widget.addItem("Inventário vazio")
        else:
            # Group and count items
            item_groups = {}
            
            # Process item objects (new format)
            if "items" in self.player.inventory:
                for item in self.player.inventory["items"]:
                    if isinstance(item, dict):
                        item_name = item.get("name", "Item desconhecido")
                        if item_name not in item_groups:
                            item_groups[item_name] = {"count": 0, "item": item}
                        item_groups[item_name]["count"] += 1
            
            # Process legacy string-based items
            for key, value in self.player.inventory.items():
                if key != "items" and isinstance(value, int):
                    if key not in item_groups:
                        item_groups[key] = {"count": value, "item": {"name": key, "type": "legacy"}}
            
            # Display items
            if not item_groups:
                self.list_widget.addItem("Inventário vazio")
            else:
                for item_name, data in sorted(item_groups.items()):
                    list_item = QListWidgetItem(f"{data['count']}x {item_name}")
                    self.list_widget.addItem(list_item)
                    self.items_data.append(data["item"])
    
    def on_item_selected(self, item):
        """Handle item selection"""
        if item.text() == "Inventário vazio":
            return
        
        # Get selected item index
        index = self.list_widget.row(item)
        if index >= 0 and index < len(self.items_data):
            self.selected_item = self.items_data[index]
            self.btn_use.setEnabled(True)
            
            # Show item details
            item_name = self.selected_item.get("name", "Desconhecido")
            item_type = self.selected_item.get("type", "Desconhecido")
            
            details = f"📦 {item_name}\n"
            
            # Add type-specific details
            if "Poção de Cura" in item_name:
                details += "💚 Restaura HP\n"
                details += f"Cura: {self.selected_item.get('heal', 30)} HP"
            elif "Poção de Stamina" in item_name:
                details += "⚡ Restaura Stamina\n"
                details += f"Restaura: {self.selected_item.get('restore', 40)} stamina"
            elif "Escudo" in item_name:
                details += "🛡️ Equipamento de Defesa\n"
                details += f"Defesa: +{self.selected_item.get('defense', 5)}"
            else:
                details += f"Tipo: {item_type}"
            
            self.lbl_details.setText(details)
    
    def use_item(self):
        """Use the selected item"""
        if not self.selected_item:
            return
        
        item_name = self.selected_item.get("name", "")
        item_id = self.selected_item.get("id", "")
        
        # Handle different item types
        if "Poção de Cura" in item_name:
            self.use_health_potion()
        elif "Poção de Stamina" in item_name:
            self.use_stamina_potion()
        elif "escudo" in item_id.lower() or "Escudo" in item_name:
            self.equip_shield()
        else:
            self._show_message("Item não utilizável", 
                              "Este item não pode ser usado diretamente.")
    
    def use_health_potion(self):
        """Use health potion"""
        if self.player.hp >= self.player.max_hp:
            self._show_message("HP Completo", "Seu HP já está no máximo!")
            return
        
        heal_amount = self.selected_item.get("heal", 30)
        old_hp = self.player.hp
        self.player.hp = min(self.player.max_hp, self.player.hp + heal_amount)
        actual_heal = self.player.hp - old_hp
        
        # Remove item from inventory
        self.remove_item_from_inventory(self.selected_item)
        
        if self.game_state:
            self.game_state.log(f"💚 {self.player.name} usou Poção de Cura e restaurou {actual_heal} HP!")
        
        self._show_message("Item Usado", 
                          f"Você restaurou {actual_heal} HP!\nHP: {self.player.hp}/{self.player.max_hp}")
        
        # Refresh inventory display
        self.populate_items()
        self.selected_item = None
        self.btn_use.setEnabled(False)
        self.lbl_details.setText("Selecione um item para ver detalhes")
    
    def use_stamina_potion(self):
        """Use stamina potion"""
        if self.player.stamina >= self.player.max_stamina:
            self._show_message("Stamina Completa", "Sua stamina já está no máximo!")
            return
        
        restore_amount = self.selected_item.get("restore", 40)
        old_stamina = self.player.stamina
        self.player.stamina = min(self.player.max_stamina, self.player.stamina + restore_amount)
        actual_restore = int(self.player.stamina - old_stamina)
        
        # Remove item from inventory
        self.remove_item_from_inventory(self.selected_item)
        
        if self.game_state:
            self.game_state.log(f"⚡ {self.player.name} usou Poção de Stamina e restaurou {actual_restore} stamina!")
        
        self._show_message("Item Usado", 
                          f"Você restaurou {actual_restore} stamina!\nStamina: {int(self.player.stamina)}/{self.player.max_stamina}")
        
        # Refresh inventory display
        self.populate_items()
        self.selected_item = None
        self.btn_use.setEnabled(False)
        self.lbl_details.setText("Selecione um item para ver detalhes")
    
    def equip_shield(self):
        """Equip a shield (permanently adds defense)"""
        defense_bonus = self.selected_item.get("defense", 5)
        
        # Apply permanent defense boost
        self.player.defense += defense_bonus
        
        # Remove from consumable items
        self.remove_item_from_inventory(self.selected_item)
        
        if self.game_state:
            self.game_state.log(f"🛡️ {self.player.name} equipou {self.selected_item.get('name')} (+{defense_bonus} defesa permanente!)")
        
        self._show_message("Escudo Equipado", 
                          f"{self.selected_item.get('name')} equipado!\nDefesa: {self.player.defense} (+{defense_bonus})")
        
        # Refresh inventory display
        self.populate_items()
        self.selected_item = None
        self.btn_use.setEnabled(False)
        self.lbl_details.setText("Selecione um item para ver detalhes")
    
    def _show_message(self, title, message):
        """Show a styled message box with white text"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        
        # Apply stylesheet for white text
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2b2b2b;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 12px;
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
    
    def remove_item_from_inventory(self, item):
        """Remove one instance of an item from inventory"""
        if "items" in self.player.inventory:
            for i, inv_item in enumerate(self.player.inventory["items"]):
                if isinstance(inv_item, dict) and inv_item.get("name") == item.get("name"):
                    self.player.inventory["items"].pop(i)
                    return
