from datetime import datetime
import os
from pathlib import Path
import shutil

def get_smart_output_path():
    """Intelligently determine the best output location"""
    candidates = [
        Path.home() / "OneDrive" / "Music",
        Path.home() / "Music",
        Path.home() / "Desktop",
        Path.home() / "Downloads"
    ]
    
    # Find first existing path with most free space
    best_path = max(
        (p for p in candidates if p.exists()),
        key=lambda p: shutil.disk_usage(p).free,
        default=candidates[0]
    )
    
    # Create conversion subfolder
    output_folder = best_path / "Audio Conversions"
    output_folder.mkdir(exist_ok=True)
    
    return str(output_folder)

def get_default_output_path():
    """Alias for get_smart_output_path for backward compatibility"""
    return get_smart_output_path()

def get_current_year():
    """Get the current year as string"""
    return str(datetime.now().year)

def get_supported_video_extensions():
    """Return tuple of supported video extensions"""
    return ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')

def get_supported_image_extensions():
    """Return tuple of supported image extensions for cover art"""
    return ('.jpg', '.jpeg', '.png')