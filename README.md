# Kajetany BIP Project

## 🚀 Quick Start for New Developers

### **VS Code Setup (Recommended)**
1. Clone the repository:
   ```bash
   git clone https://github.com/suuriko/Kajetany_BIP.git
   cd Kajetany_BIP
   ```

2. Open in VS Code:
   ```bash
   code .
   ```

3. **Install recommended extensions** when prompted, or manually install:
   - Ruff (charliermarsh.ruff)
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - EditorConfig (editorconfig.editorconfig)

4. Run setup script:
   ```bash
   ./setup.sh
   ```

### **Manual Setup (Alternative)**
```bash
git clone https://github.com/suuriko/Kajetany_BIP.git
cd Kajetany_BIP
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"   # Note the quotes for zsh
```

### **Daily Development Commands:**
```bash
# Activate environment

# macOS/Linux:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat

# Check and fix code
ruff check .              # Lint code
ruff check . --fix        # Auto-fix issues
ruff format .             # Format code
```

### **Installation Options:**
```bash
# Runtime dependencies only
pip install -e .

# Runtime + development dependencies
pip install -e ".[dev]"
```

## 🎯 **Key Benefits:**

- **🔧 VS Code Integration** - Automatic extension recommendations and workspace settings
- **📏 Consistent formatting** - Ruff enforces 4-space indentation and 120-char line limits
- **🧹 Code quality** - Real-time linting with Ruff catches issues as you type
- **⚡ Fast setup** - One-command setup with `./setup.sh`
- **🚀 Modern tooling** - Uses latest Python development standards

## 🛠 **VS Code Features Included:**

- **Extension recommendations** - Automatically suggests required extensions
- **Workspace settings** - Pre-configured for consistent development
- **Debug configurations** - Ready-to-use debug setups for main script
- **Tasks** - Pre-configured tasks for linting, formatting, and running
- **Auto-formatting** - Code formats automatically on save
