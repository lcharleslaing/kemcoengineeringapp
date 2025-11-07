# iLogic App Structure Proposal

## Recommended Approach: **Structured/Hierarchical**

### Why Structured is Better:
1. **Matches Inventor Structure** - Rules are organized by component/assembly in Inventor
2. **Easier Navigation** - Find rules by component/assembly hierarchy
3. **Better Analysis** - Can analyze rules at component, assembly, or global level
4. **Relationship Tracking** - See which rules affect which components
5. **Version Control** - Track changes per component/assembly
6. **Configurator Building** - Natural hierarchy for simulation
7. **Error Isolation** - Identify which component has issues

---

## Proposed Data Model

### Core Models:

```
Assembly (Top Level)
├── name: "Heater Assembly"
├── description
├── inventor_file_path
└── Components (related)

Component
├── assembly (FK to Assembly)
├── name: "RFSO FLANGE 150LB:1"
├── component_type: "Flange", "Pipe", "Tank", etc.
├── inventor_instance_name
└── Rules (related)

Rule
├── component (FK to Component)
├── rule_name: "Flange Size Parameters"
├── rule_code (full iLogic VBA code)
├── rule_type: "Parameter", "iProperty", "Part Number", etc.
├── triggers: ["FlangeSize", "MATERIAL"]
├── dependencies: (other rules/components it depends on)
├── created_at, updated_at
└── Versions (related)

RuleVersion
├── rule (FK to Rule)
├── version_number
├── code_snapshot
├── change_notes
└── created_at

Inconsistency
├── rule (FK to Rule)
├── inconsistency_type: "Description Mismatch", "Missing Part Number", "Duplicate Part Number", etc.
├── severity: "Critical", "Warning", "Info"
├── description
├── affected_components
├── suggested_fix
└── status: "Open", "Fixed", "Ignored"

Configurator
├── assembly (FK to Assembly)
├── name: "Heater Configurator"
├── input_parameters (JSON): {FlangeSize: 2, MATERIAL: "SS316", SS316_FLANGES: False}
├── output_bom (JSON): Generated BOM with part numbers
└── simulation_results (JSON)
```

---

## Proposed App Structure

```
ilogic/
├── models.py          # Assembly, Component, Rule, RuleVersion, Inconsistency, Configurator
├── views.py           # CRUD + Analysis + Configurator
├── forms.py           # Forms for importing/editing rules
├── admin.py           # Django admin registration
├── urls.py            # URL routing
├── utils.py           # Analysis functions, parser, configurator engine
├── templates/
│   └── ilogic/
│       ├── assembly_list.html
│       ├── assembly_detail.html
│       ├── component_detail.html
│       ├── rule_detail.html
│       ├── rule_edit.html
│       ├── inconsistency_list.html
│       ├── configurator.html
│       └── analysis_report.html
└── migrations/
```

---

## Features

### 1. Import & Organization
- **Import from file** - Upload iLogic .vb files or paste code
- **Auto-detect structure** - Parse component names from code
- **Manual organization** - Drag-and-drop or assign to components
- **Bulk import** - Import multiple rules at once

### 2. Analysis & Error Detection
- **Pattern matching** - Find duplicate part numbers
- **Description validation** - Check MATERIAL matches in descriptions
- **Missing value detection** - Find "XXX" placeholders
- **Logic consistency** - Compare similar rules for inconsistencies
- **Dependency analysis** - Map rule dependencies

### 3. Configurator/Simulator
- **Parameter input form** - Enter FlangeSize, MATERIAL, flags
- **Rule execution simulation** - Simulate iLogic rule execution
- **BOM generation** - Generate BOM based on simulated rules
- **What-if scenarios** - Test different parameter combinations
- **Export results** - Export BOM to Excel/CSV

### 4. Review & Fix
- **Inconsistency dashboard** - All errors in one place
- **Fix suggestions** - AI/pattern-based suggestions
- **Version comparison** - Compare rule versions
- **Approval workflow** - Mark fixes as approved

---

## Alternative: Single File Approach

If you prefer a single file approach, we could use:

```
RuleFile
├── file_name
├── file_path
├── full_code (all rules in one file)
├── parsed_rules (JSON structure)
└── analysis_results
```

**Pros:**
- Simpler initial structure
- Matches how rules might be stored in files
- Easier bulk operations

**Cons:**
- Harder to navigate large files
- Difficult to track which rules affect which components
- Less intuitive for configurator building
- Harder to version individual rules

---

## Recommendation

**Use Structured Approach** because:
1. You mentioned "Heater & Tank assemblies" - these are natural top-level structures
2. Rules are component-specific (e.g., "RFSO FLANGE 150LB:1", "PIPE SS304 S-5 22.5 DEG.:1")
3. Easier to build configurator that matches Inventor's assembly structure
4. Better for long-term maintenance and analysis
5. Can still export to single file format when needed

---

## Implementation Plan

### Phase 1: Basic Structure
1. Create Django app `ilogic`
2. Models: Assembly, Component, Rule
3. Basic CRUD views
4. Import functionality (paste code or upload file)

### Phase 2: Analysis
1. Rule parser to extract component names, parameters, part numbers
2. Inconsistency detection
3. Analysis dashboard

### Phase 3: Configurator
1. Parameter input interface
2. Rule execution engine
3. BOM generation
4. Export functionality

### Phase 4: Advanced Features
1. Version control
2. Dependency mapping
3. Automated fix suggestions
4. Testing framework

---

## Questions for You:

1. **Do you have existing iLogic files** we should import, or will you paste code?
2. **Assembly structure** - Do you have a standard naming convention for assemblies?
3. **Rule organization** - Are rules typically in one file per assembly, or multiple files?
4. **Priority** - Which is most urgent: organizing existing rules, finding errors, or building configurator?

Let me know your preference and I'll start building the structured app!

