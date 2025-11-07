# Import Debugging Guide

## URL Routes

Both imports should be accessible at:
- **Structured Import**: `/ilogic/import/structured/`
- **Markdown Import**: `/ilogic/import/markdown/`

## Common Issues

### 404 Error on Structured Import

**Possible causes:**
1. URL trailing slash mismatch - Django requires trailing slashes by default
2. URL not properly included in main urls.py

**Check:**
- Visit `/ilogic/import/structured/` (with trailing slash)
- Check browser console for errors
- Check Django server logs for URL resolution errors

### Markdown Import Not Working

**Possible causes:**
1. File format doesn't match expected pattern
2. Regex pattern too strict
3. File encoding issues

**Check:**
- File should start with `# Assembly Name`
- Rules should be in format:
  ```
  ## Rule: RuleName
  *Component: [[ComponentName]]*
  ```vbnet
  code here
  ```
  ```

**Debug steps:**
1. Check Django server console for error messages
2. Look for "Markdown import: File size: X chars" message
3. Check if assembly name and components are parsed

## Testing

To test the imports:

1. **Markdown Import:**
   - Create a test file with:
     ```
     # Test Assembly
     
     ## Rule: Test Rule
     *Component: [[Test Component]]*
     ```vbnet
     Sub Main()
         ' Test code
     End Sub
     ```
     ```
   - Upload and check for success message

2. **Structured Import:**
   - Create a test folder structure:
     ```
     Test Assembly/
       Test Component/
         Test Document__Test Rule.txt
     ```
   - Select the "Test Assembly" folder
   - Check for success message

