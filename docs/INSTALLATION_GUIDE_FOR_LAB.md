# Installation Guide for Lab Members

**Date:** February 2026  
**Version:** 1.0 (Production Ready)  
**Audience:** Uehling Lab members with varying technical experience

---

## Overview

This guide walks you through setting up the Fungal Research Database on your personal machine or a shared lab system. The database allows you to store, search, and export fungal genomic data and metadata in an organized, queryable format.

**Time Required:** 15-20 minutes  
**Prerequisites:** Administrative access to install software (for your personal machine)

---

## Important Note: Single vs. Shared Database Usage

### Personal Database (Recommended for Individual Use)
- Each lab member has their own copy of the database
- Can import and modify data independently
- No conflicts with other users
- Best for: Individual project work, learning the tool

### Shared Database (Limitations - Read Below)
- Multiple lab members can **query** data simultaneously
- **Only one person can import/modify at a time** ⚠️
- Database locks during write operations
- Can result in "database is locked" errors
- Best for: Centralized data storage where most users only search/export

**Recommendation:** Start with a personal database. If you need centralized shared access, contact Reece M to discuss transition to MySQL (coming in future version).

---

## Step 1: Install Python

The database runs on Python 3.8 or newer.

### Windows
1. Download Python from https://www.python.org/downloads/
2. Run the installer
3. **Important:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify installation:
   - Open Command Prompt (search "cmd")
   - Type: `python --version`
   - Should display: `Python 3.8.x` (or newer)

### macOS
1. Download Python from https://www.python.org/downloads/
2. Run the installer and follow prompts
3. Verify installation:
   - Open Terminal
   - Type: `python3 --version`
   - Should display: `Python 3.8.x` (or newer)

### Linux
```bash
sudo apt-get update
sudo apt-get install python3.8 python3-pip
python3 --version
```

---

## Step 2: Install Git

Git allows you to download and update the project.

### Windows
1. Download Git from https://git-scm.com/downloads
2. Run the installer
3. Accept default options
4. Verify installation:
   - Open Command Prompt
   - Type: `git --version`
   - Should display a version number

### macOS
1. Download Git from https://git-scm.com/downloads
2. Run the installer and follow prompts
3. Verify installation:
   - Open Terminal
   - Type: `git --version`

### Linux
```bash
sudo apt-get install git
git --version
```

---

## Step 3: Clone the Repository

This downloads the database project to your computer.

### All Platforms

1. Open Terminal/Command Prompt in your desired location
2. Run:
   ```bash
   git clone https://github.com/reecem02/relational_db.git
   ```
3. This creates a folder named `relational_db`

---

## Step 4: Install Python Dependencies

The database requires additional Python libraries.

### Windows (Command Prompt)
```bash
cd relational_db
pip install -r requirements.txt
```

### macOS/Linux (Terminal)
```bash
cd relational_db
pip3 install -r requirements.txt
```

**If you see permission errors:**
```bash
pip install --user -r requirements.txt
```

Wait for installation to complete (this may take 2-3 minutes).

---

## Step 5: Initialize the Database

The database file must be created before first use.

1. Navigate to the `database` folder in the project
2. If you don't see a file named `fungal_db.sqlite`, create it:
   - **Windows:** Right-click in the folder → New → File → Name it `fungal_db.sqlite`
   - **macOS/Linux:** 
     ```bash
     cd database
     touch fungal_db.sqlite
     cd ..
     ```

---

## Step 6: Run the Program

You're ready to use the database!

### Windows (Command Prompt)
```bash
python main.py
```

### macOS/Linux (Terminal)
```bash
python3 main.py
```

You should see a menu like:
```
Welcome to the Fungal Research Database
1) Import Data
2) Search Data
3) Delete Data
4) Help
5) Database Information
6) Exit

Enter your choice:
```

---

## Keeping Your Installation Updated

To get the latest features and bug fixes:

```bash
git pull origin main
```

Run this from inside the `relational_db` folder.

---

## Troubleshooting

### "Python is not recognized"
- Reinstall Python and **check "Add Python to PATH"**
- Restart Command Prompt/Terminal after installing Python

### "No module named 'pandas'"
- Run: `pip install -r requirements.txt` again
- Or try: `pip install --user pandas` (then repeat for other missing modules)

### "git is not recognized"
- Reinstall Git
- Restart Command Prompt/Terminal

### "Database is locked" error
- Only one person can import at a time on a shared database
- Wait a few minutes and try again
- If using a personal database, check that the program from a previous session isn't still running

### "fungal_db.sqlite not found"
- Navigate to the `database` folder
- Create the file (see Step 5)
- Or, run the program once—it may auto-create the file

### Still having issues?
Contact Reece M (Discord: Uehling Lab server) with:
- Error message you're seeing
- What you were trying to do
- Your operating system

---

## Next Steps

Once installed, see:
- **QUICK_START_GUIDE.md** - Get started in 5 minutes
- **README.md** - Full feature documentation
- **MANUAL_TESTING_GUIDE.md** - Test with example data

---
