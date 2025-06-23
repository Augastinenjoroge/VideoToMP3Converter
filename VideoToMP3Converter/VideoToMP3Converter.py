from tkinter import Tk
from ui.frames import VideoToMP3Converter
import math

if __name__ == "__main__":
    root = Tk()
    app = VideoToMP3Converter(root)
    root.mainloop()