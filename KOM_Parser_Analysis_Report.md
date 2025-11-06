# KOM File Structure Analysis Report

**Date:** November 6, 2025  
**Files Analyzed:** 9 KOM Excel files  
**Purpose:** Identify patterns and variations to improve parser robustness

## Executive Summary

Analysis of 9 KOM Excel files revealed consistent structural patterns with some positional variations. The parser has been updated to handle these variations dynamically while providing validation warnings when expected sections are not found.

## Key Findings

### 1. Tanks Section - **CONSISTENT**

**Pattern:**
- Tanks consistently found at rows 77, 79, 81
- Tank markers: `#1:`, `#2:`, `#3:` in column 1
- Data columns are consistent across all files:
  - Column 3: Type (e.g., "HW")
  - Column 5: Diameter (e.g., "84", "84\"")
  - Column 7: Height (e.g., "15", "12")
  - Column 9: GA (e.g., "STD")
  - Column 11: Material (e.g., "304", "316")

**Variations:**
- Some files have empty tank rows (expected - not all jobs have 3 tanks)
- Diameter format varies: "84" vs "84\"" (both handled)

**Parser Update:**
- Enhanced tank detection to verify marker presence
- Added validation warning if no tanks found
- Improved handling of empty tank rows

---

### 2. Line Items Section - **VARIABLE START/END**

**Pattern:**
- Description column: **Consistently column 4**
- Value columns: 6, 7, 8, 9, 10, 11 (with 6 being most common)

**Variations:**
- **Start rows vary:** 124, 125, 127, 129
  - "TO BE COMPLETED BY APPS" section found at: 122, 123, 125, 127
- **End rows vary:** 133, 134, 137, 138, 141
  - "LABOR HOURS" section found at: 133, 134, 137, 138, 141

**Parser Update:**
- Dynamic section finding for "TO BE COMPLETED BY APPS" (searches rows 120-135)
- Dynamic section finding for "LABOR HOURS" (searches rows 130-145)
- Validation warnings if sections not found
- Fallback to default rows if dynamic search fails

---

### 3. Labor Hours Section - **VARIABLE POSITION**

**Pattern:**
- Values consistently in column 4
- Structure: HR, Pkg, Fab, Wiring on consecutive rows

**Variations:**
- **Section header position:** Rows 133, 134, 137, 138, 141
- Data rows follow immediately after header

**Parser Update:**
- Dynamic finding of LABOR HOURS section
- Relative positioning for HR, Pkg, Fab, Wiring based on header location
- Fallback to fixed rows (142-145) if dynamic search fails

---

### 4. Equipment Required Section - **RELATIVE TO LABOR HOURS**

**Pattern:**
- Equipment data on same rows as Pkg, Fab, Wiring
- Columns consistent:
  - Column 7: Qty
  - Column 8: KN Number
  - Column 9: Description

**Parser Update:**
- Uses dynamic rows based on LABOR HOURS position
- Ensures equipment data aligns with labor hours rows

---

### 5. Capital Section - **VARIABLE POSITION**

**Pattern:**
- Fields: Sell Price, Equip Cost, Freight, StartUp Cost, Protect Cost, Net Revenue
- Values typically in column 3

**Variations:**
- **Section header position:** Rows 139, 140, 143, 144, 147
- Field positions relative to header vary

**Parser Update:**
- Dynamic finding of CAPITAL section (searches rows 135-150)
- Relative positioning for fields based on header location
- Fallback to fixed rows if dynamic search fails

---

## Section Position Summary

| Section | Consistent? | Row Variations | Column Consistency |
|---------|------------|----------------|-------------------|
| TANKS | ✅ Yes | 75 (header), 77/79/81 (data) | ✅ Columns 3, 5, 7, 9, 11 |
| TO BE COMPLETED BY APPS | ⚠️ Variable | 122, 123, 125, 127 | ✅ Column 4 (description) |
| LABOR HOURS | ⚠️ Variable | 133, 134, 137, 138, 141 | ✅ Column 4 (values) |
| CAPITAL | ⚠️ Variable | 139, 140, 143, 144, 147 | ✅ Column 3 (values) |
| Line Items | ⚠️ Variable | Start: 124-129, End: 133-141 | ✅ Column 4 (desc), 6-11 (values) |

---

## Parser Improvements Implemented

### 1. Dynamic Section Finding
- All variable sections now use dynamic search before falling back to defaults
- Search ranges based on observed variations in the report

### 2. Validation Warnings
- Parser now tracks `_validation_warnings` array
- Flags when:
  - Expected sections are not found
  - No tanks found with markers
  - Proposal number missing
  - No line items found

### 3. Robustness Enhancements
- Tanks: Enhanced marker detection (#1:, #2:, #3:)
- Line Items: Dynamic start/end detection
- Labor Hours: Relative positioning based on header
- Equipment: Aligned with labor hours rows
- Capital: Dynamic section finding with relative positioning

---

## Recommendations

### For Future Files
1. **Consistent Formatting:** While parser handles variations, consistent section positioning would improve reliability
2. **Tank Markers:** Always use #1:, #2:, #3: markers for tanks (parser depends on these)
3. **Section Headers:** Keep section headers in column 1 for reliable detection

### For Parser Maintenance
1. **Monitor Warnings:** Review `_validation_warnings` after each import to catch format changes
2. **Update Ranges:** If new files show sections outside current search ranges, expand them
3. **Test Coverage:** Add tests for edge cases (missing sections, empty tanks, etc.)

---

## Files Analyzed

1. `35371 KOM AND OC FORM.xlsx`
2. `KOM AND OC FORM - 35042.xlsx`
3. `KOM AND OC FORM - 35411-R4.xlsx`
4. `KOM AND OC FORM - 35167.xlsx`
5. `35359 KOM AND OC FORM.xlsx`
6. `35140 KOM AND OC FORM.xlsx`
7. `35397 KOM AND OC FORM.xlsx`
8. `34489 KOM AND OC FORM.xlsx`
9. `35282 KOM AND OC FORM.xlsx`

---

## Technical Details

### Value Column Distribution
- **Column 6:** Used in all 9 files (primary value column)
- **Column 7:** Used in 3 files
- **Column 8:** Used in 6 files
- **Column 9:** Used in 6 files
- **Column 10:** Used in 5 files
- **Column 11:** Used in 2 files

### Tank Column Consistency
- All tanks use columns: 3, 5, 7, 9, 11
- No variation observed in column positions

---

## Conclusion

The parser has been significantly improved to handle the observed variations while maintaining accuracy. The addition of validation warnings provides visibility into parsing issues, allowing for quick identification of format changes or missing data.

**Status:** ✅ Parser updated and ready for production use with validation monitoring.

