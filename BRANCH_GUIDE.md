# NarrativeWatch AI - Git Branch Guide

**Team Collaboration Structure**

---

## 📊 Branch Strategy

```
main (production)
 └── develop (development)
      ├── feature/orchestrator-agent (Team Member 1 - Rohan)
      ├── feature/backend-rag-apis (Team Member 2 - Backend Specialist)
      ├── feature/ml-nlp-agents (Team Member 3 - ML/NLP Specialist)
      ├── feature/data-eng-agents (Team Member 4 - Senior Data Engineer)
      └── feature/frontend-api-deployment (Team Member 5 - Frontend/DevOps)
```

---

## 👥 Team Assignments & Branches

### **Branch 1: feature/orchestrator-agent**
**Owner:** Rohan Urmude (Project Lead)

**Responsibilities:**
- Orchestrator Agent implementation
- Workflow orchestration logic
- State management system
- Integration coordination

**Deliverables:**
- `src/agents/orchestrator.py`
- `src/agents/base_agent.py`
- `src/workflow/orchestration.py`
- `src/workflow/state_manager.py`

**Week 1 Tasks:**
- [ ] Set up base agent architecture
- [ ] Implement agent executor pattern
- [ ] Create state management system

**Week 3 Tasks:**
- [ ] Integrate all agents
- [ ] Implement reflection loop
- [ ] Test complete workflow

**Timeline:** Weeks 1, 3-4

---

### **Branch 2: feature/backend-rag-apis**
**Owner:** Backend Specialist

**Responsibilities:**
- PostgreSQL + pgvector setup
- RAG pipeline implementation
- External API integrations
- Research Agent development

**Deliverables:**
- `src/database/postgres_client.py`
- `src/database/models.py`
- `src/database/rag_pipeline.py`
- `src/apis/tavily_api.py`
- `src/apis/instagram_api.py`
- `src/agents/rag_agent.py`
- `src/agents/research_agent.py`

**Week 1 Tasks:**
- [ ] Set up PostgreSQL + pgvector
- [ ] Create SQLAlchemy models
- [ ] Implement API wrappers

**Week 2 Tasks:**
- [ ] Build RAG pipeline
- [ ] Implement similarity search
- [ ] Create Research Agent with Tavily

**Timeline:** Weeks 1-2

---

### **Branch 3: feature/ml-nlp-agents**
**Owner:** ML/NLP Specialist

**Responsibilities:**
- Content analysis
- Bias detection
- Bot detection
- NLP preprocessing

**Deliverables:**
- `src/agents/content_analyzer.py`
- `src/agents/bias_detector.py`
- `src/agents/bot_detector.py`
- `src/utils/text_processor.py`
- `src/utils/embedding_utils.py`

**Week 1 Tasks:**
- [ ] Set up embeddings (Vertex AI)

**Week 2 Tasks:**
- [ ] Implement Content Analyzer Agent
- [ ] Implement Bias Detector Agent
- [ ] Implement Bot Detector Agent
- [ ] Write unit tests

**Timeline:** Weeks 2-3

---

### **Branch 4: feature/data-eng-agents**
**Owner:** Senior Data Engineer

**Responsibilities:**
- Campaign detection
- Synthesis agent
- Reviewer agent
- Reflection loop
- Trust score calculation

**Deliverables:**
- `src/agents/campaign_detector.py`
- `src/agents/synthesis_agent.py`
- `src/agents/reviewer_agent.py`
- `src/workflow/reflection_loop.py`
- `src/utils/scoring.py`

**Week 2 Tasks:**
- [ ] Design campaign detection algorithm
- [ ] Implement graph analysis

**Week 3 Tasks:**
- [ ] Implement Synthesis Agent
- [ ] Implement Reviewer Agent
- [ ] Build reflection loop with retry logic

**Timeline:** Weeks 2-3

---

### **Branch 5: feature/frontend-api-deployment**
**Owner:** Frontend/DevOps Specialist

**Responsibilities:**
- FastAPI service
- REST endpoint design
- Docker configuration
- Demo application
- Documentation

**Deliverables:**
- `src/app.py` (FastAPI)
- `src/models/request.py`
- `src/models/response.py`
- `Dockerfile`
- `docker-compose.yml`
- Demo interface
- Setup & deployment docs

**Week 3 Tasks:**
- [ ] Build FastAPI endpoints
- [ ] Create request/response models
- [ ] Swagger documentation

**Week 4 Tasks:**
- [ ] Docker configuration
- [ ] Demo application
- [ ] Documentation

**Timeline:** Weeks 3-4

---

## 🔄 Git Workflow

### For Each Team Member:

**1. Clone & Setup**
```bash
git clone https://github.com/rishikumargl/NarrativeWatch-AI.git
cd NarrativeWatch-AI
git checkout develop
git checkout -b your-feature-branch
```

**2. Daily Development**
```bash
# Before starting work
git pull origin develop

# Make changes
git add .
git commit -m "Clear commit message describing change"

# Push to your feature branch daily
git push origin your-feature-branch
```

**3. Create Pull Request (PR)**
When your milestone is complete:
```bash
# Make sure your branch is up to date
git pull origin develop

# Push final changes
git push origin your-feature-branch
```

Then on GitHub:
- Click "Compare & pull request"
- Set base branch to `develop`
- Write PR description (what, why, testing)
- Request review from another team member
- Address feedback and merge

**4. Merge to Develop**
After approval:
```bash
git checkout develop
git pull origin develop
git merge your-feature-branch
git push origin develop
```

---

## 📋 Branch Protection Rules

**Protect these branches on GitHub:**

