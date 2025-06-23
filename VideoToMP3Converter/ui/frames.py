from re import X
from tkinter import BOTH, END, EW, HORIZONTAL, MULTIPLE, VERTICAL, W, Y, Canvas, Checkbutton, IntVar, LabelFrame, OptionMenu, Radiobutton, Scrollbar, Text, Toplevel, ttk, Frame, Label, Button, Entry, Listbox, StringVar, BooleanVar, DISABLED, NORMAL, RAISED, FLAT, WORD
from tkinter import messagebox, filedialog
from ui.components import LEFT, RIGHT, Header
from ui.theme import ThemeManager
from ui.animations import AnimationManager
from core.converter import VideoConverter
from core.metadata import MetadataHandler
from core.utils import get_default_output_path, get_current_year
from PIL import Image, ImageTk, ImageOps
import os
import math

class VideoToMP3Converter:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.theme = ThemeManager(self)
        self.animations = AnimationManager(self)
        self.converter = VideoConverter(self)
        self.metadata = MetadataHandler(self)
        self.setup_ui()
        self.setup_bindings()
        self.animations.start_animations()

    def setup_window(self):
        self.root.title("🎵 Ultimate Video to MP3 Converter Pro")
        self.root.geometry("950x750")
        self.root.minsize(850, 650)
        self.root.configure(bg="#f0f0f0")

        # Window focus management
        self.root.attributes("-topmost", False)  # Don't force to top initially
        self.root.lift()  # Bring to front but don't stay on top
        self.root.focus_force()  # Ensure window gets focus

    def setup_variables(self):
        self.video_paths = []
        self.output_path = StringVar(value=get_default_output_path())
        self.quality_var = StringVar(value="320k")
        self.conversion_active = False
        self.currently_converting = False
        
        # Metadata variables
        self.title_var = StringVar()
        self.artist_var = StringVar()
        self.album_var = StringVar()
        self.year_var = StringVar(value=get_current_year())
        self.genre_var = StringVar(value="")
        self.cover_art_path = StringVar()
        
        # Checklist variables
        self.checklist_vars = [
        BooleanVar(value=False),  # Files added
        BooleanVar(value=True),   # Output folder (checked)
        BooleanVar(value=True),   # Quality selected (checked)
        BooleanVar(value=False),  # Metadata
        BooleanVar(value=False)   # Disk space
    ]

    def setup_ui(self):
        self.create_main_container()
        self.create_header()
        self.create_notebook()
        self.create_conversion_tab()
        self.create_metadata_tab()
        self.create_pre_conversion_checklist()
        self.create_status_bar()
        # Auto-check the path since we set a default
        self.checklist_vars[1].set(True)
        self.update_checklist_status()
    
        self.theme.update_theme()

    def create_main_container(self):
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def create_header(self):
        self.header = Header(self.main_container)
        self.header_frame = self.header.create(
            "🎵 Ultimate Video to MP3 Converter Pro",
            self.theme.toggle_theme
        )
        self.header_frame.pack(fill="x", pady=(0, 10))

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=BOTH, expand=True)
        
        self.tab_convert = Frame(self.notebook)
        self.tab_metadata = Frame(self.notebook)
        self.tab_checklist = Frame(self.notebook)
        
        self.notebook.add(self.tab_convert, text="🔧 Conversion")
        self.notebook.add(self.tab_metadata, text="📝 Metadata")
        self.notebook.add(self.tab_checklist, text="✅ Checklist")

    def create_conversion_tab(self):
        # Video Selection Frame
        video_frame = LabelFrame(self.tab_convert, text="📁 Video Files", padx=10, pady=10)
        video_frame.pack(fill=BOTH, pady=5, padx=5, expand=True)
        
        # Video Listbox with Scrollbar
        self.video_listbox = Listbox(video_frame, height=8, selectmode=MULTIPLE, font=("Helvetica", 10))
        self.video_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(video_frame, orient=VERTICAL, command=self.video_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        
        # Video Buttons Frame
        video_buttons_frame = Frame(video_frame)
        video_buttons_frame.pack(fill="x", pady=5)
        
        Button(video_buttons_frame, text="➕ Add Files", command=self.add_videos).pack(side=LEFT, padx=2)
        Button(video_buttons_frame, text="📂 Add Folder", command=self.add_folder).pack(side=LEFT, padx=2)
        Button(video_buttons_frame, text="🗑️ Clear List", command=self.clear_list).pack(side=LEFT, padx=2)
        
        # Output Settings Frame
        output_frame = LabelFrame(self.tab_convert, text="⚙️ Output Settings", padx=10, pady=10)
        output_frame.pack(fill=BOTH, pady=5, padx=5)
        
        Label(output_frame, text="📂 Output Folder:").grid(row=0, column=0, sticky=W, pady=2)
        Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, padx=5)
        Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=2)
        
        # Quality Settings
        Label(output_frame, text="🎚️ Audio Quality:").grid(row=1, column=0, sticky=W, pady=10)
        
        quality_frame = Frame(output_frame)
        quality_frame.grid(row=1, column=1, columnspan=2, sticky=W)
        
        qualities = [
            ("🔈 Low (128 kbps)", "128k"),
            ("🔉 Medium (192 kbps)", "192k"),
            ("🔊 High (256 kbps)", "256k"),
            ("🔥 Very High (320 kbps)", "320k")
        ]
        
        for text, quality in qualities:
            rb = Radiobutton(
                quality_frame, 
                text=text, 
                variable=self.quality_var, 
                value=quality,
                command=lambda: self.checklist_vars[2].set(True) or self.update_checklist_status()
            )
            rb.pack(side=LEFT, padx=5)
            if quality == "320k":  # Select default
                rb.invoke()
        
        # Convert Button
        self.convert_btn = Button(
            self.tab_convert, 
            text="▶️ Convert to MP3", 
            command=self.start_conversion,
            relief=RAISED,
            font=("Helvetica", 12, "bold"),
            borderwidth=2
        )
        self.convert_btn.pack(pady=10)

        preset_frame = LabelFrame(self.tab_convert, text="⚡ Quick Presets", padx=10, pady=10)
        preset_frame.pack(fill="x", pady=5, padx=5)
    
        presets = [
            ("Podcast", "192k", os.path.expanduser("~/Downloads")),
            ("Music", "320k", os.path.expanduser("~/Downloads")),
            ("Voice Memo", "128k", os.path.expanduser("~/Downloads"))
        ]
           
    
        for name, quality, path in presets:
            btn = Button(
                preset_frame,
                text=name,
                command=lambda q=quality, p=path: self.load_preset(q, p),
                width=10
            )
            btn.pack(side=LEFT, padx=5)

    def load_preset(self, quality, path):
        self.quality_var.set(quality)
        self.output_path.set(path)
        


    def create_metadata_tab(self):
        # Metadata Editor Frame
        meta_frame = LabelFrame(self.tab_metadata, text="📝 Edit MP3 Metadata", padx=10, pady=10)
        meta_frame.pack(fill=BOTH, pady=5, padx=5, expand=True)
        
        # Cover Art Section
        Label(meta_frame, text="🖼️ Cover Art:").grid(row=0, column=0, sticky=W, pady=5)
        
        self.cover_art_label = Label(meta_frame, text="No image selected", relief="solid", width=30, height=10)
        self.cover_art_label.grid(row=0, column=1, padx=5, pady=5, rowspan=3)
        
        Button(meta_frame, text="📁 Select Image", command=self.select_cover_art).grid(row=0, column=2, sticky="nw")
        Button(meta_frame, text="❌ Remove", command=self.remove_cover_art).grid(row=1, column=2, sticky="nw")
        
        # Metadata Fields
        fields = [
            ("🎵 Title:", self.title_var),
            ("👤 Artist:", self.artist_var),
            ("💿 Album:", self.album_var),
            ("📅 Year:", self.year_var),
            ("🎶 Genre:", self.genre_var)
        ]
        
        for i, (label_text, var) in enumerate(fields, start=3):
            Label(meta_frame, text=label_text).grid(row=i, column=0, sticky=W, pady=2)
            Entry(meta_frame, textvariable=var).grid(row=i, column=1, columnspan=2, sticky=EW, padx=5, pady=2)
        
        # Presets Frame
        presets_frame = LabelFrame(self.tab_metadata, text="💾 Metadata Presets", padx=10, pady=10)
        presets_frame.pack(fill=BOTH, pady=5, padx=5)
        
        Button(presets_frame, text="🎤 Podcast", command=lambda: self.apply_preset("Podcast")).pack(side=LEFT, padx=5)
        Button(presets_frame, text="🎵 Music", command=lambda: self.apply_preset("Music")).pack(side=LEFT, padx=5)
        Button(presets_frame, text="📚 Audiobook", command=lambda: self.apply_preset("Audiobook")).pack(side=LEFT, padx=5)

    def create_pre_conversion_checklist(self):
        # Checklist Frame
        checklist_frame = LabelFrame(self.tab_checklist, text="✅ Pre-Conversion Checklist", padx=10, pady=10)
        checklist_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Checklist Items
        checklist_items = [
            "1. Added all video files to convert",
            "2. Selected output folder",
            "3. Chosen audio quality",
            "4. Added metadata (optional)",
            "5. Verified enough disk space"
        ]
        
        for i, (item, var) in enumerate(zip(checklist_items, self.checklist_vars)):
            Checkbutton(
                checklist_frame, 
                text=item, 
                variable=var,
                state='normal' if i in [0,3,4] else 'disabled',  # Disable auto-checked items
                command=self.update_checklist_status
            ).pack(anchor=W, pady=2)
        
        # Checklist Status
        self.checklist_status = Label(checklist_frame, text="", font=("Helvetica", 10))
        self.checklist_status.pack(pady=10)

        # Update status immediately
        self.update_checklist_status()
        
        # Quick Actions
        quick_frame = Frame(checklist_frame)
        quick_frame.pack(fill="x", pady=10)
        
        Button(quick_frame, text="📁 Open Output Folder", command=self.open_output_folder).pack(side=LEFT, padx=5)
        Button(quick_frame, text="🧹 Clear All", command=self.clear_all_fields).pack(side=LEFT, padx=5)

    def create_status_bar(self):
        self.status_frame = Frame(self.main_container)
        self.status_frame.pack(fill="x", pady=(5, 0))
    
        # Progress bar with custom style
        self.style = ttk.Style()
        self.style.configure("green.Horizontal.TProgressbar",
                           foreground='green',
                           background='green',
                           thickness=20)
    
        # Progress frame to contain both progress elements
        progress_frame = Frame(self.status_frame)
        progress_frame.pack(side=LEFT, fill='x', expand=True, padx=5)
    
        # Wider progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient=HORIZONTAL,
            mode='determinate',
            style="green.Horizontal.TProgressbar",
            length=400  # Increased length
        )
        self.progress_bar.pack(fill='x', expand=True)
    
        # Progress text showing KB/MB and count
        self.progress_percent = Label(
            progress_frame,
            text="0 KB / 0 KB (0%) | 0/0 files",
            width=30,
            anchor='w'
        )
        self.progress_percent.pack(fill='x', pady=(2, 0))
    
        # Status label for current file
        self.status_label = Label(
            self.status_frame,
            text="Ready",
            font=("Helvetica", 9),
            width=40,
            anchor='w'
        )
        self.status_label.pack(side=LEFT, fill='x', expand=True, padx=5)
    
        # Cancel Button (hidden by default)
        self.cancel_btn = Button(
            self.status_frame, 
            text="✖ Cancel", 
            command=self.cancel_conversion,
            state=DISABLED
        )
        self.cancel_btn.pack(side=RIGHT, padx=5)

    def setup_bindings(self):
        self.root.bind("<Configure>", self.on_window_resize)
        self.video_listbox.bind("<<ListboxSelect>>", self.on_video_select)

    def on_window_resize(self, event):
        if self.currently_converting:
            self.root.attributes("-topmost", True)
        else:
            self.root.attributes("-topmost", False)
            
    def on_video_select(self, event):
        selected = self.video_listbox.curselection()
        if selected:
            video_path = self.video_paths[selected[0]]
            self.title_var.set(os.path.splitext(os.path.basename(video_path))[0])
            
    def update_checklist_status(self):
        # Ensure checklist_status exists before using it
            if not hasattr(self, 'checklist_status'):
                return
            completed = sum(var.get() for var in self.checklist_vars)
            total = len(self.checklist_vars)
            
            if completed == total:
                self.checklist_status.config(text="✓ Ready to convert!", fg="green")
            else:
                self.checklist_status.config(text=f"Completed {completed}/{total} items", fg="orange")
     
    def create_batch_controls(self):
        control_frame = Frame(self.tab_convert)
        control_frame.pack(fill="x", pady=10)
    
        # Parallel processing toggle
        self.parallel_var = BooleanVar(value=True)
        Checkbutton(
            control_frame,
            text="Parallel Processing (faster)",
            variable=self.parallel_var
        ).pack(side=LEFT, padx=10)
    
        # Max concurrent jobs
        self.thread_var = IntVar(value=4)
        OptionMenu(
            control_frame,
            self.thread_var,
            *range(1, 9),
        ).pack(side=LEFT)

    def create_queue_display(self):
        self.queue_canvas = Canvas(self.tab_convert, height=100)
        self.queue_canvas.pack(fill="x", pady=5)
    
        # Visual queue representation
        self.queue_items = []
    
    def update_queue_display(self):
        self.queue_canvas.delete("all")
        item_width = 80
        padding = 10
    
        for i, file in enumerate(self.video_paths):
            x = i * (item_width + padding)
            color = "#4CAF50" if i < self.current_conversion else "#CCCCCC"
        
            self.queue_canvas.create_rectangle(
                x, 20, x+item_width, 80,
                fill=color,
                outline="#333333"
            )
        
            # Display shortened filename
            name = os.path.basename(file)[:8] + "..."
            self.queue_canvas.create_text(
                x+(item_width/2), 50,
                text=name,
                fill="#333333"
            )

    def add_videos(self):
        filetypes = (
            ("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.flv;*.wmv"),
            ("All files", "*.*")
        )
        filenames = filedialog.askopenfilenames(title="Select video files", filetypes=filetypes)
        if filenames:
            for filename in filenames:
                if filename not in self.video_paths:
                    self.video_paths.append(filename)
                    self.video_listbox.insert(END, os.path.basename(filename))
            
            # Update checklist
            if len(self.video_paths) > 0:
                self.checklist_vars[0].set(True)
                self.update_checklist_status()
    
    def add_folder(self):
        foldername = filedialog.askdirectory(title="Select folder with videos")
        if foldername:
            extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            added_files = False
            for root, _, files in os.walk(foldername):
                for file in files:
                    if file.lower().endswith(extensions):
                        full_path = os.path.join(root, file)
                        if full_path not in self.video_paths:
                            self.video_paths.append(full_path)
                            self.video_listbox.insert(END, os.path.basename(file))
                            added_files = True
            
            if added_files:
                self.checklist_vars[0].set(True)
                self.update_checklist_status()
    
    def clear_list(self):
        self.video_paths = []
        self.video_listbox.delete(0, END)
        self.checklist_vars[0].set(False)
        self.update_checklist_status()
    
    def browse_output(self):
        foldername = filedialog.askdirectory(title="Select output folder")
        if foldername:
            self.output_path.set(foldername)
            self.checklist_vars[1].set(True)
            self.update_checklist_status()
    
    def select_cover_art(self):
        filetypes = (("Image files", "*.jpg;*.jpeg;*.png"), ("All files", "*.*"))
        filename = filedialog.askopenfilename(title="Select cover art", filetypes=filetypes)
        if filename:
            self.cover_art_path.set(filename)
            try:
                img = Image.open(filename)
                # Create thumbnail with border
                img.thumbnail((200, 200))
                img_with_border = ImageOps.expand(img, border=2, fill='#888888')
                self.cover_img = ImageTk.PhotoImage(img_with_border)
                self.cover_art_label.config(image=self.cover_img, text="")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.cover_art_label.config(text="Invalid image")
            
            self.checklist_vars[3].set(True)
            self.update_checklist_status()
    
    def remove_cover_art(self):
        self.cover_art_path.set("")
        self.cover_art_label.config(image=None, text="No image selected")
    
    def apply_preset(self, preset_type):
        if preset_type == "Podcast":
            self.genre_var.set("Podcast")
            self.title_var.set("My Podcast Episode")
            self.artist_var.set("Podcast Host")
        elif preset_type == "Music":
            self.genre_var.set("Pop")
            self.title_var.set("My Song")
            self.artist_var.set("Artist Name")
        elif preset_type == "Audiobook":
            self.genre_var.set("Audiobook")
            self.title_var.set("Book Title")
            self.artist_var.set("Author Name")
        
        self.checklist_vars[3].set(True)
        self.update_checklist_status()
    
    def open_output_folder(self):
        output_path = self.output_path.get()
        if os.path.exists(output_path):
            os.startfile(output_path)
    
    def clear_all_fields(self):
        self.clear_list()
        self.output_path.set(get_default_output_path())
        self.quality_var.set("320k")
        self.title_var.set("")
        self.artist_var.set("")
        self.album_var.set("")
        self.year_var.set(get_current_year())
        self.genre_var.set("Pop")
        self.remove_cover_art()
        
        for var in self.checklist_vars:
            var.set(False)
        self.update_checklist_status()
    
    def start_conversion(self):
        if not self.video_paths:
            messagebox.showerror("Error", "Please add at least one video file")
            return
    
        if not self.output_path.get():
            messagebox.showerror("Error", "Please select an output folder")
            return
    
        # Reset UI
        self.progress_bar['value'] = 0
        self.progress_percent.config(text="0%")
        self.status_label.config(text="Starting conversion...")
    
        # Show converting popup (will center itself)
        self.show_converting_popup()
    
        # Start conversion
        self.conversion_active = True
        self.currently_converting = True
        self.converter.start_conversion()
    
    def cancel_conversion(self):
        self.conversion_active = False
        self.status_label.config(text="Conversion cancelled")
        self.progress_percent.config(text="Cancelled")
        self.cancel_btn.config(state=DISABLED)
        self.animations.remove_animation(self.convert_btn)
        self.currently_converting = False
        self.root.attributes("-topmost", False)
    
    def initialize_progress(self, total_files):
        """Initialize progress with total file count"""
        self.total_files = total_files
        self.progress_bar['value'] = 0
        self.progress_text = "0 KB / ? KB (0%) | 0/{} files".format(total_files)
        self.progress_percent.config(text=self.progress_text)

    def update_progress(self, current_kb, total_kb, message=""):
        """Update progress with current and total MP3 KB"""
        if total_kb > 0:
            progress_pct = (current_kb / total_kb) * 100
            size_text = "{} / {} KB ({:.1f}%)".format(
                int(current_kb), int(total_kb), progress_pct
            )
        else:
            size_text = "{} KB / ? KB".format(int(current_kb))
    
        # Get current file count from the status label text
        status_text = self.status_label.cget("text")
        current_count = 0
        if "(" in status_text and "/" in status_text:
            try:
                current_count = int(status_text.split("(")[1].split("/")[0])
            except:
                pass
    
        self.progress_text = "{} | {}/{} files".format(
            size_text, current_count, self.total_files
        )
        self.progress_percent.config(text=self.progress_text)
    
        if message:
            self.status_label.config(text=message)
        self.progress_bar['value'] = current_kb
        if total_kb > 0:
            self.progress_bar['maximum'] = total_kb

    def update_file_progress(self, filename, current_count, total_count):
        """Update current file being processed"""
        self.status_label.config(
            text=f"Processing {filename} ({current_count}/{total_count})"
        )
        # Update the count in progress text
        progress_text = self.progress_percent.cget("text").split("|")[0]
        self.progress_percent.config(
            text=f"{progress_text} | {current_count}/{total_count} files"
        )

    def format_kb(self, kb_value):
        """Format KB values for display"""
        if kb_value >= 1024:
            return f"{kb_value/1024:.1f} MB"
        return f"{int(kb_value)} KB"

    
    def conversion_complete(self, success_count, failed_files, processed_kb, total_kb):
        """Final update with complete information"""
        self.progress_bar['value'] = processed_kb
        self.progress_bar['maximum'] = total_kb
        self.progress_text = "{} / {} KB (100%) | {}/{} files".format(
            int(processed_kb), int(total_kb), 
            success_count + len(failed_files), 
            self.total_files
        )
        self.progress_percent.config(text=self.progress_text)

        self.conversion_active = False
        self.currently_converting = False
    
        # Hide popup
        self.hide_converting_popup()

        # Show completion message
        if success_count > 0:
            self.status_label.config(text=f"✅ Successfully converted {success_count} file(s)")
    
        # Show detailed error report if needed
        if failed_files:
            error_details = "\n\n".join(
                f"• {filename}: {error}" 
                for filename, error in failed_files
            )
        
            error_window = Toplevel(self.root)
            error_window.title("Conversion Errors")
            error_window.geometry("600x400")
        
            # Error header
            Label(error_window, 
                 text=f"{len(failed_files)} files failed:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
            # Scrollable error display
            error_frame = Frame(error_window)
            error_frame.pack(fill=BOTH, expand=True)
        
            scrollbar = Scrollbar(error_frame)
            scrollbar.pack(side=RIGHT, fill=Y)
        
            error_text = Text(error_frame, wrap=WORD, yscrollcommand=scrollbar.set)
            error_text.pack(fill=BOTH, expand=True)
            scrollbar.config(command=error_text.yview)
        
            error_text.insert(END, error_details)
            error_text.config(state=DISABLED)
        
            # Close button
            Button(error_window, 
                  text="Close", 
                  command=error_window.destroy).pack(pady=10)
    
        elif success_count > 0:
            messagebox.showinfo(
                "🎉 Conversion Complete",
                f"Successfully converted {success_count} video(s) to MP3"
            )

        # Update status
        self.status_label.config(
            text=f"Completed: {success_count} success, {len(failed_files)} failed"
        )

    # def show_processing_dialog(self):
    #     """Show a processing dialog during conversion"""
    #     self.processing_dialog = Toplevel(self.root)
    #     self.processing_dialog.title("Processing")
    #     self.processing_dialog.geometry("300x100")
    #     self.processing_dialog.resizable(False, False)
    
    #     # Make it modal
    #     self.processing_dialog.grab_set()
    #     self.processing_dialog.transient(self.root)
    
    #     Label(self.processing_dialog, 
    #          text="Converting videos...\nPlease wait", 
    #          font=("Helvetica", 12)).pack(pady=20)
    
    #     # Center the dialog
    #     self.center_window(self.processing_dialog)

    # def hide_processing_dialog(self):
    #     """Hide the processing dialog"""
    #     if hasattr(self, 'processing_dialog') and self.processing_dialog.winfo_exists():
    #         self.processing_dialog.grab_release()
    #         self.processing_dialog.destroy()

    def center_window(self, window):
        """Center a window on screen"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def show_converting_popup(self):
        """Show an animated converting popup that stays visible and centered"""
        self.converting_popup = Toplevel(self.root)
        self.converting_popup.title("Converting Videos")
        self.converting_popup.geometry("400x150")
        self.converting_popup.resizable(False, False)
    
        # Ensure popup stays on top of main window but not necessarily all other apps
        self.converting_popup.attributes("-topmost", True)
    
        # Make it modal but don't completely block main window
        self.converting_popup.grab_set()
        self.converting_popup.transient(self.root)
    
        # Content frame
        content_frame = Frame(self.converting_popup)
        content_frame.pack(pady=20, padx=20, fill=BOTH, expand=True)
    
        # Animated spinner
        self.spinner_label = Label(content_frame, text="◐", font=("Arial", 24))
        self.spinner_label.pack()
    
        # Status text
        self.converting_status = Label(content_frame, text="Starting conversion...", font=("Arial", 10))
        self.converting_status.pack(pady=10)
    
        # Progress bar
        self.popup_progress = ttk.Progressbar(content_frame, orient=HORIZONTAL, mode='determinate')
        self.popup_progress.pack(fill="x", pady=5)
    
        # Cancel button
        Button(content_frame, text="Cancel", command=self.cancel_conversion).pack(pady=5)
    
        # Center the popup properly
        self._center_popup()
    
        # Start spinner animation
        self.animate_spinner()
    
        # Bring to front again in case it got hidden
        self.converting_popup.lift()
        self.converting_popup.focus_force()
    
    def animate_spinner(self):
        """Animate the spinner icon"""
        spinner_frames = ["◐", "◓", "◑", "◒"]
        if hasattr(self, 'spinner_label') and self.spinner_label.winfo_exists():
            current_frame = self.spinner_label.cget("text")
            next_frame = spinner_frames[(spinner_frames.index(current_frame) + 1) % len(spinner_frames)]
            self.spinner_label.config(text=next_frame)
            self.root.after(150, self.animate_spinner)


    def update_converting_popup(self, progress, message):
        """Update the converting popup progress and ensure it stays visible"""
        if hasattr(self, 'converting_popup') and self.converting_popup.winfo_exists():
            self.popup_progress['value'] = progress
            self.converting_status.config(text=message)
        
            # Ensure popup stays visible
            self.converting_popup.lift()
            self.converting_popup.update()

    def hide_converting_popup(self):
        """Hide the converting popup"""
        if hasattr(self, 'converting_popup') and self.converting_popup.winfo_exists():
            self.converting_popup.grab_release()
            self.converting_popup.destroy()

    def _center_popup(self):
        """Properly center the popup on screen"""
        if hasattr(self, 'converting_popup') and self.converting_popup.winfo_exists():
            self.converting_popup.update_idletasks()  # Ensure window dimensions are calculated
        
            # Get screen dimensions
            screen_width = self.converting_popup.winfo_screenwidth()
            screen_height = self.converting_popup.winfo_screenheight()
        
            # Get window dimensions
            window_width = self.converting_popup.winfo_width()
            window_height = self.converting_popup.winfo_height()
        
            # Calculate position
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
        
            # Set geometry
            self.converting_popup.geometry(f"+{x}+{y}")