from tkinter import Entry, ttk


class ThemeManager:
    def __init__(self, app):
        self.app = app
        self.dark_mode = False
        self.theme_colors = {
            "light": {
                "bg": "#f0f0f0",
                "fg": "#333333",
                "button": "#4CAF50",
                "activebutton": "#45a049",
                "text": "#000000",
                "frame": "#ffffff",
                "highlight": "#e0e0e0",
                "listbox": "#ffffff",
                "listbox_fg": "#000000",
                "entry_bg": "#ffffff",
                "entry_fg": "#000000",
                "disabled": "#cccccc"
            },
            "dark": {
                "bg": "#2d2d2d",
                "fg": "#e0e0e0",
                "button": "#5C6BC0",
                "activebutton": "#3949AB",
                "text": "#ffffff",
                "frame": "#3d3d3d",
                "highlight": "#4d4d4d",
                "listbox": "#3d3d3d",
                "listbox_fg": "#ffffff",
                "entry_bg": "#4d4d4d",
                "entry_fg": "#ffffff",
                "disabled": "#555555"
            }
        }

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.app.header.theme_btn.config(
            text="☀️ Light Mode" if self.dark_mode else "🌙 Dark Mode"
        )
        self.update_theme()

    def update_theme(self):
        colors = self.theme_colors["dark"] if self.dark_mode else self.theme_colors["light"]
        
        # Update root window
        self.app.root.config(bg=colors["bg"])
        
        # Update all widgets
        widgets = [
            self.app.header.frame, self.app.header.title_label, self.app.header.theme_btn,
            self.app.status_frame, self.app.status_label, self.app.progress_percent,
            self.app.convert_btn, self.app.cancel_btn, self.app.tab_convert,
            self.app.tab_metadata, self.app.tab_checklist
        ]
        
        for widget in widgets:
            if widget:
                try:
                    widget.config(
                        bg=colors["bg"],
                        fg=colors["fg"],
                        highlightbackground=colors["highlight"],
                        highlightcolor=colors["highlight"]
                    )
                except:
                    pass
        
        # Special widget updates
        self.app.video_listbox.config(
            bg=colors["listbox"],
            fg=colors["listbox_fg"],
            selectbackground=colors["button"],
            selectforeground=colors["text"]
        )
        
        # Update button colors
        self.app.header.theme_btn.config(
            bg=colors["button"],
            activebackground=colors["activebutton"],
            fg=colors["text"]
        )
        
        self.app.convert_btn.config(
            bg=colors["button"],
            activebackground=colors["activebutton"],
            fg=colors["text"]
        )
        
        self.app.cancel_btn.config(
            bg="#f44336" if self.dark_mode else "#ff6666",
            activebackground="#d32f2f" if self.dark_mode else "#ff4444",
            fg=colors["text"]
        )
        
        # Update all entry fields
        for child in self.app.tab_convert.winfo_children() + self.app.tab_metadata.winfo_children() + self.app.tab_checklist.winfo_children():
            if isinstance(child, Entry):
                child.config(
                    bg=colors["entry_bg"],
                    fg=colors["entry_fg"],
                    insertbackground=colors["fg"]
                )
        
        # Update notebook style
        self.app.style = ttk.Style()
        self.app.style.configure("TNotebook", background=colors["bg"])
        self.app.style.configure("TNotebook.Tab", 
                               background=colors["bg"],
                               foreground=colors["fg"],
                               lightcolor=colors["bg"],
                               bordercolor=colors["bg"])
        
        # Update cover art label
        if hasattr(self.app, 'cover_img'):
            self.app.cover_art_label.config(bg=colors["frame"])