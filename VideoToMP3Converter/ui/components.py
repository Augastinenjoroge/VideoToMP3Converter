from tkinter import LEFT, RIGHT, ttk, Frame, Label, Button, Entry, Listbox, StringVar, BooleanVar
from PIL import Image, ImageTk, ImageOps
import os

from ui.frames import FLAT

class Header:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.logo = None
        self.title_label = None
        self.theme_btn = None
        
    def create(self, title, theme_callback):
        try:
            logo_img = Image.open("assets/icon.png").resize((50, 50)) if os.path.exists("assets/icon.png") else None
            self.logo = ImageTk.PhotoImage(logo_img) if logo_img else None
            if self.logo:
                ttk.Label(self.frame, image=self.logo).pack(side=LEFT, padx=5)
        except:
            self.logo = None
        
        self.title_label = Label(
            self.frame, 
            text=title,
            font=("Helvetica", 16, "bold")
        )
        self.title_label.pack(side=LEFT, padx=10, expand=True)
        
        self.theme_btn = Button(
            self.frame, 
            text="🌙 Dark Mode", 
            command=theme_callback,
            relief=FLAT,
            font=("Helvetica", 10),
            borderwidth=0
        )
        self.theme_btn.pack(side=RIGHT)
        
        return self.frame