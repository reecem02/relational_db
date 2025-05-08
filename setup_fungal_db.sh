#!/bin/bash

# 🔹 Set Variables
PROJECT_DIR="$HOME/fungal_db_project"
SQLITE_DB="$HOME/fungal_db.sqlite"

# 🔹 Step 1: Create Project Directory (If Not Exists)
echo "📂 Setting up project directory at $PROJECT_DIR..."
mkdir -p $PROJECT_DIR

# 🔹 Step 2: Transfer Files from Local Machine (Run This on Local PC)
if [ "$1" == "transfer" ]; then
    echo "📤 Transferring project files to CQLS server..."
    scp -r ~/your-local-project-folder yourusername@cqls.oregonstate.edu:$PROJECT_DIR
    echo "✅ Files transferred successfully!"
    exit 0
fi

# 🔹 Step 3: Navigate to Project Directory
cd $PROJECT_DIR || exit 1

# 🔹 Step 4: Install Python Dependencies (Without Root Privileges)
echo "📦 Installing required Python packages..."
pip install --user -r requirements.txt

# 🔹 Step 5: Ensure SQLite is Set Up
if [ ! -f "$SQLITE_DB" ]; then
    echo "🗄️ Creating SQLite database at $SQLITE_DB..."
    python3 -c "from sqlalchemy import create_engine, MetaData; engine = create_engine('sqlite:///$SQLITE_DB'); MetaData().create_all(engine)"
    echo "✅ SQLite database initialized!"
else
    echo "🗄️ SQLite database already exists. Skipping creation."
fi

# 🔹 Step 6: Verify Everything is Working
echo "🔍 Running basic checks..."
python3 -c "
import os
from sqlalchemy import create_engine
DB_PATH = os.path.expanduser('$SQLITE_DB')
engine = create_engine(f'sqlite:///{DB_PATH}')
print('✅ SQLite database connection successful!')"

# 🔹 Step 7: Prompt User to Run Main Script
echo "🚀 Setup complete! You can now run the database program with:"
echo "   python3 main.py"
