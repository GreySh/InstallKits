"""
Точка входа Toga-приложения InstallKits.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from toga_app.app import main

if __name__ == "__main__":
    app = main()
    app.main_loop()
