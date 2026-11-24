#!/usr/bin/env bash
set -e

echo "=========================================="
echo " Setting up FRA371 Kinematics Labs (Lab 3)"
echo " (Linux / macOS - Python 3.11-3.13)"
echo "=========================================="

# Select Python 3.13 (recommended for Lab 3), falling back to 3.12 / 3.11 / python3
PYTHON_BIN=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &> /dev/null; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "[ERROR] Python 3.11-3.13 not found. Please install Python 3.13."
    exit 1
fi
echo "[OK] Using $($PYTHON_BIN --version)"

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    "$PYTHON_BIN" -m venv .venv
else
    echo "[INFO] Existing .venv found."
fi

# Clean PYTHONPATH to prevent ROS conflicts on Ubuntu
export PYTHONPATH=""

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip

# Install pinned Lab 3 dependencies + symbolic tools
echo "[INFO] Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Run fix_swift.py (no-op on Linux/macOS if not needed, safe to run)
echo "[INFO] Running fix_swift.py..."
python fix_swift.py

# Quick verification check
echo "[INFO] Verifying Robot.URDF_read, Swift, and SymPy..."
python -c "import roboticstoolbox as rtb, swift, sympy; from roboticstoolbox.robot.Robot import Robot; assert hasattr(Robot, 'URDF_read'); print('[OK] All Lab 3 imports verified!')"

echo ""
echo "=========================================="
echo " Setup complete!"
echo " Activate anytime: source .venv/bin/activate"
echo " Select kernel '.venv' in Lab_Calculator.ipynb or Lab 3 notebooks"
echo "=========================================="
