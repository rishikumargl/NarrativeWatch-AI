# Merge Strategy - Avoid Conflicts

Guide for Team Member 5 to merge safely with other team branches.

## Current Branch Layout

```
main
  ↓
develop (implied)
  ├── feature/orchestrator-agent (Team 1)
  ├── feature/backend-rag-apis (Team 2)
  ├── feature/ml-nlp-agents (Team 3)
  ├── feature/data-eng-agents (Team 4)
  └── feature/frontend-api-deployment (Team 5 - YOU)
       └── member5-implementation (Your working branch)
```

---

## ✅ Why No Conflicts?

### File Ownership Matrix

| Directory | Owner | Your Conflict Risk |
|-----------|-------|-------------------|
| `src/agents/` | Teams 1,3,4 | ❌ NONE - You don't touch |
| `src/database/` | Team 2 | ❌ NONE - You don't touch |
| `src/workflow/` | Team 1 | ❌ NONE - You don't touch |
| `src/models/` | **YOU** | ✅ SAFE - Only you own this |
| `src/utils/` | **YOU** | ✅ SAFE - Only you own this |
| `src/app.py` | **YOU** | ✅ SAFE - Only you own this |
| `frontend/` | **YOU** | ✅ SAFE - Only you own this |
| `docs/` | **YOU** | ✅ SAFE - Only you own this |
| `requirements.txt` | ⚠️ SHARED | ⚠️ COORDINATE |
| `src/apis/` | Team 2 | ❌ NONE - They own it |
| `src/config.py` | Team 1 | ❌ NONE - Don't modify |

**Summary:** You own isolated directories. Only potential conflict is `requirements.txt`.

---

## ⚠️ SHARED FILE: requirements.txt

### Current Content
```
# Core LLM & Agents (Teams 1-4)
langchain>=0.1.0
langchain-google-vertexai>=0.1.0
langchain-community>=0.1.0

# Database & Vector Search (Team 2)
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pgvector>=0.3.0
alembic>=1.13.0

# ... (other dependencies)

# API & Web Framework (YOU - ADD THESE)
fastapi>=0.104.0      # ← You add this
uvicorn>=0.24.0       # ← You add this
pydantic>=2.0.0       # ← You add this
pydantic-settings>=2.0.0  # ← You add this
```

### How to Resolve Conflicts

**Strategy: "Their Core, Your Web"**

If you see a conflict in `requirements.txt`:

```diff
# KEEP from other teams (they added for agents)
langchain>=0.1.0
langchain-google-vertexai>=0.1.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pgvector>=0.3.0

# ADD YOUR DEPENDENCIES (web framework)
+ fastapi>=0.104.0
+ uvicorn>=0.24.0
+ pydantic>=2.0.0
+ pydantic-settings>=2.0.0

# Keep any other existing dependencies
transformers>=4.30.0
nltk>=3.8.0
# ... etc
```

**Don't remove anything from other teams!**

---

## 🔄 Merge Workflow (Step by Step)

### Phase 1: Prep Your Branch (NOW)

```bash
# Make sure your branch is clean
git status
# Should show: "nothing to commit, working tree clean"

# If not, commit your changes
git add -A
git commit -m "[frontend] description of changes"

# Verify your commits
git log --oneline member5-implementation -5
```

### Phase 2: When Other Teams Are Done

```bash
# Update your local main/develop
git fetch origin
git checkout develop  # or main, depending on their branch
git pull origin develop

# Merge their changes into your feature branch
git checkout feature/frontend-api-deployment
git pull origin feature/frontend-api-deployment

# Merge develop into your feature branch
git merge develop

# If merge conflicts in requirements.txt:
# 1. Edit the file manually (see strategy above)
# 2. Keep everyone's dependencies
# git add requirements.txt
# git commit -m "resolve: merge requirements.txt with all dependencies"
```

### Phase 3: Rebase for Clean History (OPTIONAL)

```bash
# If you want a clean, linear history:
git checkout member5-implementation
git rebase feature/frontend-api-deployment

# If conflicts during rebase:
# 1. Fix conflicts
# 2. git add <files>
# 3. git rebase --continue
```

### Phase 4: Final Merge to Feature Branch

