#!/bin/bash
# validate-imports.sh - Import resolution validation
# Checks: Python imports resolve, TypeScript imports resolve

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"
SCRIPT_NAME="$(basename "$0")"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

main() {
    echo "=== $SCRIPT_NAME ==="
    
    import_errors=0
    
    # ===== PYTHON IMPORTS =====
    echo ""
    echo "Validating Python imports..."
    cd "$BACKEND_DIR" || return 1
    
    while IFS= read -r py_file; do
        # Extract all import statements
        while IFS= read -r import_line; do
            # Skip comments and empty lines
            [[ -z "$import_line" ]] && continue
            [[ "$import_line" =~ ^[[:space:]]*# ]] && continue
            
            # Handle: from module import something
            if [[ "$import_line" =~ ^from[[:space:]]+(.+)[[:space:]]+import ]]; then
                module="${BASH_REMATCH[1]}"
                
                # Skip standard library and third-party (no relative path)
                if [[ "$module" =~ ^[a-zA-Z_] ]] && ! [[ "$module" =~ ^\. ]]; then
                    continue
                fi
                
                # Relative imports: convert to file path
                if [[ "$module" =~ ^\. ]]; then
                    module_path=$(echo "$module" | sed 's/\./{}/g' | sed 's/[^\/]*/{}/g' | sed 's/{}/\//g')
                    file_dir=$(dirname "$py_file")
                    resolved_path="$file_dir/$module_path.py"
                    
                    if [[ ! -f "$resolved_path" ]] && [[ ! -d "$file_dir/$module_path" ]]; then
                        echo "  ✗ FAIL: Missing import in $py_file"
                        echo "         Line: $import_line"
                        echo "         Looking for: $resolved_path"
                        ((import_errors++))
                    fi
                fi
            fi
        done < <(grep -E "^(from|import)[[:space:]]+" "$py_file" 2>/dev/null || true)
    done < <(find app -name "*.py" -type f 2>/dev/null)
    
    if [[ $import_errors -eq 0 ]]; then
        echo "✓ Python imports valid"
    else
        echo "✗ FAIL: Found $import_errors Python import errors"
        return 1
    fi
    
    # ===== TYPESCRIPT IMPORTS =====
    echo ""
    echo "Validating TypeScript imports..."
    cd "$FRONTEND_DIR" || return 1
    
    ts_import_errors=0
    
    while IFS= read -r ts_file; do
        # Extract all import statements
        while IFS= read -r import_line; do
            # Skip comments and empty lines
            [[ -z "$import_line" ]] && continue
            [[ "$import_line" =~ ^[[:space:]]*/\/ ]] && continue
            
            # Handle: import ... from "path" or import ... from 'path'
            if [[ "$import_line" =~ from[[:space:]]+[\'\"]([^\'\"]+)[\'\"] ]]; then
                import_path="${BASH_REMATCH[1]}"
                
                # Skip node_modules and absolute imports
                if [[ "$import_path" =~ ^[^./] ]]; then
                    continue
                fi
                
                # Resolve relative import path
                if [[ "$import_path" =~ ^\. ]]; then
                    file_dir=$(dirname "$ts_file")
                    
                    # Handle both './file.tsx' and './file' patterns
                    # Remove .ts/.tsx if already present
                    import_base="${import_path%.tsx}"
                    import_base="${import_base%.ts}"
                    
                    # Try to find the file
                    resolved_base="$file_dir/$import_base"
                    
                    found=0
                    # Direct match with extensions
                    if [[ -f "$file_dir/$import_path" ]]; then
                        found=1
                    # Try adding extensions if not present
                    elif [[ -f "${resolved_base}.ts" ]] || \
                       [[ -f "${resolved_base}.tsx" ]] || \
                       [[ -f "${resolved_base}/index.ts" ]] || \
                       [[ -f "${resolved_base}/index.tsx" ]] || \
                       [[ -d "$resolved_base" ]]; then
                        found=1
                    fi
                    
                    if [[ $found -eq 0 ]]; then
                        echo "  ✗ FAIL: Missing import in $ts_file"
                        echo "         Line: $import_line"
                        echo "         Looking for: $file_dir/$import_path"
                        ((ts_import_errors++))
                    fi
                fi
            fi
        done < <(grep -E "import.*from ['\"]" "$ts_file" 2>/dev/null || true)
    done < <(find src -name "*.ts" -o -name "*.tsx" 2>/dev/null)
    
    if [[ $ts_import_errors -eq 0 ]]; then
        echo "✓ TypeScript imports valid"
    else
        echo "✗ FAIL: Found $ts_import_errors TypeScript import errors"
        return 1
    fi
    
    echo ""
    echo "✓ All imports validated successfully"
    return 0
}

main "$@"
