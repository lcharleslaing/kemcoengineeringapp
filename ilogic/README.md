# iLogic Rules Management App

A Django app for organizing, analyzing, and managing Inventor iLogic rules. This app helps you:

1. **Organize** rules by assembly structure (matches Inventor hierarchy)
2. **Import** rules from structured folders or markdown files
3. **Analyze** rules for inconsistencies and errors
4. **Track** issues and fixes
5. **Build** configurators to simulate rule execution

## Features

### Import Options

1. **Paste Code** - Manually paste iLogic VBA code
2. **Markdown Import** - Import from single-file markdown export
3. **Structured Import** - Import from folder hierarchy (coming soon)

### Analysis

- **Automatic Detection** of:
  - Missing part numbers (XXX placeholders)
  - Description mismatches (e.g., SS316 code but SS304 description)
  - Duplicate part numbers
  - Logic inconsistencies (mismatched If/End If)
  - Missing conditions

### Organization

- **Assembly** → **Component** → **Rule** hierarchy
- Matches Inventor's assembly structure
- Easy navigation and search

### Configurator (Coming Soon)

- Simulate rule execution
- Generate BOMs based on parameters
- Test different configurations

## Usage

### 1. Create an Assembly

Navigate to iLogic → New Assembly, or import rules (assembly will be created automatically).

### 2. Import Rules

**Option A: Paste Code**
- Go to "Import Code"
- Enter assembly name, rule name, and paste your iLogic VBA code
- The app will automatically:
  - Extract component name from code
  - Detect rule type
  - Extract triggers and part numbers
  - Analyze for inconsistencies

**Option B: Markdown File**
- Use the single-file export rule from Inventor
- Upload the generated .md file
- All rules will be imported with structure preserved

### 3. Review Analysis

- Go to "Analysis Dashboard" to see all issues
- Click on any rule to see detailed analysis
- Issues are categorized by severity (Critical, Warning, Info)

### 4. Fix Issues

- View inconsistency details
- See suggested fixes
- Mark as fixed when resolved

## Data Model

```
Assembly
  └── Component
      └── Rule
          ├── RuleVersion (history)
          └── Inconsistency (issues found)
```

## Export Rules from Inventor

### Structured Export (Folder Hierarchy)

Use the structured export rule to create a folder structure:
```
RootFolder/
  └── ComponentFolder/
      └── DocumentName__RuleName.txt
```

### Single File Export (Markdown)

Use the single file export rule to create one .md file with all rules organized by component.

## Future Enhancements

- [ ] Structured folder import (zip file)
- [ ] Rule execution simulator
- [ ] BOM generator
- [ ] Dependency mapping
- [ ] Automated fix suggestions
- [ ] Export back to Inventor format
- [ ] Version comparison
- [ ] Testing framework

## Technical Details

- **Models**: Assembly, Component, Rule, RuleVersion, Inconsistency, Configurator
- **Analysis**: Pattern matching, regex parsing, logic validation
- **Storage**: JSONField for flexible data (triggers, extracted data, BOMs)

