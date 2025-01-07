import re
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QPen, QCursor, QPixmap, QFont, QKeySequence
import pytesseract
from PIL import ImageGrab
import sys
from overlay import RectangleOverlay

class Item:
    def __init__(self, name, physical_damage=[22, 55], cold_damage=None, lightning_damage=None, chaos_damage=None, fire_damage=None, elemental_damage=None, critical_hit_chance=None, attacks_per_second=None, item_level=None, quality=None):
        self.name = name
        self.physical_damage_current = physical_damage  # Current physical damage (after quality)
        self.cold_damage = cold_damage
        self.lightning_damage = lightning_damage
        self.chaos_damage = chaos_damage
        self.fire_damage = fire_damage
        self.elemental_damage = elemental_damage
        self.critical_hit_chance = critical_hit_chance
        self.attacks_per_second = attacks_per_second
        self.item_level = item_level
        self.quality = quality  # Added quality attribute
        self.physical_damage_base = self.calculate_base_physical_damage()  # Calculate base physical damage
        self.physical_damage_max_qual = self.calculate_max_quality_damage()  # Max quality damage

    def calculate_base_physical_damage(self):
        """ Calculate base physical damage before applying quality bonus. """
        
        if self.physical_damage_current and self.quality:
            try:
                quality_bonus = float(self.quality)
                # Calculate base physical damage by dividing the current damage by (1 + quality bonus)
                base_damage = [(self.physical_damage_current[0][0] / (1 + quality_bonus / 100), self.physical_damage_current[0][1] / (1 + quality_bonus / 100))]
                return base_damage
            except ValueError:
                # If quality is invalid, return the current physical damage as base
                return self.physical_damage_current
        return self.physical_damage_current

    def calculate_max_quality_damage(self):
        """ Calculate physical damage after applying max quality (20%). """
        
        if self.physical_damage_current:
            # Max quality bonus of 20%
            max_quality_bonus = 20
            physical_damage_max_qual = [(self.physical_damage_base[0][0] * (1 + max_quality_bonus / 100), self.physical_damage_base[0][1] * (1 + max_quality_bonus / 100))]
            return physical_damage_max_qual 
        return self.physical_damage_current


    def calculate_dps(self):
        """ Calculate DPS based on the damage stats and attacks per second. """
        total_damage = 0
        damage_count = 0
        
        # Add up the average damage for each type
        for damage in [self.cold_damage, self.lightning_damage, self.chaos_damage, self.fire_damage, self.elemental_damage]:
            if damage:
                if isinstance(damage[0], tuple) and len(damage[0]) == 2:
                    try:
                        print("Damage:", damage, len(damage))
                        low_damage = float(damage[0][0])
                        high_damage = float(damage[0][1])
                        avg_damage = (low_damage + high_damage) / 2
                        total_damage += avg_damage
                        damage_count += 1
                    except ValueError:
                        continue
                else:
                    try:
                        total_damage += float(damage[0])
                        damage_count += 1
                    except ValueError:
                        continue
        
        if self.physical_damage_current:
            total_damage_current = total_damage + (self.physical_damage_current[0][0] + self.physical_damage_current[0][1]) / 2
        else:
            total_damage_current = total_damage
        
        if self.physical_damage_base:
            total_damage_base = total_damage + (self.physical_damage_base[0][0] + self.physical_damage_base[0][1]) / 2
        else:
            total_damage_base = total_damage
        
        if self.physical_damage_max_qual:
            total_damage_max_qual = total_damage + (self.physical_damage_max_qual[0][0] + self.physical_damage_max_qual[0][1]) / 2
        else:
            total_damage_max_qual = total_damage
    
        if self.attacks_per_second:
            try:
                attacks_per_second = float(self.attacks_per_second)
            except ValueError:
                attacks_per_second = 0
        else:
            attacks_per_second = 0
    
        if damage_count > 0 and attacks_per_second > 0:
            total_damage_base = total_damage_base * attacks_per_second
            total_damage_current = total_damage_current * attacks_per_second
            total_damage_max_qual = total_damage_max_qual * attacks_per_second
            total_damages = [total_damage_current, total_damage_base, total_damage_max_qual]
            return total_damages
    
        return [0, 0, 0]
    
    def __str__(self):
        dps_values = self.calculate_dps()
        return (f"Item: {self.name}, \n"
                f"Physical Damage: {self.physical_damage_current}, "
                f"Physical Damage Base: {self.physical_damage_base}, "
                f"Physical Damage Max Qual: {self.physical_damage_max_qual}, "
                f"Cold Damage: {self.cold_damage}, "
                f"Lightning Damage: {self.lightning_damage}, Chaos Damage: {self.chaos_damage}, Fire Damage: {self.fire_damage}, "
                f"Elemental Damage: {self.elemental_damage}, Critical Hit Chance: {self.critical_hit_chance}, "
                f"Attacks per Second: {self.attacks_per_second}, Item Level: {self.item_level}, Quality: {self.quality}, "
                f"DPS: Current: {dps_values[0]:.2f}, Base: {dps_values[1]:.2f}, Max Qual: {dps_values[2]:.2f}")
   
def main():
    app = QApplication(sys.argv)
    overlay = RectangleOverlay()
    overlay.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
