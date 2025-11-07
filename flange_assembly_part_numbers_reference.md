# Flange Assembly Part Numbers Reference

## Overview
This document lists all part number assignments for multiple components in a flange assembly based on:
- Flange Size (1.5", 2", 2.5", 3", 4", 6", 8", 10", 12")
- Material: SS304 or SS316
- SS316_FLANGES flag (True/False) - for SS316 only

**Components:**
1. Flange 150lb-02:1
2. PIPE SS304 S-5 22.5 DEG.:1
3. PIPE SS304 S-5 22.5 AND 45 DEG.:1
4. RFSO FLANGE 150LB:1

---

## Issues Found in Code

### ⚠️ Critical Issues:

1. **SS316 Descriptions Still Say "SS304"**: When MATERIAL = "SS316", many descriptions still incorrectly say "SS304" instead of "SS316"
   - Flange 150lb-02:1 descriptions are correct for SS316_FLANGES = True, but wrong for SS316_FLANGES = False
   - RFSO FLANGE 150LB:1 descriptions always say "SS304" even when MATERIAL = "SS316"

2. **Missing Part Numbers**: 
   - SS316, 12" size: Flange 150lb-02:1 = "800-08-XXX" (placeholder)
   - SS316, 12" size: PIPE components = "910-03-XXX" (placeholder)

3. **PIPE Components**: Use same part numbers regardless of SS316_FLANGES flag (only MATERIAL matters)

---

## Part Number Tables by Component

### Component 1: Flange 150lb-02:1

#### SS304 Material
| Size | Part Number | Description |
|------|-------------|-------------|
| 1.5" | 800-08-009 | FLANGE, SS304, 1/2" PLT., 1-1/2" |
| 2" | 800-08-007 | FLANGE, SS304, 1/2" PLT., 2" |
| 2.5" | 800-08-008 | FLANGE, SS304, 1/2" PLT., 2-1/2" |
| 3" | 800-08-001 | FLANGE, SS304, 1/2" PLT., 3" |
| 4" | 800-08-002 | FLANGE, SS304, 1/2" PLT., 4" |
| 6" | 800-08-004 | FLANGE, SS304, 1/2" PLT., 6" |
| 8" | 800-08-005 | FLANGE, SS304, 1/2" PLT., 8" |
| 10" | 800-08-006 | FLANGE, SS304, 1/2" PLT., 10" |
| 12" | 800-08-014 | FLANGE, SS304, 1/2" PLT., 12" |

#### SS316 Material (SS316_FLANGES = False)
| Size | Part Number | Description | ⚠️ Issue |
|------|-------------|-------------|----------|
| 1.5" | 800-08-009 | FLANGE, SS304, 1/2" PLT., 1-1/2" | Description says SS304, should be SS316 |
| 2" | 800-08-007 | FLANGE, SS304, 1/2" PLT., 2" | Description says SS304, should be SS316 |
| 2.5" | 800-08-008 | FLANGE, SS304, 1/2" PLT., 2-1/2" | Description says SS304, should be SS316 |
| 3" | 800-08-001 | FLANGE, SS304, 1/2" PLT., 3" | Description says SS304, should be SS316 |
| 4" | 800-08-002 | FLANGE, SS304, 1/2" PLT., 4" | Description says SS304, should be SS316 |
| 6" | 800-08-004 | FLANGE, SS304, 1/2" PLT., 6" | Description says SS304, should be SS316 |
| 8" | 800-08-005 | FLANGE, SS304, 1/2" PLT., 8" | Description says SS304, should be SS316 |
| 10" | 800-08-006 | FLANGE, SS304, 1/2" PLT., 10" | Description says SS304, should be SS316 |
| 12" | 800-08-014 | FLANGE, SS304, 1/2" PLT., 12" | Description says SS304, should be SS316 |

**Note:** Part numbers are IDENTICAL to SS304, but descriptions are wrong.

#### SS316 Material (SS316_FLANGES = True)
| Size | Part Number | Description |
|------|-------------|-------------|
| 1.5" | 800-08-029 | FLANGE, SS316, 1/2" PLT., 1-1/2" |
| 2" | 800-08-020 | FLANGE, SS316, 1/2" PLT., 2" |
| 2.5" | 800-01-036 | FLANGE, SS316, 1/2" PLT., 2-1/2" |
| 3" | 800-08-034 | FLANGE, SS316, 1/2" PLT., 3" |
| 4" | 800-01-035 | FLANGE, SS316, 1/2" PLT., 4" |
| 6" | 800-08-022 | FLANGE, SS316, 1/2" PLT., 6" |
| 8" | 800-08-024 | FLANGE, SS316, 1/2" PLT., 8" |
| 10" | 800-08-034 | FLANGE, SS316, 1/2" PLT., 10" |
| 12" | 800-08-XXX | FLANGE, SS316, 1/2" PLT., 12" | ⚠️ Missing part number |

---

### Component 2 & 3: PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1

**Note:** Both pipe components use the SAME part numbers.

#### SS304 Material
| Size | Part Number | Used By Both Components |
|------|-------------|-------------------------|
| 1.5" | 910-01-083 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 2" | 910-01-082 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 2.5" | 910-01-101 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 3" | 910-01-111 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 4" | 910-01-081 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 6" | 910-01-079 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 8" | 910-01-080 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 10" | 910-01-076 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 12" | 910-01-120 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |

#### SS316 Material (Both SS316_FLANGES = False and True)
**Note:** PIPE components use the SAME part numbers regardless of SS316_FLANGES flag.

| Size | Part Number | Used By Both Components |
|------|-------------|-------------------------|
| 1.5" | 910-03-042 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 2" | 910-03-043 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 2.5" | 910-03-031 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 3" | 910-03-046 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 4" | 910-03-051 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 6" | 910-03-038 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 8" | 910-03-050 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 10" | 910-03-036 | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 |
| 12" | 910-03-XXX | PIPE SS304 S-5 22.5 DEG.:1 & PIPE SS304 S-5 22.5 AND 45 DEG.:1 | ⚠️ Missing part number |

---

### Component 4: RFSO FLANGE 150LB:1

#### SS304 Material
| Size | Part Number | Description |
|------|-------------|-------------|
| 1.5" | 800-02-010 | FLANGE, SS304, RFSO, 1-1/2" |
| 2" | 800-02-007 | FLANGE, SS304, RFSO, 2" |
| 2.5" | 800-02-016 | FLANGE, SS304, RFSO, 2-1/2" |
| 3" | 800-02-001 | FLANGE, SS304, RFSO, 3" |
| 4" | 800-02-002 | FLANGE, SS304, RFSO, 4" |
| 6" | 800-02-004 | FLANGE, SS304, RFSO, 6" |
| 8" | 800-02-011 | FLANGE, SS304, RFSO, 8" |
| 10" | 800-02-017 | FLANGE, SS304, RFSO, 10" |
| 12" | 800-02-013 | FLANGE, SS304, RFSO, 12" |

#### SS316 Material (SS316_FLANGES = False)
| Size | Part Number | Description | ⚠️ Issue |
|------|-------------|-------------|----------|
| 1.5" | 800-02-010 | FLANGE, SS304, RFSO, 1-1/2" | Description says SS304, should be SS316 |
| 2" | 800-02-007 | FLANGE, SS304, RFSO, 2" | Description says SS304, should be SS316 |
| 2.5" | 800-02-016 | FLANGE, SS304, RFSO, 2-1/2" | Description says SS304, should be SS316 |
| 3" | 800-02-001 | FLANGE, SS304, RFSO, 3" | Description says SS304, should be SS316 |
| 4" | 800-02-002 | FLANGE, SS304, RFSO, 4" | Description says SS304, should be SS316 |
| 6" | 800-02-004 | FLANGE, SS304, RFSO, 6" | Description says SS304, should be SS316 |
| 8" | 800-02-011 | FLANGE, SS304, RFSO, 8" | Description says SS304, should be SS316 |
| 10" | 800-02-017 | FLANGE, SS304, RFSO, 10" | Description says SS304, should be SS316 |
| 12" | 800-02-013 | FLANGE, SS304, RFSO, 12" | Description says SS304, should be SS316 |

**Note:** Part numbers are IDENTICAL to SS304, but descriptions are wrong.

#### SS316 Material (SS316_FLANGES = True)
| Size | Part Number | Description | ⚠️ Issue |
|------|-------------|-------------|----------|
| 1.5" | 800-02-010 | FLANGE, SS304, RFSO, 1-1/2" | Description says SS304, should be SS316 |
| 2" | 800-02-007 | FLANGE, SS304, RFSO, 2" | Description says SS304, should be SS316 |
| 2.5" | 800-02-016 | FLANGE, SS304, RFSO, 2-1/2" | Description says SS304, should be SS316 |
| 3" | 800-02-001 | FLANGE, SS304, RFSO, 3" | Description says SS304, should be SS316 |
| 4" | 800-02-002 | FLANGE, SS304, RFSO, 4" | Description says SS304, should be SS316 |
| 6" | 800-02-004 | FLANGE, SS304, RFSO, 6" | Description says SS304, should be SS316 |
| 8" | 800-02-011 | FLANGE, SS304, RFSO, 8" | Description says SS304, should be SS316 |
| 10" | 800-02-017 | FLANGE, SS304, RFSO, 10" | Description says SS304, should be SS316 |
| 12" | 800-02-013 | FLANGE, SS304, RFSO, 12" | Description says SS304, should be SS316 |

**Note:** Part numbers are IDENTICAL to SS304, but descriptions are wrong.

---

## Complete Assembly Reference by Size

### 1.5" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-009
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-083
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-083
- **RFSO FLANGE 150LB:1**: 800-02-010

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-009 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-042
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-042
- **RFSO FLANGE 150LB:1**: 800-02-010 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-029
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-042
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-042
- **RFSO FLANGE 150LB:1**: 800-02-010 ⚠️ (same as SS304, description wrong)

### 2" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-007
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-082
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-082
- **RFSO FLANGE 150LB:1**: 800-02-007

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-007 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-043
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-043
- **RFSO FLANGE 150LB:1**: 800-02-007 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-020
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-043
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-043
- **RFSO FLANGE 150LB:1**: 800-02-007 ⚠️ (same as SS304, description wrong)

### 2.5" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-008
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-101
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-101
- **RFSO FLANGE 150LB:1**: 800-02-016

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-008 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-031
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-031
- **RFSO FLANGE 150LB:1**: 800-02-016 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-01-036
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-031
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-031
- **RFSO FLANGE 150LB:1**: 800-02-016 ⚠️ (same as SS304, description wrong)

### 3" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-001
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-111
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-111
- **RFSO FLANGE 150LB:1**: 800-02-001

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-001 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-046
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-046
- **RFSO FLANGE 150LB:1**: 800-02-001 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-034
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-046
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-046
- **RFSO FLANGE 150LB:1**: 800-02-001 ⚠️ (same as SS304, description wrong)

### 4" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-002
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-081
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-081
- **RFSO FLANGE 150LB:1**: 800-02-002

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-002 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-051
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-051
- **RFSO FLANGE 150LB:1**: 800-02-002 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-01-035
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-051
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-051
- **RFSO FLANGE 150LB:1**: 800-02-002 ⚠️ (same as SS304, description wrong)

### 6" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-004
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-079
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-079
- **RFSO FLANGE 150LB:1**: 800-02-004

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-004 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-038
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-038
- **RFSO FLANGE 150LB:1**: 800-02-004 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-022
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-038
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-038
- **RFSO FLANGE 150LB:1**: 800-02-004 ⚠️ (same as SS304, description wrong)

### 8" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-005
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-080
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-080
- **RFSO FLANGE 150LB:1**: 800-02-011

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-005 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-050
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-050
- **RFSO FLANGE 150LB:1**: 800-02-011 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-024
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-050
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-050
- **RFSO FLANGE 150LB:1**: 800-02-011 ⚠️ (same as SS304, description wrong)

### 10" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-006
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-076
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-076
- **RFSO FLANGE 150LB:1**: 800-02-017

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-006 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-036
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-036
- **RFSO FLANGE 150LB:1**: 800-02-017 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-034
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-036
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-036
- **RFSO FLANGE 150LB:1**: 800-02-017 ⚠️ (same as SS304, description wrong)

### 12" Flange Size

#### SS304
- **Flange 150lb-02:1**: 800-08-014
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-01-120
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-01-120
- **RFSO FLANGE 150LB:1**: 800-02-013

#### SS316 (SS316_FLANGES = False)
- **Flange 150lb-02:1**: 800-08-014 ⚠️ (same as SS304, description wrong)
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-XXX ⚠️ Missing part number
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-XXX ⚠️ Missing part number
- **RFSO FLANGE 150LB:1**: 800-02-013 ⚠️ (same as SS304, description wrong)

#### SS316 (SS316_FLANGES = True)
- **Flange 150lb-02:1**: 800-08-XXX ⚠️ Missing part number
- **PIPE SS304 S-5 22.5 DEG.:1**: 910-03-XXX ⚠️ Missing part number
- **PIPE SS304 S-5 22.5 AND 45 DEG.:1**: 910-03-XXX ⚠️ Missing part number
- **RFSO FLANGE 150LB:1**: 800-02-013 ⚠️ (same as SS304, description wrong)

---

## Decision Tree

```
Is MATERIAL = "SS304"?
├─ YES → Use SS304 part numbers for all components
│
└─ NO (SS316)
   ├─ Is SS316_FLANGES = True?
   │  ├─ YES → Use SS316_FLANGES = True part numbers
   │  │        (Different Flange 150lb-02:1 part numbers)
   │  │        (Same PIPE and RFSO part numbers as SS316_FLANGES = False)
   │  └─ NO → Use SS316_FLANGES = False part numbers
   │           (Same Flange 150lb-02:1 part numbers as SS304)
   │           (Different PIPE part numbers from SS304)
   │           (Same RFSO part numbers as SS304)
```

---

## Summary of Issues

1. **Description Errors**: When MATERIAL = "SS316", descriptions incorrectly say "SS304" in:
   - Flange 150lb-02:1 (for SS316_FLANGES = False only)
   - RFSO FLANGE 150LB:1 (for both SS316_FLANGES = False and True)

2. **Missing Part Numbers**: 
   - SS316, 12" size, SS316_FLANGES = True: Flange 150lb-02:1 = "800-08-XXX"
   - SS316, 12" size: PIPE components = "910-03-XXX" (both SS316_FLANGES flags)

3. **Duplicate Part Numbers**: 
   - Flange 150lb-02:1 uses same part numbers for SS304 and SS316 (SS316_FLANGES = False)
   - RFSO FLANGE 150LB:1 uses same part numbers for SS304 and SS316 (both flags)

4. **PIPE Components**: Use same part numbers regardless of SS316_FLANGES flag (only MATERIAL matters)

