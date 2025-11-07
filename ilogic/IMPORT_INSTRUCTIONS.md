# iLogic Rules Import Instructions

## Overview

You can import iLogic rules from Inventor in **two ways**:

1. **Structured Folder Export** - Creates a folder hierarchy matching your assembly structure
2. **Single File Export (Markdown)** - Creates one consolidated markdown file

Both methods preserve the assembly structure and component relationships.

---

## Method 1: Structured Folder Export

### Step 1: Export from Inventor

Run the **structured export rule** in Inventor. This will:
- Create a folder structure matching your assembly hierarchy
- Save each rule as: `DocumentName__RuleName.txt`
- Organize by component folders

**Example structure:**
```
Heater Assembly/
  ├── RFSO FLANGE 150LB:1/
  │   ├── RFSO FLANGE 150LB__Flange Size Parameters.txt
  │   └── RFSO FLANGE 150LB__Part Number Assignment.txt
  ├── PIPE SS304 S-5 22.5 DEG.:1/
  │   └── PIPE SS304 S-5 22.5 DEG.__Pipe Parameters.txt
  └── ...
```

### Step 2: Zip the Folder

1. Right-click on the root folder (e.g., "Heater Assembly")
2. Select "Send to" → "Compressed (zipped) folder"
3. This creates a `.zip` file

### Step 3: Import in the App

1. Go to **iLogic** → **Import Markdown** (we'll add structured import button)
2. OR use the **"Import Structured"** option (coming soon)
3. Upload the `.zip` file
4. The app will:
   - Extract the folder structure
   - Parse each `.txt` file
   - Create Assembly → Component → Rule hierarchy
   - Analyze all rules for inconsistencies

---

## Method 2: Single File Export (Markdown)

### Step 1: Export from Inventor

Run the **single file export rule** in Inventor. This will:
- Create one `.md` file with all rules
- Include component paths and rule code
- Format as markdown with code blocks

**Example output:**
```markdown
# Heater Assembly

## Rule: Flange Size Parameters
*Component: [[RFSO FLANGE 150LB:1]]*
*Path: `RFSO FLANGE 150LB:1`*

```vbnet
Sub Main()
    ' Rule code here...
End Sub
```

## Rule: Part Number Assignment
*Component: [[RFSO FLANGE 150LB:1]]*
...
```

### Step 2: Import in the App

1. Go to **iLogic** → **Import Markdown**
2. Click "Choose File" and select your `.md` file
3. Click "Import File"
4. The app will:
   - Parse the markdown structure
   - Extract assembly name from first heading
   - Create components from `[[Component Name]]` markers
   - Extract rules with their code
   - Analyze all rules for inconsistencies

---

## Method 3: Paste Single Rule (Quick Test)

**Use this for:**
- Testing the analysis engine
- Importing a single rule quickly
- When you only have one rule to add

**Steps:**
1. Go to **iLogic** → **Import Code**
2. Enter:
   - **Assembly Name**: e.g., "Heater Assembly"
   - **Rule Name**: e.g., "Flange Size Parameters"
   - **iLogic Code**: Paste your VBA code
3. Click "Import & Analyze"
4. The app will:
   - Create/use the assembly
   - Extract component name from code
   - Create the rule
   - Analyze for inconsistencies

---

## What Happens After Import?

1. **Assembly Created** - Top-level assembly (e.g., "Heater Assembly")
2. **Components Created** - Each component from the structure
3. **Rules Created** - All rules with full code
4. **Analysis Run** - Automatic detection of:
   - Missing part numbers (XXX placeholders)
   - Description mismatches
   - Duplicate part numbers
   - Logic inconsistencies
5. **Inconsistencies Logged** - View in Analysis Dashboard

---

## Viewing Your Imported Rules

1. **Assembly List** - See all assemblies with stats
2. **Assembly Detail** - View components and rules
3. **Component Detail** - See all rules for a component
4. **Rule Detail** - View code, analysis, and part numbers
5. **Analysis Dashboard** - Review all found issues

---

## Tips

- **Start with Markdown Import** - Easiest way to import everything at once
- **Use Structured Import** - When you want to preserve exact folder structure
- **Paste Code** - For quick testing or single rule imports
- **Check Analysis Dashboard** - Always review after import for issues

---

## Troubleshooting

**"Could not parse assembly name"**
- Make sure your markdown file starts with `# Assembly Name`
- Check that the file is valid markdown

**"Component not found"**
- The app extracts component names from code
- If extraction fails, component will be named "Unknown Component"
- You can edit it later in Component Detail

**"No rules imported"**
- Check that your export file contains rule code
- For markdown, ensure rules are in ````vbnet` code blocks
- For structured, ensure `.txt` files contain code

---

## Next Steps

After importing:
1. Review the **Analysis Dashboard** for issues
2. Fix inconsistencies in the rules
3. Use the **Configurator** (coming soon) to simulate rule execution
4. Export organized rules back to Inventor (coming soon)

