#!/bin/bash
# validate-deployment.sh - Master deployment validation script
# Orchestrates all pre-flight checks for Option A deployment
# Exit: 0 if all checks pass, 1 if any check fails

set -o pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$REPO_ROOT/scripts"
SCRIPT_NAME="$(basename "$0")"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track results
declare -A results
declare -A times

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Option A Deployment Pre-Flight Validation${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Repository: $REPO_ROOT"
    echo "Starting at: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
}

run_validation() {
    local script_name=$1
    local script_path="$SCRIPTS_DIR/$script_name"
    
    echo -e "${BLUE}[TEST]${NC} Running $script_name..."
    
    # Check script exists
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}✗ FAIL: $script_name not found${NC}"
        results[$script_name]="FAIL"
        return 1
    fi
    
    # Make executable
    chmod +x "$script_path"
    
    # Run script and capture output + time
    local start_time=$(date +%s%N)
    local output
    
    if output=$("$script_path" 2>&1); then
        local end_time=$(date +%s%N)
        local duration=$(echo "scale=2; ($end_time - $start_time) / 1000000" | bc)
        
        results[$script_name]="PASS"
        times[$script_name]="$duration"
        
        echo -e "${GREEN}✓ PASS${NC}: $script_name (${duration}ms)"
        echo "$output" | sed 's/^/  /'
        return 0
    else
        local end_time=$(date +%s%N)
        local duration=$(echo "scale=2; ($end_time - $start_time) / 1000000" | bc)
        
        results[$script_name]="FAIL"
        times[$script_name]="$duration"
        
        echo -e "${RED}✗ FAIL${NC}: $script_name (${duration}ms)"
        echo "$output" | sed 's/^/  /'
        return 1
    fi
}

print_summary() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Validation Summary${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    local total_tests=${#results[@]}
    local passed_tests=0
    local failed_tests=0
    
    for script in "${!results[@]}"; do
        local status="${results[$script]}"
        local duration="${times[$script]}"
        
        if [[ "$status" == "PASS" ]]; then
            echo -e "${GREEN}✓ PASS${NC} | $script (${duration}ms)"
            ((passed_tests++))
        else
            echo -e "${RED}✗ FAIL${NC} | $script (${duration}ms)"
            ((failed_tests++))
        fi
    done
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total Tests: $total_tests | Passed: $passed_tests | Failed: $failed_tests"
    echo "Status: $([ $failed_tests -eq 0 ] && echo -e "${GREEN}READY FOR DEPLOYMENT${NC}" || echo -e "${RED}VALIDATION FAILED${NC}")"
    echo "Completed at: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [[ $failed_tests -eq 0 ]]; then
        echo -e "${GREEN}✓ All validations passed! System ready for Option A deployment.${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Review the validation results above"
        echo "  2. Run: docker-compose up -d"
        echo "  3. Monitor logs: docker-compose logs -f"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Validation failed with $failed_tests error(s).${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. Review failures above"
        echo "  2. Fix issues in source code"
        echo "  3. Re-run: $SCRIPT_NAME"
        echo ""
        return 1
    fi
}

main() {
    print_header
    
    # Run all validation scripts
    local overall_status=0
    
    run_validation "validate-yaml.sh" || overall_status=1
    run_validation "validate-backend.sh" || overall_status=1
    run_validation "validate-frontend.sh" || overall_status=1
    run_validation "validate-imports.sh" || overall_status=1
    
    # Print summary and return status
    print_summary
    return $overall_status
}

main "$@"
