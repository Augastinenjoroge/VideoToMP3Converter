import math

class AnimationManager:
    def __init__(self, app):
        self.app = app
        self.active_animations = []
        self.pulse_phase = 0
        self.animation_interval = 20  # ms
        
    def start_animations(self):
        self.animate_ui()
        
    def animate_ui(self):
        # Update pulse animations
        self.pulse_phase = (self.pulse_phase + 0.05) % (2 * 3.14159)
        pulse_value = (1 + 0.1 * (1 + math.sin(self.pulse_phase))) / 2  # 0.9 to 1.1
        
        for widget, base_color in self.active_animations:
            if widget.winfo_exists():
                r, g, b = int(base_color[1:3], 16), int(base_color[3:5], 16), int(base_color[5:7], 16)
                r = min(255, int(r * pulse_value))
                g = min(255, int(g * pulse_value))
                b = min(255, int(b * pulse_value))
                color = f"#{r:02x}{g:02x}{b:02x}"
                widget.config(bg=color)
        
        self.app.root.after(self.animation_interval, self.animate_ui)
        
    def add_animation(self, widget, base_color):
        self.active_animations.append((widget, base_color))
        
    def remove_animation(self, widget):
        self.active_animations = [anim for anim in self.active_animations if anim[0] != widget]