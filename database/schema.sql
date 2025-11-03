-- Metadata Table
CREATE TABLE Metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    file_uploaded DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lab_id, key)
);

-- GenomicData Table
CREATE TABLE GenomicData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    seq_order INTEGER,
    file_uploaded DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lab_id, key)
);

-- Indexes to speed common lookups
CREATE INDEX IF NOT EXISTS idx_metadata_lab_id ON Metadata(lab_id);
CREATE INDEX IF NOT EXISTS idx_metadata_key ON Metadata(key);

CREATE INDEX IF NOT EXISTS idx_genomic_lab_id ON GenomicData(lab_id);
CREATE INDEX IF NOT EXISTS idx_genomic_key ON GenomicData(key);