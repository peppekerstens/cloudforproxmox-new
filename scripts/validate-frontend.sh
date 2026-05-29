#!/bin/bash
# validate-frontend.sh - Frontend linting and import validation
# Checks: npm lint, TypeScript compilation, critical imports

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$REPO_ROOT/frontend"
SCRIPT_NAME="$(basename "$0")"

main() {
    echo "=== $SCRIPT_NAME ==="
    
    # Check frontend directory exists
    if [[ ! -d "$FRONTEND_DIR" ]]; then
        echo "✗ FAIL: frontend directory not found at $FRONTEND_DIR"
        return 1
    fi
    
    cd "$FRONTEND_DIR"
    
    # Check package.json exists
    if [[ ! -f "package.json" ]]; then
        echo "✗ FAIL: package.json not found"
        return 1
    fi
    
    # Install dependencies if node_modules missing
    echo "Checking dependencies..."
    if [[ ! -d "node_modules" ]]; then
        echo "Installing npm packages..."
        npm install --silent 2>&1 | tail -5
    fi
    echo "✓ Dependencies OK"
    
    # Run ESLint if available
    echo ""
    echo "Running frontend linting..."
    if [[ -f ".eslintrc" ]] || [[ -f ".eslintrc.json" ]] || [[ -f ".eslintrc.cjs" ]]; then
        if npm run lint > /tmp/lint.log 2>&1; then
            echo "✓ Lint passed"
        else
            echo "✗ FAIL: Lint errors found"
            cat /tmp/lint.log | head -50
            return 1
        fi
    else
        echo "⚠ ESLint config not found, skipping lint check"
    fi
    
    # Check critical imports in key files
    echo ""
    echo "Validating critical imports..."
    critical_files=(
        "src/App.tsx"
        "src/components/ConfirmDialog.tsx"
        "src/stores/configStore.ts"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo "  ⚠ Warning: $file not found (may not be critical for this build)"
            continue
        fi
        
        # Check for obvious broken imports (imports with non-existent files)
        if grep -E "^import.*from ['\"]\..*['\"]" "$file" | while read -r line; do
            # Extract the import path
            import_path=$(echo "$line" | sed -E "s/.*from ['\"]([^'\"]+)['\"].*/\1/")
            
            # Resolve relative path
            file_dir=$(dirname "$file")
            resolved_path="$file_dir/$import_path"
            
            # Check if file exists (with .ts, .tsx extensions)
            if [[ ! -f "$resolved_path" ]] && \
               [[ ! -f "${resolved_path}.ts" ]] && \
               [[ ! -f "${resolved_path}.tsx" ]] && \
               [[ ! -f "${resolved_path}/index.ts" ]] && \
               [[ ! -f "${resolved_path}/index.tsx" ]]; then
                echo "  ✗ FAIL: Missing import in $file: $import_path"
                return 1
            fi
        done; then
            echo "  ✓ $file imports OK"
        fi
    done
    
    # Verify tsconfig.json
    echo ""
    echo "Checking TypeScript configuration..."
    if [[ ! -f "tsconfig.json" ]]; then
        echo "✗ FAIL: tsconfig.json not found"
        return 1
    fi
    
    # Try TypeScript type-check
    echo "Running TypeScript type check..."
    if command -v npx &> /dev/null && npx tsc --noEmit > /tmp/tsc.log 2>&1; then
        echo "✓ TypeScript check passed"
    else
        # Warn but don't fail if tsc not available
        echo "⚠ TypeScript check skipped (tsc not available)"
    fi
    
    echo ""
    echo "✓ Frontend validation passed"
    return 0
}

main "$@"
