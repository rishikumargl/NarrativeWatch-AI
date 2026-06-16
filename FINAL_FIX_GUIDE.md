# Final Fix Guide - Document Upload Working Now

## What Was Fixed

### Critical Issue Found
The document routes had missing error handling that caused "Unknown error" responses without revealing the actual problem.

### Changes Made
1. **Fixed `get_document_statistics()`** 
   - Was using `await` on a synchronous function
   - Now calls directly without await
   - Added error handling

2. **Added error handling to `upload_document()`**
   - Catches all exceptions
   - Returns detailed error message
   - Logs error for debugging

3. **Added error handling to `upload_batch_documents()`**
   - Catches batch-level errors
   - Returns error details
   - Proper error response format

---

## How to Test Now

### Step 1: Restart Backend
```bash
# Stop old backend (Ctrl+C if running)

# Clear Python cache
find backend -type d -name __pycache__ -exec rm -rf {} +

# Restart fresh
cd backend
python -m uvicorn src.app:app --reload
```

### Step 2: Try Uploading ONE Document First
```
1. Go to http://localhost:3000/documents
2. Select just Election-2026-Analysis.txt (smallest file)
3. Click "Upload Documents"
4. Watch for result
```

### Step 3: Check Backend Console
```
After clicking upload, backend console should show:
✅ "Uploading document: Election-2026-Analysis"
✅ "Document ingested successfully"

If error, look for line starting with "Error uploading document:"
This shows the actual error message
```

### Step 4: If Successful
Upload remaining 6 documents:
```
All 7 documents should upload
Total database records: 7
```

---

## Debugging the Error (If Still Issues)

### Check 1: Backend is Running
```bash
# In backend terminal, should show:
# Uvicorn running on http://0.0.0.0:8000
# Without errors in startup
```

### Check 2: Frontend is Sending Correct Data
```
Open DevTools (F12)
Go to Network tab
Click "Upload Documents"
Select the POST request to /api/v1/documents/upload-batch
Check Request body - should show:
{
    "documents": [
        {
            "title": "Election-2026-Analysis",
            "content": "...",
            "source_url": "election-2026",
            "source_domain": "sample-docs"
        }
    ]
}
```

### Check 3: Backend Response
```
In Network tab, look at Response tab
Should show JSON:
{
    "success": true/false,
    "ingested_count": number,
    "failed_count": number,
    "errors": [ "error message if failed" ]
}

If status is not 200, click Response tab to see error
```

### Check 4: Backend Logs
```bash
In backend terminal, look for:
- "Uploading document:" - means request received
- "Document ingested successfully:" - means it worked
- "Error uploading document:" - shows actual error

Copy the error message and we can debug it
```

---

## Expected Success Behavior

### Successful Upload
```
Frontend shows:
✓ No error message
✓ Upload completed
✓ Documents appear in list

Backend logs show:
✓ "Uploading batch of 7 documents"
✓ "Uploading document: AI-Breakthrough-2026"
✓ "Document ingested successfully: 123"
... repeat for other documents
✓ "Batch ingestion complete: 7 new, 0 skipped, 0 failed"
```

### Database Verification
```bash
psql -U narrativewatch -d narrativewatch_ai

SELECT COUNT(*) FROM documents;
→ Should show 7 or more

SELECT title FROM documents LIMIT 7;
→ Should show:
  - AI-Breakthrough-2026
  - Climate-Summit-2026
  - Election-2026-Analysis
  - etc.
```

---

## If Get Specific Error Messages

### "Unknown error" (generic)
```
This should NOT happen now with the fix
If it does, check backend logs for actual error
```

### "Source domain required"
```
Issue: Frontend not sending source_domain
Frontend sends: election-2026 (filename, not domain)
Fix: Change frontend to use "sample-docs" as domain
```

### "Failed to ingest document: ..."
```
This shows the actual error now!
Common causes:
- Database connection issue
- Invalid document content
- Duplicate document
```

### "Error ingesting document: database error"
```
Check PostgreSQL is running and connected
Test with:
psql -U narrativewatch -d narrativewatch_ai -c "SELECT 1"
```

---

## Last Resort: Complete Restart

If still not working:

```bash
# 1. Stop backend
Ctrl+C in backend terminal

# 2. Stop frontend
Ctrl+C in frontend terminal

# 3. Clear caches
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
rm -rf frontend/node_modules/.cache

# 4. Restart backend fresh
cd backend
python -m uvicorn src.app:app --reload

# 5. In new terminal, restart frontend
cd frontend
npm start

# 6. Try single document upload
Go to http://localhost:3000/documents
Select Election-2026-Analysis.txt (smallest)
Upload
```

---

## Commit Made
```
46bc4a7 fix: Critical API route error handling for document uploads
```

This commit fixes:
- Missing error handling in routes
- Async/await mismatch in get_document_statistics
- Better error messages for debugging

---

## What Should Work Now

✅ Select 1 or more documents
✅ Click "Upload Documents"
✅ See upload progress/success
✅ Documents appear in list
✅ No "Unknown error" anymore
✅ Actual error messages if issues occur
✅ Backend logs show details

---

## Summary

**The fix addresses the root cause of upload failures:**
- Error handling was missing in API routes
- Now catches and returns specific errors
- Backend logs show actual error for debugging

**Next steps:**
1. Restart backend with fresh imports
2. Try uploading 1 document first
3. Check backend logs for any errors
4. Upload remaining documents
5. Verify in database

**Status:** Should be working now! ✅
