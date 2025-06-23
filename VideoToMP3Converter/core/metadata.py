from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TYER, TCON

class MetadataHandler:
    def __init__(self, app):
        self.app = app
        
    def apply_metadata(self, mp3_file):
        """Apply metadata to an MP3 file"""
        try:
            # Create ID3 tag if it doesn't exist
            try:
                audio = MP3(mp3_file, ID3=ID3)
            except:
                audio = MP3()
                audio.add_tags()
        
            # Set basic tags
            if self.app.title_var.get():
                audio.tags.add(TIT2(encoding=3, text=self.app.title_var.get()))
            if self.app.artist_var.get():
                audio.tags.add(TPE1(encoding=3, text=self.app.artist_var.get()))
            if self.app.album_var.get():
                audio.tags.add(TALB(encoding=3, text=self.app.album_var.get()))
            if self.app.year_var.get():
                audio.tags.add(TYER(encoding=3, text=self.app.year_var.get()))
            if self.app.genre_var.get():
                audio.tags.add(TCON(encoding=3, text=self.app.genre_var.get()))
        
            # Add cover art if selected
            if self.app.cover_art_path.get():
                with open(self.app.cover_art_path.get(), "rb") as f:
                    cover_data = f.read()
                    mime = "image/jpeg" if self.app.cover_art_path.get().lower().endswith(('.jpg', '.jpeg')) else "image/png"
                    audio.tags.add(APIC(
                        encoding=3,
                        mime=mime,
                        type=3,  # 3 = front cover
                        desc="Cover",
                        data=cover_data
                    ))
        
            # Save the file
            audio.save(mp3_file)
        
        except Exception as e:
            print(f"Failed to add metadata to {mp3_file}: {e}")

    def extract_video_metadata(video_path):
        """Extract technical metadata from video file"""
        try:
            with VideoFileClip(video_path) as clip:
                return {
                    'duration': clip.duration,
                    'fps': clip.fps,
                    'size': clip.size,
                    'audio_fps': clip.audio.fps if clip.audio else None
                }
        except:
            return {}
