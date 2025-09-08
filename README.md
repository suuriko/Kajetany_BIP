### **For Daily Development:**
```bash
# Activate environment
source venv/bin/activate

# Format and check your code
black .
isort .
ruff check . --fix
```

### **For New Developers:**
They just need to run:
```bash
git clone <repository>
cd Kajetany_BIP
source venv/bin/activate  # or create new venv
pip install -e ".[dev]"   # Note the quotes for zsh
```

### **Installation Options:**
```bash
# Runtime dependencies only
pip install -e .

# Runtime + development dependencies
pip install -e ".[dev]"
```

## 🎯 **Key Benefits:**

- **Consistent formatting** - Black enforces 4-space indentation automatically
- **Clean imports** - isort organizes your imports consistently
- **Code quality** - Ruff catches potential issues and style problems
- **Easy setup** - New developers get everything with one command

Your code formatting and linting tools are now properly configured and working! 🎉
