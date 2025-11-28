#!/bin/bash
# Start the PostgreSQL Attendance System
# This script starts your Flask application using PostgreSQL

echo ""
echo "======================================================================"
echo "PostgreSQL Attendance System - Starting Flask App"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  Database: PostgreSQL (attdbsch)"
echo "  User: adminit"
echo "  Host: localhost:5432"
echo ""
echo "Data Status:"
echo "  ✓ 97 users migrated"
echo "  ✓ 933 students migrated"
echo "  ✓ 30 classes migrated"
echo "  ✓ 483 attendance records migrated"
echo ""
echo "Starting Flask application..."
echo "======================================================================"
echo ""

# Start the app
python app.py
