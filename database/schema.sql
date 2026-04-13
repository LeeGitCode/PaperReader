PRAGMA foreign_keys = ON;

-- Core paper records.
CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    aka_name TEXT,
    authors_display TEXT,
    venue TEXT,
    pub_year INTEGER,
    pub_month INTEGER CHECK (pub_month BETWEEN 1 AND 12),
    status TEXT NOT NULL DEFAULT 'to_read'
        CHECK (status IN ('to_read', 'reading', 'completed')),
    priority INTEGER NOT NULL DEFAULT 3
        CHECK (priority BETWEEN 1 AND 5),
    pdf_path TEXT,
    pdf_url TEXT,
    code_url TEXT,
    notes TEXT,
    last_read_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    arxiv_id TEXT,
    doi TEXT,
    is_archived INTEGER NOT NULL DEFAULT 0
        CHECK (is_archived IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_arxiv_id
    ON papers(arxiv_id)
    WHERE arxiv_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_papers_doi
    ON papers(doi)
    WHERE doi IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_papers_status_priority_updated
    ON papers(status, priority DESC, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_papers_pub_year
    ON papers(pub_year DESC);

CREATE INDEX IF NOT EXISTS idx_papers_last_read_at
    ON papers(last_read_at DESC);

CREATE INDEX IF NOT EXISTS idx_papers_aka_name
    ON papers(aka_name);

-- Tag families keep the tag system extensible:
-- examples: area, method, task, system.
CREATE TABLE IF NOT EXISTS tag_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Individual tags. normalized_name helps deduplicate case/style variants.
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_group_id INTEGER,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    color TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tag_group_id) REFERENCES tag_groups(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_tags_group_normalized_name
    ON tags(tag_group_id, normalized_name);

CREATE INDEX IF NOT EXISTS idx_tags_normalized_name
    ON tags(normalized_name);

-- Many-to-many mapping between papers and tags.
CREATE TABLE IF NOT EXISTS paper_tags (
    paper_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (paper_id, tag_id),
    FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_paper_tags_tag_id_paper_id
    ON paper_tags(tag_id, paper_id);

-- Keep updated_at fresh on every paper update.
CREATE TRIGGER IF NOT EXISTS trg_papers_updated_at
AFTER UPDATE ON papers
FOR EACH ROW
BEGIN
    UPDATE papers
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
