# Consolidated local CV versions

The working CV lives in `resume/`. The GitHub version takes precedence for conflicting facts.
This archive retains every distinct source document and PDF from the four local folders,
including uncommitted work. Identical files are stored once. Original folders are untouched.

| Source folder | Files | Unique files stored | Different from working tree | Live additions |
|---|---:|---:|---:|---:|
| Resume 3 | 182 | 169 | 63 | 0 |
| Resume 3_v2_2026-08-14 | 56 | 16 | 22 | 0 |
| Resume_Detailed | 21 | 15 | 6 | 0 |
| Resume | 24 | 8 | 6 | 0 |

## Finding an older version

`manifest.json` maps **every original path** to its archived `stored_at` path and SHA-256.
Folders are deduplicated, so an individual archive folder is not a standalone build.
To reconstruct a complete version in a new directory:

```bash
python resume/scripts/restore_local_version.py 'Resume_Detailed' /tmp/restored-cv
```

Verify all stored content with:

```bash
python resume/scripts/consolidate_local_versions.py --verify
```

## Conflict policy

Local wording, dates, metrics, projects, and templates remain available for the next content review.
Conflicting facts are not silently combined. Local-only files from `Resume 3` extend the live tree.
Older CI workflows are archived as reference rather than activated.
Excluded OS metadata and disposable TeX artifacts are listed in the manifest; `.git` histories remain in the original folders.