- `main` - Require PR reviews (2 approvals), require tests passing
- `develop` - Require PR reviews (1 approval), require tests passing

**Allow direct commits to:**
- `feature/*` - Allow direct commits (each person's branch)

---

## 🔀 Merging Strategy

### Week 1-2: Features in Progress
- Each team member works independently on their feature branch
- Push changes daily
- NO merge to develop yet

### Week 2-3: Integration Phase
- Merge Agent features to develop (one at a time)
  1. **Monday:** Merge `feature/backend-rag-apis`
  2. **Tuesday:** Merge `feature/ml-nlp-agents`
  3. **Wednesday:** Merge `feature/data-eng-agents`
  4. **Thursday:** Merge `feature/orchestrator-agent`
  5. **Friday:** Merge `feature/frontend-api-deployment`

### Week 4: Demo & Final
- All features in develop
- Create release branch from develop
- Test completely
- Merge to main for production

---

## ✅ Before Merging to Develop

**Checklist for every PR:**

- [ ] All code committed to feature branch
- [ ] All tests passing locally (`pytest tests/ -v`)
- [ ] No merge conflicts with develop
- [ ] Code formatted with black (`black src/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] No hardcoded API keys or secrets
- [ ] Commit messages are clear
- [ ] PR description explains changes
- [ ] Tests cover 80%+ of new code
- [ ] No console errors or warnings

---

## 🔗 Dependency Map

**Order to merge PRs (minimize conflicts):**

1. **First:** `feature/backend-rag-apis` (creates DB models & utilities)
2. **Second:** `feature/ml-nlp-agents` (uses utilities from backend)
3. **Third:** `feature/data-eng-agents` (can depend on agents)
4. **Fourth:** `feature/orchestrator-agent` (orchestrates all agents)
5. **Fifth:** `feature/frontend-api-deployment` (exposes orchestrator via API)

**Parallel (no conflicts):**
- All feature branches can develop in parallel
- Conflicts only resolved when merging to develop

---

## 📌 Commit Message Convention

**Format:** `[Branch] Action: Description`

**Examples:**
```
[orchestrator] feat: implement base agent architecture
[backend] fix: correct pgvector similarity query
[ml-nlp] test: add unit tests for bias detector
[data-eng] refactor: improve reflection loop logic
[frontend] docs: add API endpoint documentation
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Add/update tests
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `perf:` - Performance improvement

---

## 🚨 Conflict Resolution

**If you get merge conflicts:**

```bash
# Pull develop to see conflicts
git pull origin develop

# Fix conflicts in affected files
# Look for <<<<<<, ======, >>>>>> markers
# Keep both versions if needed, or choose one

# After fixing
git add .
git commit -m "[Branch] merge: resolve conflicts with develop"
git push origin your-feature-branch
```

**Ask for help if:**
- Conflicts are too complex
- Not sure which version to keep
- Multiple files have conflicts

---

## 📊 Progress Tracking

**Weekly Updates (Friday):**

Each team member updates their status:

```markdown
## [Your Name] - Week [N] Status

### Completed
- [ ] Task 1
- [ ] Task 2

### In Progress
- [ ] Task 3 (70% done)

### Blockers
- Issue: [Description]
  - Help needed: [What]

### Next Week
- [ ] Task X
- [ ] Task Y
```

---

## 🔐 Important Rules

1. **Never commit secrets**
   - No API keys in code
   - No passwords in .env (use .env.example)
   - Use .gitignore for sensitive files

2. **Never force push to develop or main**
   - Use only regular push
   - If needed, ask team lead first

3. **Always pull before pushing**
   - Reduces merge conflicts
   - Keeps branch in sync

4. **Test before pushing**
   - Run your tests locally
   - Run `black` formatter
   - Check for console errors

5. **Write clear commit messages**
   - Describe WHAT and WHY
   - Make it searchable
   - One commit = one logical change

---

## 📱 Communication

**Slack Updates:**
- Daily: Brief 10 AM standup update
- Blockers: Post in #dev-help immediately
- PRs: Mention in channel when ready for review
- Conflicts: Notify team before resolving

**GitHub Issues:**
- Create issue for bugs/tasks
- Link PRs to issues
- Use labels (bug, feature, blocked)

---

## 🎯 Success Criteria

**By End of Week 2:**
- ✅ All feature branches have code
- ✅ All developers pushing daily
- ✅ Tests written for features

**By End of Week 3:**
- ✅ All features merged to develop
- ✅ Integration tests passing
- ✅ No conflicts remaining

**By End of Week 4:**
- ✅ All tests passing (90%+ coverage)
- ✅ Demo working end-to-end
- ✅ Ready to merge develop → main

---

## Quick Command Reference

```bash
# Create and switch to your branch
git checkout -b feature/your-task

# Pull latest from develop
git pull origin develop

# Check branch status
git status
git branch -v

# View branches
git branch -a  # All branches
git branch     # Local only

# Push to your branch
git push origin feature/your-task

# Update feature branch with develop changes
git fetch origin
git merge origin/develop

# Create PR on GitHub (web)
# Then merge after approval

# Switch back to develop
git checkout develop
git pull origin develop
```

---

## Questions?

1. **"How do I merge my branch?"** → Follow "Merging Strategy" section above
2. **"I have conflicts"** → See "Conflict Resolution" section
3. **"Where should I commit this?"** → Check "Team Assignments" section
4. **"Can I push directly to develop?"** → No, always use PR workflow
5. **"Do I need to wait for others?"** → No, develop in parallel on feature branches

---

**Last Updated:** 2026-06-12  
**Status:** Ready for team distribution

