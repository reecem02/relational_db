# Multi-User Limitations and Solutions

**Date:** February 2026  
**Version:** 1.0  
**Audience:** Lab members and project planners  

---

## Overview

This document explains the limitations of using a shared SQLite database with multiple users and recommends solutions.

---

## Current Limitation: Single Writer

### What This Means

**✓ Multiple users CAN:**
- Query the database simultaneously
- Search for data at the same time
- Export results in parallel
- View results

**✗ Only ONE user CAN:**
- Import data at a time
- Modify data (editing/updating)
- Delete records
- Perform write operations

### Why?

SQLite is a **file-based database** that locks the entire database file during write operations. This is fine for single users but problematic for concurrent writers.

**Example Timeline:**

```
Time    User A              Database State    User B
────────────────────────────────────────────────────
10:00   Starts import       LOCKED             (Waiting...)
10:01   Importing...        LOCKED             (Still waiting...)
10:02   Import complete     UNLOCKED           Can now import
10:03                       (available)
```

---

## Problems This Causes

### Problem 1: Import Conflicts

**Scenario:**
- User A starts bulk import of 50 genomes
- User B tries to import 10 genomes
- User B gets error: **"database is locked"**
- User B's import fails

**Impact:** Work is interrupted, frustration

### Problem 2: Data Overwriting

**Scenario:**
- User A updates metadata for UL001
- User B simultaneously updates metadata for UL001
- One person's changes are lost

**Impact:** Data loss and inconsistency

### Problem 3: Performance Degradation

**Scenario:**
- User A is running a complex search
- User B tries to export
- Both operations slow to a crawl

**Impact:** Everyone waits

---

## Current Workarounds

### Workaround 1: Personal Database (Recommended)

**Each lab member maintains their own copy:**

```
Reece's Computer          Lab Server              Colleague's Computer
    ↓                          ↓                          ↓
personal_db.sqlite   →   shared_lab_db.sqlite   →   personal_db.sqlite
                           (shared storage)
```

**Setup:**
1. Each person runs: `git clone https://github.com/reecem02/relational_db.git`
2. Each person has their own `database/fungal_db.sqlite`
3. When needed, manually copy data between databases using export/import

**Pros:**
- ✓ No conflicts
- ✓ Fast performance
- ✓ Data isolation
- ✓ Works with current SQLite setup

**Cons:**
- ✗ Data is duplicated
- ✗ Manual sync required
- ✗ Risk of version mismatches

### Workaround 2: Import Schedule

**Designate import times:**

```
Monday    9:00 AM         Reece imports data
Wednesday 2:00 PM         Dr. Uehling imports data
Friday    4:00 PM         New members import test data
```

**Setup:**
1. Create shared calendar entry
2. Users wait their turn
3. Plan ahead for large imports

**Pros:**
- ✓ Prevents conflicts
- ✓ Centralized data
- ✓ Simple to implement

**Cons:**
- ✗ Inflexible
- ✗ Delays work
- ✗ Requires coordination

### Workaround 3: Queue System

**Users submit import jobs to a queue:**

```
User A: [Queued] UL050-UL060 import
User B: [Running] UL040-UL049 import
User C: [Queued] New metadata update
```

**Implementation:** (Requires development)
- Create `import_queue.py` script
- Users submit jobs, script processes sequentially
- Email notification when complete

**Pros:**
- ✓ Automatic scheduling
- ✓ Scalable approach

**Cons:**
- ✗ Requires new code
- ✗ Moderate complexity

---

## Long-Term Solution: Migration to MySQL

### Why MySQL?

**MySQL is a network database that supports:**
- ✓ Multiple simultaneous writers
- ✓ User authentication (who can edit what)
- ✓ Transaction security
- ✓ Centralized data
- ✓ Built-in access control

### Timeline

**Phase 1 (Current):** SQLite-based personal/scheduled imports  
**Phase 2 (Q3 2026):** MySQL server set up by CQLS  
**Phase 3 (Q4 2026):** Database data migrated to MySQL  
**Phase 4 (2027):** Full lab-wide access via MySQL  

### What Changes for Users

**Before (SQLite):**
```bash
python3 main.py
→ Imports to local database/fungal_db.sqlite
```

**After (MySQL):**
```bash
python3 main.py
→ Prompts for database credentials
→ Connects to server database
→ Imports to central database
→ Users see changes immediately
```

---

## Recommendation for Current Use

For **stable, conflict-free operation**, we recommend:

### For Individual Projects
- Use **Personal Database** (Workaround 1)
- Each person has their own copy
- Best for: Learning, testing, isolated work

### For Lab-Wide Data Sharing
- Use **Import Schedule** (Workaround 2)
- Designate import windows
- Best for: Core datasets that need central storage

### For Large Collaborations
- Request **MySQL transition** (Phase 2)
- Contact Reece M or Dr. Uehling to discuss timeline
- Best for: Lab-wide adoption

---

## Handling "Database Locked" Errors

If you see: **"Error: database is locked"**

### Quick Fixes

1. **Wait 30 seconds and retry**
   - Someone else may be finishing an import
   ```bash
   # Try again after waiting
   python3 main.py
   ```

2. **Check if another process is running**
   - On your machine:
     ```bash
     # Windows
     tasklist | find "python"
     
     # macOS/Linux
     ps aux | grep python
     ```
   - Close any stray `main.py` processes

3. **Reset the database connection**
   - Close Python completely
   - Wait 5 seconds
   - Run again

4. **Contact administrator**
   - If using shared database on server
   - Ask Reece M to check what's locked

### If Using a Shared Database

```bash
# Wait before retrying (exponential backoff)
Wait 10 seconds → try
Wait 30 seconds → try
Wait 60 seconds → try
→ If still locked, contact Reece M
```

---

## Data Safety Precautions

### Backup Your Data

**Personal copy:**
```bash
# Copy your SQLite file to a safe location
cp database/fungal_db.sqlite backups/fungal_db.backup.sqlite
```

**Export everything:**
```bash
# (Run from database CLI)
# Search: * (search all)
# Export: CSV
→ Have readable backup in spreadsheet form
```

### Shared Database

- Weekly automated backups (contact sys admin)
- Keep exports of important data
- Document data sources

---

## Migration Checklist: When MySQL Becomes Available

- [ ] Back up current SQLite database
- [ ] Export all data to CSV as reference
- [ ] Test with MySQL development system
- [ ] Coordinate migration timing with lab
- [ ] Update installation/quick start guides
- [ ] Train lab members on new system
- [ ] Archive old SQLite databases

---

## FAQ

**Q: Can I switch to personal database later?**  
A: Yes! Export your data as CSV, set up new personal database, re-import.

**Q: What if I accidentally lock the database?**  
A: Wait 30 seconds for automatic timeout, or restart your Python process.

**Q: Can we have MySQL now instead of later?**  
A: Contact Reece M or Dr. Uehling. May require resources/approval. Current workarounds use SQLite by design.

**Q: How do I know if someone else is using the database?**  
A: No built-in indicator yet. Coordinate via Discord/email.

**Q: Can I "force" unlock the database?**  
A: Not recommended (data corruption risk). Use timeouts instead.

---

## Contact & Support

- **Technical Issues:** Reece M (Discord - Uehling Lab server)
- **MySQL Migration Timeline:** Dr. Uehling
- **Server Access:** CQLS (cqls@oregonstate.edu)

---

