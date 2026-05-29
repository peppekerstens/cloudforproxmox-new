#!/bin/bash
# validate-yaml.sh - YAML validation for docker-compose.yml
# Checks: syntax, required keys, structural integrity

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DC_FILE="$REPO_ROOT/docker-compose.yml"
SCRIPT_NAME="$(basename "$0")"

main() {
    echo "=== $SCRIPT_NAME ==="
    
    # Check file exists
    if [[ ! -f "$DC_FILE" ]]; then
        echo "✗ FAIL: docker-compose.yml not found at $DC_FILE"
        return 1
    fi
    
    # Try using docker-compose config (preferred, validates structure)
    if command -v docker-compose &> /dev/null; then
        echo "Validating YAML syntax with docker-compose config..."
        if ! docker-compose -f "$DC_FILE" config > /dev/null 2>&1; then
            echo "✗ FAIL: docker-compose.yml has syntax errors"
            docker-compose -f "$DC_FILE" config 2>&1 | head -20
            return 1
        fi
        echo "✓ docker-compose.yml syntax valid"
    else
        # Fallback: use python yaml parser
        echo "Validating YAML syntax with Python..."
        if ! python3 -c "import yaml; yaml.safe_load(open('$DC_FILE'))" 2>/dev/null; then
            echo "✗ FAIL: docker-compose.yml has syntax errors"
            return 1
        fi
        echo "✓ docker-compose.yml syntax valid"
    fi
    
    # Verify required top-level keys
    echo "Checking required keys..."
    required_keys=("version" "services" "volumes" "networks")
    for key in "${required_keys[@]}"; do
        if grep -q "^$key:" "$DC_FILE"; then
            echo "  ✓ Found: $key"
        else
            echo "  ✗ FAIL: Missing required key: $key"
            return 1
        fi
    done
    
    # Verify required services
    echo "Checking required services..."
    required_services=("postgres" "redis" "rabbitmq" "api" "frontend")
    for service in "${required_services[@]}"; do
        if grep -q "^  $service:" "$DC_FILE"; then
            echo "  ✓ Found service: $service"
        else
            echo "  ✗ FAIL: Missing required service: $service"
            return 1
        fi
    done
    
    echo ""
    echo "✓ YAML validation passed"
    return 0
}

main "$@"
