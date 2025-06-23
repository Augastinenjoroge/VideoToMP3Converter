import datetime
from moviepy import VideoFileClip
import threading
import os
import time
from tkinter import messagebox

class VideoConverter:
    def __init__(self, app):
        self.app = app
        
    def start_conversion(self):
        # Show processing dialog
        # self.app.show_processing_dialog()
        
        # Start conversion in a separate thread
        conversion_thread = threading.Thread(target=self.convert_videos)
        conversion_thread.start()
        
    def convert_videos(self):
        total_files = len(self.app.video_paths)
        success_count = 0
        failed_files = []
        total_mp3_size_kb = 0  # Will be updated as we convert
        processed_mp3_size_kb = 0
    
        # Initial UI update
        self.app.root.after(0, self.app.initialize_progress, total_files)
    
        for i, video_file in enumerate(self.app.video_paths):
            if not self.app.conversion_active:
                break
            
            current_file = os.path.basename(video_file)
        
            try:
                # Update UI before processing
                self.app.root.after(0, self.app.update_file_progress, 
                                  current_file, i+1, total_files)
            
                # Process the file and get output size
                result, mp3_size_kb = self.process_video_file(video_file)
            
                if result is True:
                    success_count += 1
                    processed_mp3_size_kb += mp3_size_kb
                    total_mp3_size_kb += mp3_size_kb  # Add to total
                
                    # Update progress with MP3 sizes
                    self.app.root.after(0, self.app.update_progress, 
                                      processed_mp3_size_kb, total_mp3_size_kb,
                                      f"Processed: {current_file}")
                else:
                    failed_files.append((current_file, result))
                
            except Exception as e:
                failed_files.append((current_file, str(e)))
        
            time.sleep(0.1)
    
        # Final update
        self.app.root.after(0, self.app.conversion_complete, 
                           success_count, failed_files,
                           processed_mp3_size_kb, total_mp3_size_kb)
    
    def process_video_file(self, video_file):
        try:
            # Verify file exists and is accessible
            if not os.path.exists(video_file):
                raise Exception(f"File not found: {video_file}")
            
            if not os.access(video_file, os.R_OK):
                raise Exception(f"No read permissions for: {video_file}")

            # Create output directory if needed
            output_dir = self.app.output_path.get()
            os.makedirs(output_dir, exist_ok=True)
        
            # Generate safe output filename
            base_name = os.path.splitext(os.path.basename(video_file))[0]
            safe_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
            output_file = os.path.join(output_dir, f"{safe_name}.mp3")

            # Check for codec support
            with VideoFileClip(video_file) as clip:
                if not hasattr(clip, 'audio') or clip.audio is None:
                    raise Exception("Video file contains no audio stream")
                
                # Convert with detailed error handling
                try:
                    clip.audio.write_audiofile(
                        output_file,
                        bitrate=self.app.quality_var.get(),
                        codec='libmp3lame',
                        ffmpeg_params=[
                            '-ar', '44100',
                            '-ac', '2',
                            '-q:a', '0' if self.app.quality_var.get() == '320k' else '2'
                        ],
                        logger=None
                    )
                except Exception as write_error:
                    raise Exception(f"Audio writing failed: {str(write_error)}")

            # Verify output file was created
            if not os.path.exists(output_file):
                raise Exception("Output file was not created")
            
            if os.path.getsize(output_file) == 0:
                os.remove(output_file)
                raise Exception("Created empty output file")

            mp3_size_kb = os.path.getsize(output_file) / 1024
            
            return True, mp3_size_kb
        
        except Exception as e:
            # Clean up failed files
            if 'output_file' in locals() and os.path.exists(output_file):
                try:
                    os.remove(output_file)
                except:
                    pass
                
            error_msg = f"{os.path.basename(video_file)}: {str(e)}"
            print(f"Conversion Error: {error_msg}")
            return error_msg