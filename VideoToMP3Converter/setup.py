from cx_Freeze import setup, Executable
import sys
import os

# Base setup
base = "Win32GUI" if sys.platform == "win32" else None

# Packages to include
packages = [
    "tkinter",
    "moviepy",
    "PIL",
    "imageio",
    "numpy",
    "os",
    "sys",
    "re",
    "threading",
    "imageio_ffmpeg",
    "tqdm"
]

# Packages to explicitly exclude
excludes = [
    "tkinter.test",
    "IPython",
    "matplotlib",
    "pandas",
    "pytest",
    "tensorflow",
    "dask",
    "keras",
    "setuptools_scm",
    "requests",
    "slack_sdk",
    "rich",
    "cv2",
    "av",
    "lxml",
    "rawpy",
    "zstd",
    "itk",
    "backports",
    "tifffile",
    "SimpleITK",
    "asyncio",
    "email",
    "html",
    "http",
    "xml",
    "unittest",
    "nose",
    "test",
    "tests",
    "setuptools",
    "distutils",
    "astropy",
    "bsdf",
    "gdal",
    "heif",
    "notebook",
    "pyav",
    "simpleitk",
    "telegram",
    "discord",
    "nose",
    "test",
    "tests",
    "setuptools",
    "distutils",
    "pkg_resources"
]

# Include files
include_files = []
data_folders = ['assets', 'data']
for folder in data_folders:
    if os.path.exists(folder):
        for root, dirs, files in os.walk(folder):
            dest_dir = os.path.relpath(root, os.path.curdir)
            include_files.extend(
                (os.path.join(root, f), os.path.join(dest_dir, f))
                for f in files
            )

setup(
    name="VideoToMP3Converter",
    version="1.0",
    description="Video to MP3 Converter",
    options={
        "build_exe": {
            "packages": packages,
            "include_files": include_files,
            "excludes": excludes,
            "optimize": 2,
            "include_msvcr": True
        }
    },
    executables=[Executable(
        "VideoToMP3Converter.py",
        base=base,
        icon="assets/music.ico",
        target_name="VideoToMP3Converter"
    )]
)