```bash
git checkout feature/frontend-api-deployment
git merge member5-implementation

# Or if using rebase:
git merge --ff-only member5-implementation

# Push to remote
git push origin feature/frontend-api-deployment
```

### Phase 5: Submit for Review

```bash
# From GitHub UI: Create PR from feature/frontend-api-deployment → main
# Or command line:
gh pr create --base main --head feature/frontend-api-deployment \
  --title "Feature: Frontend API and React demo" \
  --body "Implements Team Member 5 responsibilities: FastAPI backend, React frontend, Docker deployment, documentation"
```

---

## 🛡️ Safe Merge Checklist

Before merging:

- [ ] Your code is committed to `member5-implementation`
- [ ] You've pulled latest from `feature/frontend-api-deployment`
- [ ] You've merged other teams' changes
- [ ] No conflicts exist (or you've resolved them)
- [ ] `requirements.txt` has all dependencies (no removals)
- [ ] You haven't modified `src/agents/`, `src/database/`, `src/workflow/`
- [ ] You haven't modified `src/config.py`
- [ ] Frontend still builds: `cd frontend && npm run build`
- [ ] Backend still imports: `python -c "import src.app"`
- [ ] Tests pass (if any): `pytest tests/`

---

## ⚡ Quick Commands

### Check for conflicts
```bash
git diff --name-only --diff-filter=U
# Should return empty if no conflicts
```

### See what changed in other branches
```bash
git diff feature/frontend-api-deployment...feature/backend-rag-apis -- src/
# Shows what changed in src/ between branches
```

### Reset if something goes wrong
```bash
# Undo last merge (before pushing)
git merge --abort

# Or reset to before merge
git reset --hard HEAD~1

# Or checkout clean version
git checkout -f feature/frontend-api-deployment
```

### View merge commit history
```bash
git log --graph --oneline --all
```

---

## 📋 Conflict Resolution Reference

### Scenario 1: requirements.txt Conflict

**When you see:**
```
<<<<<<< HEAD
fastapi>=0.104.0
=======
transformers>=4.30.0
>>>>>>> develop
```

**Do this:**
```python
# KEEP BOTH! It's not either/or, it's AND
fastapi>=0.104.0
transformers>=4.30.0
```

### Scenario 2: Code Conflict (shouldn't happen)

If somehow code conflicts exist:
```bash
# Check which files
git status

# For each file, edit and keep relevant code
nano src/app.py  # or your editor

# Mark as resolved
git add src/app.py

# Continue merge
git commit -m "resolve: merge conflicts"
```

---

## 🔍 Safety Checks

### Before Final Merge

```bash
# 1. Verify no accidental file deletes
git log --name-status feature/frontend-api-deployment...member5-implementation | grep "^D"
# Should be empty (no deletes)

# 2. Verify your files are still there
git ls-tree -r member5-implementation | grep -E "(app.py|frontend|docs)"
# Should show your files

# 3. Count total files
git ls-tree -r member5-implementation | wc -l
# Should match your implementation (28 files approx)
```

---

## 🚨 If Something Goes Wrong

### Abort a merge
```bash
git merge --abort
# Reverts to pre-merge state
```

### Reset to a known good state
```bash
git reset --hard origin/feature/frontend-api-deployment
git checkout member5-implementation
# Back to your last committed state
```

### Force pull latest
```bash
git fetch origin --force
git checkout -B feature/frontend-api-deployment origin/feature/frontend-api-deployment
```

### Cherry-pick specific commits
```bash
# If you want just your work, without merging:
git cherry-pick <commit-hash>
```

---

## 📞 Asking for Help

If you get stuck:

1. **Don't force push** - Never use `git push --force`
2. **Show the error** - Screenshot or paste git output
3. **Show the status** - Run `git status` and share output
4. **Show the diff** - Run `git diff --name-only` and share
5. **Undo if unsure** - Use `git merge --abort` to reset

---

## ✅ Success = Clean Merge

You'll know it worked when:
- ✅ No "CONFLICT" messages
- ✅ All files from all teams present
- ✅ `requirements.txt` has all dependencies
- ✅ No `<<<<<<< HEAD` markers
- ✅ Merge commit created successfully
- ✅ Remote updated: `git push origin feature/frontend-api-deployment`

---

**Remember:** You're in an isolated branch. Most conflicts won't happen. Just follow the checklist when merging with others. 🚀
