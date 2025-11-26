#!/bin/bash
# Quick PostgreSQL Setup Script for Attendance System

set -e

echo "============================================"
echo "PostgreSQL Local Setup for Attendance System"
echo "============================================"

# Step 1: Check PostgreSQL installation
echo -e "\n[1/6] Checking PostgreSQL installation..."
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found. Installing..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
else
    echo "✓ PostgreSQL found: $(psql --version)"
fi

# Step 2: Start PostgreSQL service
echo -e "\n[2/6] Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo "✓ PostgreSQL service started"

# Step 3: Create user and database
echo -e "\n[3/6] Creating database user and database..."

read -p "Enter database password (default: password123): " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-password123}

read -p "Enter database name (default: attendance_db): " DB_NAME
DB_NAME=${DB_NAME:-attendance_db}

read -p "Enter database user (default: att_user): " DB_USER
DB_USER=${DB_USER:-att_user}

# Create user and database
sudo -u postgres psql << EOF
-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Set role configuration
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET default_transaction_deferrable TO on;
ALTER ROLE $DB_USER SET timezone TO 'UTC';

-- Create database
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Exit
\q
EOF

echo "✓ Database user and database created"

# Step 4: Create .env file
echo -e "\n[4/6] Creating .env file..."

cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql+psycopg2://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME

# Flask Configuration  
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
TIMEZONE=Asia/Qatar
FLASK_DEBUG=1
EOF

echo "✓ .env file created"

# Step 5: Install Python dependencies
echo -e "\n[5/6] Installing Python dependencies..."

pip install -q psycopg2-binary python-dotenv flask flask-login werkzeug pandas openpyxl pytz 2>/dev/null || true

echo "✓ Dependencies installed"

# Step 6: Initialize database
echo -e "\n[6/6] Initializing database..."

# Create tables and indexes
flask --app app init-db
flask --app app add-attendance-columns

echo "✓ Database initialized"

# Test connection
echo -e "\n[Test] Testing database connection..."

psql -U $DB_USER -d $DB_NAME -h localhost << EOF
\dt
SELECT COUNT(*) FROM attendance;
\q
EOF

echo -e "\n✓✓✓ PostgreSQL setup completed successfully! ✓✓✓\n"

echo "Next steps:"
echo "  1. Start Flask app: python app.py"
echo "  2. Run load test: python load_test.py"
echo "  3. Access dashboard: http://localhost:5000"
echo ""
echo "Database credentials:"
echo "  User: $DB_USER"
echo "  Database: $DB_NAME"
echo "  Connection: postgresql+psycopg2://$DB_USER:[password]@localhost:5432/$DB_NAME"
    echo "✗ Migration script not found!"
    exit 1
fi

echo "✓ Migration script found"

# Check if load test script exists
if [ ! -f "load_test.py" ]; then
    echo "✗ Load test script not found!"
    exit 1
fi

echo "✓ Load test script found"

echo ""
echo "=============================================="
echo "Setup verification complete!"
echo ""
echo "Next steps:"
echo "1. Ensure PostgreSQL is running"
echo "2. Run: python migrate_to_postgresql.py"
echo "3. Run: python load_test.py"
echo "4. Start app: python app.py"
echo "=============================================="
