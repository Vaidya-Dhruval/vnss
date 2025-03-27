from distutils.core import setup

import py2exe

setup(
    name="bhavya",
    version="1.0",
    description="Your App Description",
    windows=[{"script": "main.py"}],  # For GUI applications
    # console=[{"script": "main.py"}],  # Uncomment for console applications
    options={
        "py2exe": {
            "packages": ["sqlalchemy"],  # Include any specific packages you need
            "includes": ["pandas", "numpy"],  # Additional libraries if required
            "excludes": ["tkinter"],  # Exclude libraries if not needed
            "bundle_files": 1,  # Bundle everything into one executable
            "compressed": True,
        }
    },
    zipfile=None  # Embed the library.zip in the executable
)
