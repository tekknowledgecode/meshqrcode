import subprocess
import sys
import os
from pathlib import Path

py_exec = str(sys.executable)
# Get lib directory
lib = os.path.join(Path(py_exec).parent.parent, "lib")
# Ensure pip is installed
subprocess.call([py_exec, "-m", "ensurepip", "--user" ])
# Update pip (not mandatory)
subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip" ])
# Install package
subprocess.call([py_exec,"-m", "pip", "install", f"--target={str(lib)}", "qrcode2"]
