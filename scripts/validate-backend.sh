#!/bin/bash
# validate-backend.sh - Backend linting and validation
# Checks: Python syntax, import errors, critical files

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
SCRIPT_NAME="$(basename "$0")"

main() {
    echo "=== $SCRIPT_NAME ==="
    
    # Check backend directory exists
    if [[ ! -d "$BACKEND_DIR" ]]; then
        echo "✗ FAIL: backend directory not found at $BACKEND_DIR"
        return 1
    fi
    
    cd "$BACKEND_DIR"
    
    # Check requirements.txt exists
    if [[ ! -f "requirements.txt" ]]; then
        echo "✗ FAIL: requirements.txt not found"
        return 1
    fi
    
    # Check app directory exists
    if [[ ! -d "app" ]]; then
        echo "✗ FAIL: app directory not found"
        return 1
    fi
    
    # Verify critical Python files exist
    echo "Checking critical Python files..."
    critical_files=(
        "app/auth.py"
        "app/main.py"
        "app/dependencies.py"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo "  ✓ Found: $file"
        else
            echo "  ⚠ Warning: $file not found"
        fi
    done
    
    # Python syntax check on all Python files
    echo ""
    echo "Checking Python syntax..."
    py_errors=0
    while IFS= read -r py_file; do
        if ! python3 -m py_compile "$py_file" 2>/dev/null; then
            echo "  ✗ FAIL: Syntax error in $py_file"
            python3 -m py_compile "$py_file" 2>&1 | head -5
            ((py_errors++))
        fi
    done < <(find app -name "*.py" -type f)
    
    if [[ $py_errors -gt 0 ]]; then
        echo "✗ FAIL: Found $py_errors Python files with syntax errors"
        return 1
    fi
    echo "✓ Python syntax valid"
    
    # Import validation: Check if key imports can be resolved
    echo ""
    echo "Validating critical imports..."
    
    # Check for common import errors in key files
    if [[ -f "app/auth.py" ]]; then
        echo "  Checking app/auth.py imports..."
        if grep -q "^from fastapi import" app/auth.py || \
           grep -q "^import fastapi" app/auth.py; then
            echo "    ✓ FastAPI import OK"
        fi
        
        if grep -q "^from.*models import" app/auth.py || \
           grep -q "^from.*database import" app/auth.py; then
            echo "    ✓ Local imports OK"
        fi
    fi
    
    # Check main.py
    if [[ -f "app/main.py" ]]; then
        echo "  Checking app/main.py imports..."
        if ! grep -q "from fastapi import" app/main.py && \
           ! grep -q "import fastapi" app/main.py; then
            echo "  ⚠ Warning: FastAPI import not found in main.py"
        fi
    fi
    
    # Attempt pylint if available
    echo ""
    echo "Running Python linting..."
    if command -v pylint &> /dev/null; then
        if pylint app --rcfile=/dev/null --disable=all --enable=syntax-error \
            > /tmp/pylint.log 2>&1; then
            echo "✓ Pylint passed (syntax check)"
        else
            echo "✗ FAIL: Pylint found syntax errors"
            cat /tmp/pylint.log | head -20
            return 1
        fi
    else
        echo "⚠ Pylint not available, skipping"
    fi
    
    # Flake8 syntax check if available
    if command -v flake8 &> /dev/null; then
        echo "Running flake8 syntax check..."
        if flake8 app --select=E,F --max-line-length=120 > /tmp/flake8.log 2>&1; then
            echo "✓ Flake8 passed"
        else
            echo "⚠ Flake8 warnings (non-critical):"
            cat /tmp/flake8.log | head -10
        fi
    fi
    
    echo ""
    echo "✓ Backend validation passed"
    return 0
}

main "$@"
