# Qualys BUSINESS_INFORMATION Tag Cleanup Script

This script is designed to safely identify and delete Qualys Asset Tags of type `BUSINESS_INFORMATION` using a **two-stage execution model**:

1. **Discovery & Review phase** – export matching tags to files for inspection  
2. **Deletion phase** – delete only the tags explicitly retained in a reviewed JSON file  

This approach helps prevent accidental deletions by requiring a manual review step before any destructive action is taken.

---

## Overview

The script interacts with the Qualys QPS API to:

- Locate all tags with `ruleType = BUSINESS_INFORMATION`
- Export their IDs and names for offline review
- Allow selective deletion based on an edited JSON file

Execution behaviour depends on whether the `--delete` flag is supplied.

---

## Requirements

- Python **3.9+**
- Network access to the relevant Qualys API endpoint
- A Qualys account with permissions to:
  - Search tags
  - Delete tags

### Python Dependencies

Install required libraries using:

```bash
pip install -r requirements.txt
```

---

## Supported Qualys Pods

The script supports the following Qualys platforms:

- `US01`, `US02`, `US03`, `US04`
- `EU01`, `EU02`, `EU03`
- `UK01`
- `IN01`, `CA01`, `AE01`, `AU01`, `KSA1`
- `PRIVATE`

If `PRIVATE` is specified, the script will prompt for a full API base URL.

---

## Execution Model

### Phase 1 — Discover & Export Tags (Non-Destructive)

This phase queries Qualys and writes two output files:

- `<filename>.json` — full tag data (used later for deletion)
- `<filename>.txt` — human-readable list of tag IDs and names

#### Command

```bash
python tag_cleanup.py   --user <username>   --password <password>   --pod <POD_NAME>   --filename <output_name>
```

#### Example

```bash
python tag_cleanup.py   -u apiuser   -p secret   -pod UK01   -f business_tags
```

#### Output

- `business_tags.json`
- `business_tags.txt`

> No tags are deleted during this phase.

---

### Manual Review Step (Required)

Before proceeding to deletion:

1. Open `<filename>.json`
2. Remove any tag objects you **do not want deleted**
3. Save the file

Only the tags that remain in the JSON file will be deleted in Phase 2.

---

### Phase 2 — Delete Reviewed Tags (Destructive)

This phase:

- Reads tag IDs from the reviewed JSON file
- Issues a delete request to Qualys
- Writes execution output to `<filename>.log`

#### Command

```bash
python tag_cleanup.py   --user <username>   --password <password>   --pod <POD_NAME>   --filename <input_name>   --delete
```

#### Example

```bash
python tag_cleanup.py   -u apiuser   -p secret   -pod UK01   -f business_tags   --delete
```

---

## Output Files Summary

| File | Purpose |
|------|---------|
| `<name>.json` | Source of truth for deletion targets |
| `<name>.txt` | Human-readable review list |
| `<name>.log` | Deletion execution log |

---

## Safety Characteristics

- Two-phase execution prevents accidental deletion
- Human review required before destructive action
- Explicit `--delete` flag required
- No automatic rollback (by design)

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Successful execution |
| `1` | Invalid pod name |
| `2` | API failure or no tags found |

---

## Script Notes

- Tag deletion is performed using a filtered `IN` clause on tag IDs
- Deletion is executed in a single API call
- Authentication uses basic auth over HTTPS
- Credentials are not masked — handle with care

---

## Recommended Workflow

1. Run Phase 1  
2. Review the `.txt` file  
3. Edit the `.json` file  
4. Run Phase 2  
5. Archive outputs  

---

## Disclaimer

This script performs **irreversible deletions** in Qualys.  
Test in non-production environments first and validate results carefully.
