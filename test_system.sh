#!/bin/bash

# NarrativeWatch AI - End-to-End System Test Script
# This script tests the entire system flow from backend health to API endpoints

echo "═════════════════════════════════════════════════════════════════"
echo "  NarrativeWatch AI - End-to-End System Test"
echo "═════════════════════════════════════════════════════════════════"
echo ""

API_URL="http://localhost:8000"
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to test endpoints
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_status=$4

    echo -n "Testing [$name]... "

    if [ "$method" = "GET" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$endpoint")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d '{}')
    fi

    if [ "$status" = "$expected_status" ]; then
        echo "✅ PASS (HTTP $status)"
        ((TESTS_PASSED++))
    else
        echo "❌ FAIL (Expected $expected_status, got $status)"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Health Check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 1: Backend Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
test_endpoint "Health Check" "GET" "/health" "200"
echo ""

# Test 2: API Endpoints
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 2: API Endpoint Tests"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "History" "GET" "/api/v1/history" "200"
test_endpoint "Analytics Dashboard" "GET" "/api/v1/analytics/dashboard" "200"
test_endpoint "Document Stats" "GET" "/api/v1/documents/stats" "200"

echo ""

# Test 3: Import Verification
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 3: Python Imports Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Change to backend directory
cd backend || exit 1

echo -n "Testing URLDataExtractor import... "
if python -c "from src.services.url_data_extractor import URLDataExtractor; print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

echo -n "Testing RAGContextService import... "
if python -c "from src.services.rag_context_service import RAGContextService; print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

echo -n "Testing ContextCombiner import... "
if python -c "from src.services.context_combiner import ContextCombiner; print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

echo -n "Testing DocumentIngestionService import... "
if python -c "from src.services.document_ingestion_service import document_ingestion_service; print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

echo -n "Testing All 4 Agents import... "
if python -c "from src.agents.content_analyzer import content_analyzer; from src.agents.bias_detector import bias_detector; from src.agents.bot_detector import bot_detector; from src.agents.misinformation_detector import misinformation_detector; print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "❌ FAIL"
    ((TESTS_FAILED++))
fi

cd .. || exit 1

echo ""

# Test 4: Database Connection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PHASE 4: Database Connection Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -n "Checking PostgreSQL connection... "
if python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://narrativewatch:password@localhost:5432/narrativewatch_ai'); conn = engine.connect(); print('[OK]')" 2>/dev/null | grep -q "OK"; then
    echo "✅ PASS"
    ((TESTS_PASSED++))
else
    echo "⚠️  WARNING (PostgreSQL may not be running)"
    ((TESTS_FAILED++))
fi

echo ""

# Summary
echo "═════════════════════════════════════════════════════════════════"
echo "  TEST SUMMARY"
echo "═════════════════════════════════════════════════════════════════"
echo ""
echo "Tests Passed:  ✅ $TESTS_PASSED"
echo "Tests Failed:  ❌ $TESTS_FAILED"
echo "Total Tests:   $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - System is healthy!"
    echo ""
    echo "Next steps:"
    echo "  1. Start frontend: cd frontend && npm start"
    echo "  2. Go to http://localhost:3000"
    echo "  3. Upload documents at http://localhost:3000/documents"
    echo "  4. Analyze articles at http://localhost:3000/projects"
    exit 0
else
    echo "❌ SOME TESTS FAILED - Check errors above"
    echo ""
    echo "Troubleshooting:"
    echo "  - Ensure backend is running on port 8000"
    echo "  - Verify PostgreSQL is running"
    echo "  - Check Python dependencies are installed"
    exit 1
fi
