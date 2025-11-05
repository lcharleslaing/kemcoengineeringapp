# Dashboard Apps Management Guide

## Understanding Dashboard Apps

The Django admin has a **Dashboard Apps** section where you can manage all apps that appear on the main dashboard.

## Two Types of Apps

### 1. **Available Apps** (Built-in, Active)
These appear in the top "Available Apps" section with green "Active" badges:
- My Calendar
- My Budget  
- My Meds

**Settings for these:**
- `is_active = True`
- `show_in_dashboard = False` (they're hardcoded in the template)

### 2. **Featured Apps** (Coming Soon)
These appear in the "Featured Apps" section with blue "Coming Soon" badges:
- Immigration Process
- My Credit History
- My Original Music
- My Taxes

**Settings for these:**
- `is_active = True`
- `show_in_dashboard = True` (dynamically loaded from database)

## Current Apps in Admin

After adding the missing apps, you should now see **7 total apps**:

| Title | Slug | Show in Dashboard | Purpose |
|-------|------|-------------------|---------|
| Immigration Process | immigration-process | ✅ Yes | Future app (Coming Soon) |
| My Budget | my-budget | ❌ No | Active (Available Apps) |
| My Calendar | my-calendar | ❌ No | Active (Available Apps) |
| My Credit History | my-credit-history | ✅ Yes | Future app (Coming Soon) |
| My Meds | my-meds | ❌ No | Active (Available Apps) |
| My Original Music | my-original-music | ✅ Yes | Future app (Coming Soon) |
| My Taxes | my-taxes | ✅ Yes | Future app (Coming Soon) |

## How to Manage Apps

### In Django Admin (`/admin/core/dashboardapp/`)

**To hide a "Coming Soon" app:**
1. Uncheck "Show in dashboard"
2. Save

**To deactivate an app completely:**
1. Uncheck "Is active"
2. Save

**To add a new "Coming Soon" app:**
1. Click "ADD DASHBOARD APP +"
2. Fill in:
   - Title: Display name
   - Slug: URL-friendly name (lowercase, hyphens)
   - Short description: Brief text for the card
   - Is active: ✅ Check
   - Show in dashboard: ✅ Check
3. Save

## Important Notes

1. **Active apps (My Calendar, My Budget, My Meds)** should have `show_in_dashboard = False` because they're hardcoded in the template for better control.

2. **"Coming Soon" apps** should have `show_in_dashboard = True` to appear dynamically.

3. All apps should have `is_active = True` unless you want to completely hide them.

4. You can control which users see apps using the "Allowed groups" field (leave empty for all authenticated users).

## Template Location

The dashboard template is at:
`core/templates/core/dashboard.html`

It has two sections:
1. **Available Apps** (lines ~14-67): Hardcoded active apps
2. **Featured Apps** (lines ~70-98): Dynamically loaded from database

