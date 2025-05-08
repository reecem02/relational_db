-- Metadata Table
CREATE TABLE Metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    UNIQUE(lab_id, key)
);

-- GenomicData Table
CREATE TABLE GenomicData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    UNIQUE(lab_id, key)
);