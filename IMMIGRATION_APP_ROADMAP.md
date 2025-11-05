# 🧳 Immigration Research Vault - Complete Roadmap

**Project Goal:** Build a zero-friction research system for immigration-related content with auto-enrichment, AI-powered insights, and intelligent organization.

**Core Concept:** Trusted Research Vault - Capture any immigration link/PDF in one click, auto-enrich with metadata + AI, annotate deeply, and query your entire corpus intelligently.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Phase 1: MVP - Frictionless Capture & Notes](#phase-1-mvp---frictionless-capture--notes-week-1-2)
3. [Phase 2: AI Integration](#phase-2-ai-integration-week-3-4)
4. [Phase 3: Advanced Features](#phase-3-advanced-features-week-5-6)
5. [Phase 4: Browser Extension](#phase-4-browser-extension-week-7-8)
6. [Data Models Reference](#data-models-reference)
7. [URL Structure](#url-structure)
8. [Technology Stack](#technology-stack)
9. [Implementation Checklist](#implementation-checklist)

---

## Overview

### Key Principles
- ✅ **Zero Friction**: One-click capture, minimal input required
- ✅ **Auto-Enrichment**: Automatically pull metadata, text, and insights
- ✅ **Trust & Citations**: Always show sources, badge official .gov sites
- ✅ **Easy Notes**: Inline markdown editing with templates
- ✅ **Intelligent Search**: Full-text search across titles, URLs, notes, content
- ✅ **AI-Powered**: Summarization, Q&A, extraction, tagging

### User Flow
1. **Capture**: User pastes URL → system auto-fetches title, description, favicon, text
2. **Enrich**: AI optionally summarizes, extracts forms/fees/deadlines, suggests tags
3. **Organize**: User adds quick notes, categorizes, tags, favorites
4. **Search**: User queries across entire corpus with filters
5. **Analyze**: AI answers questions based on saved research (RAG)

---

## Phase 1: MVP - Frictionless Capture & Notes (Week 1-2)

### Goal
Build the core research vault with instant link capture, auto-enrichment, and rich note-taking.

### Features Checklist

#### Dashboard
- [ ] Main dashboard with stats (total items, notes, categories)
- [ ] Recent saves list (last 10 items)
- [ ] Favorites section (pinned items)
- [ ] Quick save modal/form (paste URL → save)
- [ ] Quick action buttons (All Items, Favorites, Categories, Search)

#### Link Capture & Auto-Enrichment
- [ ] Quick save form (single URL input)
- [ ] Auto-fetch metadata:
  - [ ] Page title
  - [ ] Meta description
  - [ ] Favicon URL
  - [ ] OpenGraph tags (og:title, og:description, og:image)
  - [ ] Canonical URL
  - [ ] Domain extraction
- [ ] Clean text extraction (BeautifulSoup + readability)
- [ ] Source type detection:
  - [ ] USCIS (uscis.gov)
  - [ ] Dept of State (travel.state.gov)
  - [ ] NVC (nvc.state.gov)
  - [ ] CBP (cbp.gov)
  - [ ] ICE (ice.gov)
  - [ ] EOIR (justice.gov/eoir)
  - [ ] Congress (congress.gov)
  - [ ] Federal Register (federalregister.gov)
  - [ ] Forum/Blog/Other
- [ ] Official .gov badge display
- [ ] Duplicate detection (same canonical URL)
- [ ] Text hash generation (for change detection later)

#### Organization System
- [ ] Categories (hierarchical):
  - [ ] Visa Types (H-1B, K-1, Green Card, Citizenship, etc.)
  - [ ] Documents & Forms
  - [ ] Fees & Costs
  - [ ] Timelines & Processing
  - [ ] Legal Resources
  - [ ] Forums & Community
  - [ ] News & Updates
- [ ] Tags (flexible, multi-select per item)
- [ ] Favorites/Pins (quick access)
- [ ] Archive functionality (hide without deleting)

#### Note-Taking
- [ ] Rich notes per item (one-to-many relationship)
- [ ] Markdown support (headings, lists, bold, links)
- [ ] Note types:
  - [ ] General Note
  - [ ] Question
  - [ ] To-Do
  - [ ] Important
  - [ ] RFE Notes
  - [ ] Deadline
- [ ] Inline note creation (add note directly on item detail page)
- [ ] Note templates:
  - [ ] "RFE Response Notes"
  - [ ] "Form Requirements"
  - [ ] "Policy Update Notes"
  - [ ] "Interview Prep"
- [ ] Timestamp display (created/updated)

#### Item Management
- [ ] Item list view with filters:
  - [ ] By source type (USCIS, DOS, etc.)
  - [ ] By content type (webpage, PDF, form, news)
  - [ ] By date range (today, week, month, custom)
  - [ ] By category
  - [ ] By tag
  - [ ] Favorites only
  - [ ] Archived/active
- [ ] Item detail view:
  - [ ] Full metadata display
  - [ ] All notes (with add/edit/delete)
  - [ ] Quick actions (favorite, archive, delete, edit)
  - [ ] "Open Original" link
  - [ ] Extracted text preview (collapsible)
- [ ] Item edit form (update title, description, categories, tags)
- [ ] Item delete (with confirmation)
- [ ] Bulk actions (select multiple → tag, categorize, delete)

#### Search & Discovery
- [ ] Global search bar (always visible)
- [ ] Search across:
  - [ ] Titles
  - [ ] URLs
  - [ ] Descriptions
  - [ ] Extracted text (full-text search)
  - [ ] Note content
- [ ] Search filters (same as item list filters)
- [ ] Search results with highlights
- [ ] Recent searches (quick access)

#### UI/UX (Tailwind/DaisyUI)
- [ ] Responsive dashboard layout
- [ ] Card-based item display
- [ ] Modal for quick save
- [ ] Badge system (official, PDF, new, favorite)
- [ ] Clean typography and spacing
- [ ] Dark mode support (DaisyUI themes)
- [ ] Loading states (during auto-enrichment)
- [ ] Toast notifications (success/error messages)

### Data Models (Phase 1)

**ResearchItem**
- Core: `owner`, `url`, `canonical_url`, `title`, `description`, `domain`
- Metadata: `favicon_url`, `content_type`, `source_type`, `is_official`
- Content: `extracted_text`, `text_hash`
- PDF: `pdf_file` (optional FileField)
- Organization: `is_favorite`, `is_archived`
- Timestamps: `created_at`, `updated_at`, `last_checked_at`

**Category**
- Fields: `owner`, `name`, `slug`, `icon`, `description`, `parent`, `order`
- Hierarchical support (self-referencing FK)

**Tag**
- Fields: `owner`, `name`, `slug`, `color`
- Simple tagging system

**ItemCategory** (many-to-many through)
- Fields: `item`, `category`, `added_at`

**ItemTag** (many-to-many through)
- Fields: `item`, `tag`, `added_at`

**ResearchNote**
- Fields: `item`, `owner`, `content` (markdown), `note_type`
- Timestamps: `created_at`, `updated_at`

### URL Structure (Phase 1)

```
/immigration/                          → Dashboard
/immigration/quick-save/               → Quick save form/modal
/immigration/items/                    → Item list
/immigration/items/<pk>/               → Item detail
/immigration/items/<pk>/edit/          → Edit item
/immigration/items/<pk>/delete/        → Delete item
/immigration/items/<pk>/notes/add/     → Add note
/immigration/notes/<pk>/edit/          → Edit note
/immigration/notes/<pk>/delete/        → Delete note
/immigration/categories/               → Category list
/immigration/categories/<slug>/        → Category detail (filtered items)
/immigration/tags/                     → Tag cloud/list
/immigration/favorites/                → Favorites list
/immigration/search/                   → Search results
```

### Utilities (Phase 1)

**immigration/utils.py**
- `fetch_metadata(url)` → dict with title, description, favicon, OG tags
- `extract_text(url)` → clean text from HTML
- `detect_source_type(url)` → source_type enum based on domain
- `compute_text_hash(text)` → SHA-256 hash for change detection
- `normalize_url(url)` → clean URL (remove tracking params)

---

## Phase 2: AI Integration (Week 3-4)

### Goal
Add AI-powered summarization, extraction, Q&A, and smart tagging using OpenAI API.

### Features Checklist

#### Auto-Summarization
- [ ] One-click "Summarize with AI" button on item detail
- [ ] Two summary modes:
  - [ ] Short (3 sentences)
  - [ ] Detailed (comprehensive overview)
- [ ] Display summary in collapsible card
- [ ] "Save to Notes" button (copy AI summary to new note)
- [ ] Token usage tracking (for cost monitoring)
- [ ] Cache summaries (don't regenerate)

#### Smart Extraction
- [ ] Auto-detect immigration entities:
  - [ ] Forms (I-130, I-485, DS-160, etc.)
  - [ ] Fees (with amounts)
  - [ ] Deadlines (with dates)
  - [ ] Requirements (eligibility criteria)
  - [ ] Processing times
- [ ] Display extracts in structured format (badges, tables)
- [ ] Link forms to official USCIS form pages
- [ ] Add extracts to searchable index

#### AI Q&A (RAG - Retrieval Augmented Generation)
- [ ] Chat interface in sidebar (always accessible)
- [ ] Ask questions about saved research
- [ ] AI searches user's corpus + answers
- [ ] Always show source citations
- [ ] Link back to specific saved items
- [ ] Conversation history (per session or saved)
- [ ] Example questions:
  - [ ] "What documents do I need for K-1 visa?"
  - [ ] "Compare AOS vs consular processing"
  - [ ] "What changed about I-485 medical requirements?"

#### Smart Tagging
- [ ] AI suggests tags based on content
- [ ] User can accept/reject suggestions
- [ ] Learn from user's tag patterns
- [ ] Auto-apply high-confidence tags

#### Key Points Extraction
- [ ] AI generates bullet list of key points
- [ ] Display in item detail view
- [ ] Useful for quick review without reading full text

#### AI Chat Assistant
- [ ] Dedicated chat page (`/immigration/ai-chat/`)
- [ ] Persistent conversation history
- [ ] Context selection (which items to include)
- [ ] Export conversation to notes
- [ ] Example use cases:
  - [ ] "Explain public charge rule"
  - [ ] "What's the difference between I-130 and I-129F?"
  - [ ] "Timeline for K-1 visa based on my research"

### Additional Data Models (Phase 2)

**AIExtract**
- Fields: `item` (OneToOne), `summary_short`, `summary_detailed`, `key_points` (JSON)
- Immigration-specific: `forms_mentioned` (JSON), `fees_mentioned` (JSON), `deadlines` (JSON), `requirements` (JSON)
- Metadata: `model_used`, `tokens_used`, `generated_at`

**AIConversation**
- Fields: `owner`, `title`, `messages` (JSON array), `context_items` (ManyToMany to ResearchItem)
- Timestamps: `created_at`, `updated_at`

### AI Utilities (Phase 2)

**immigration/ai_utils.py**
- `summarize_content(text, mode='short')` → AI summary
- `extract_immigration_entities(text)` → dict with forms, fees, deadlines
- `answer_from_corpus(question, items_queryset)` → RAG-based answer
- `suggest_tags(text)` → list of suggested tags
- `extract_key_points(text)` → bullet list
- `chat_assistant(messages, context_items)` → conversational AI

### API Configuration

**myproject/settings.py**
```python
# OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4o-mini'  # Cost-effective, fast
OPENAI_MAX_TOKENS = 4000  # Control costs
```

**Environment Variables**
```bash
OPENAI_API_KEY=sk-...
```

---

## Phase 3: Advanced Features (Week 5-6)

### Goal
Add change detection, collections, PDF handling, comparisons, and export tools.

### Features Checklist

#### Change Detection & Monitoring
- [ ] Monitor saved items for content changes
- [ ] Daily/weekly check frequency (user configurable)
- [ ] Store snapshots (ResearchSnapshot model)
- [ ] Visual diff view (show what changed)
- [ ] Email/notification alerts on changes
- [ ] Dashboard widget showing recent changes
- [ ] "History" tab on item detail (view all snapshots)

#### Collections/Workspaces
- [ ] Create named collections (e.g., "K-1 Visa Case", "Citizenship Process")
- [ ] Add items to multiple collections
- [ ] Collection dashboard (overview per collection)
- [ ] Share collections (read-only link)
- [ ] Export collection as PDF report
- [ ] Collection progress tracking (checklist)

#### PDF Upload & Parsing
- [ ] Drag-and-drop PDF upload
- [ ] Auto-extract text from PDFs (PyPDF2 or pdfplumber)
- [ ] Parse USCIS notices (extract case numbers, dates, actions)
- [ ] Parse official forms (detect form number, edition date)
- [ ] Store PDF file securely (media/immigration/pdfs/)
- [ ] PDF viewer in browser (pdf.js)
- [ ] Annotate PDFs (highlight, comments)

#### Comparison Tool
- [ ] Select 2+ items to compare side-by-side
- [ ] AI-powered comparison summary
- [ ] Highlight differences
- [ ] Use cases:
  - [ ] Compare visa types (H-1B vs O-1)
  - [ ] Compare processing times across service centers
  - [ ] Compare old vs new policy versions
- [ ] Export comparison as table/PDF

#### Glossary Builder
- [ ] Auto-extract immigration terms from saved content
- [ ] Build personal glossary (term → definition)
- [ ] AI-powered definitions
- [ ] Link terms in text (hover to see definition)
- [ ] Glossary page with search/filter
- [ ] Export glossary as PDF cheat sheet

#### Saved Searches (Smart Folders)
- [ ] Save complex search queries as "smart folders"
- [ ] Examples:
  - [ ] "Any USCIS page updated in last 7 days"
  - [ ] "All items mentioning 'I-485 fee'"
  - [ ] "K-1 visa resources with notes"
- [ ] Auto-update as new items are added
- [ ] Badge showing count

#### Export & Sharing
- [ ] Export single item as PDF (pretty print)
- [ ] Export collection as PDF report (with cover page, TOC)
- [ ] Export as CSV (for Excel analysis)
- [ ] Export as JSON (backup/transfer)
- [ ] Generate shareable link (read-only, expiring)
- [ ] Print-friendly CSS for all views

#### Bookmarklet
- [ ] JavaScript bookmarklet for one-click save
- [ ] Popup window with item preview
- [ ] Auto-fill URL, title, description
- [ ] Quick note field
- [ ] Tag/category selection
- [ ] "Save & Close" button

### Additional Data Models (Phase 3)

**ResearchSnapshot**
- Fields: `item`, `text_hash`, `html_hash`, `extracted_text`, `screenshot`, `captured_at`
- For change detection

**Collection**
- Fields: `owner`, `name`, `slug`, `description`, `icon`, `is_public`, `share_token`
- Timestamps: `created_at`, `updated_at`

**CollectionItem**
- Fields: `collection`, `item`, `order`, `added_at`

**Glossary**
- Fields: `owner`, `term`, `definition`, `source_item` (FK, optional), `category`

**Monitor**
- Fields: `item`, `frequency` (daily/weekly), `last_check_at`, `last_change_at`, `is_active`

---

## Phase 4: Browser Extension (Week 7-8)

### Goal
Build Chrome/Firefox extension for seamless capture from any webpage.

### Features Checklist

#### Extension Core
- [ ] One-click save button in toolbar
- [ ] Context menu: "Save to Immigration Vault"
- [ ] Badge showing # of saved items
- [ ] Popup UI (mini dashboard)

#### Capture Features
- [ ] Save current page with one click
- [ ] Highlight text → right-click → "Save highlight"
- [ ] Quick note input in popup
- [ ] Tag/category selection
- [ ] "Save & Continue" vs "Save & View"

#### Quick Access
- [ ] Recent saves in popup (last 5)
- [ ] Search saved items from popup
- [ ] Quick actions (favorites, categories)
- [ ] Badge notifications (changes detected)

#### Sync
- [ ] Sync with Django backend via API
- [ ] OAuth authentication
- [ ] Offline queue (save when offline, sync later)

### Extension Tech Stack
- Manifest V3 (Chrome/Firefox compatible)
- Vanilla JS or lightweight React
- IndexedDB for offline storage
- Fetch API for backend communication

---

## Data Models Reference

### Complete Schema

```python
# Core Models
ResearchItem(
    owner, url, canonical_url, title, description, domain,
    favicon_url, content_type, source_type, is_official,
    extracted_text, text_hash, pdf_file,
    is_favorite, is_archived,
    created_at, updated_at, last_checked_at
)

Category(owner, name, slug, icon, description, parent, order)

Tag(owner, name, slug, color)

ItemCategory(item, category, added_at)

ItemTag(item, tag, added_at)

ResearchNote(item, owner, content, note_type, created_at, updated_at)

# AI Models
AIExtract(
    item, summary_short, summary_detailed, key_points,
    forms_mentioned, fees_mentioned, deadlines, requirements,
    model_used, tokens_used, generated_at
)

AIConversation(owner, title, messages, context_items, created_at, updated_at)

# Advanced Models
ResearchSnapshot(item, text_hash, html_hash, extracted_text, screenshot, captured_at)

Collection(owner, name, slug, description, icon, is_public, share_token, created_at, updated_at)

CollectionItem(collection, item, order, added_at)

Glossary(owner, term, definition, source_item, category)

Monitor(item, frequency, last_check_at, last_change_at, is_active)
```

---

## URL Structure

### Complete URL Map

```python
# Dashboard
/immigration/                                  → Dashboard

# Quick Capture
/immigration/quick-save/                       → Quick save form (GET/POST)
/immigration/api/capture/                      → API endpoint for extension (POST)

# Item Management
/immigration/items/                            → Item list (with filters)
/immigration/items/<pk>/                       → Item detail
/immigration/items/<pk>/edit/                  → Edit item
/immigration/items/<pk>/delete/                → Delete item (confirmation)
/immigration/items/<pk>/favorite/              → Toggle favorite (POST)
/immigration/items/<pk>/archive/               → Toggle archive (POST)

# Notes
/immigration/items/<pk>/notes/add/             → Add note to item
/immigration/notes/<pk>/edit/                  → Edit note
/immigration/notes/<pk>/delete/                → Delete note

# Organization
/immigration/categories/                       → Category list
/immigration/categories/<slug>/                → Category detail (filtered items)
/immigration/categories/create/                → Create category
/immigration/tags/                             → Tag cloud/list
/immigration/tags/<slug>/                      → Tag detail (filtered items)
/immigration/favorites/                        → Favorites list
/immigration/archived/                         → Archived items

# Search
/immigration/search/                           → Search results

# AI Features (Phase 2)
/immigration/items/<pk>/ai-summarize/          → Generate AI summary (POST)
/immigration/items/<pk>/ai-extract/            → Extract entities (POST)
/immigration/ai-chat/                          → AI chat interface
/immigration/ai-chat/<pk>/                     → Specific conversation
/immigration/api/ai-ask/                       → AI Q&A endpoint (POST)

# Advanced Features (Phase 3)
/immigration/items/<pk>/history/               → Snapshot history
/immigration/items/<pk>/monitor/               → Enable/disable monitoring
/immigration/compare/                          → Comparison tool (multi-select items)
/immigration/collections/                      → Collection list
/immigration/collections/<slug>/               → Collection detail
/immigration/collections/create/               → Create collection
/immigration/glossary/                         → Glossary list
/immigration/glossary/<term>/                  → Term detail
/immigration/export/item/<pk>/                 → Export item as PDF
/immigration/export/collection/<slug>/         → Export collection as PDF
/immigration/bookmarklet/                      → Bookmarklet code page

# API Endpoints (for extension)
/immigration/api/v1/auth/                      → OAuth/token auth
/immigration/api/v1/items/                     → CRUD items (REST)
/immigration/api/v1/notes/                     → CRUD notes
/immigration/api/v1/search/                    → Search API
```

---

## Technology Stack

### Backend (Django)
- **Framework**: Django 5.1.4
- **Database**: SQLite (dev), PostgreSQL (production)
- **Auth**: Django built-in authentication
- **Storage**: Local media files (dev), S3 (production optional)

### Frontend
- **Templates**: Django templates
- **CSS Framework**: Tailwind CSS 3.x
- **Component Library**: DaisyUI
- **JavaScript**: Alpine.js (minimal interactivity)
- **Rich Text**: Quill or SimpleMDE (markdown editor)
- **Charts**: Chart.js (optional for analytics)

### External APIs & Libraries
- **OpenAI API**: GPT-4o-mini for AI features
- **Web Scraping**: BeautifulSoup4, Requests, Readability-lxml
- **PDF Processing**: PyPDF2 or pdfplumber
- **Screenshot**: Playwright (optional, for full-page screenshots)
- **Markdown**: python-markdown (rendering notes)

### Python Packages
```txt
# Core Django
django==5.1.4
pillow
python-dateutil

# Web scraping & parsing
beautifulsoup4
requests
lxml
readability-lxml

# PDF handling
pypdf2
pdfplumber

# AI
openai

# Markdown
markdown

# Optional
playwright  # For screenshots
python-slugify  # For slug generation
django-taggit  # Alternative tagging library
```

---

## Implementation Checklist

### Phase 1: MVP (Week 1-2)

**Day 1-2: Project Setup**
- [ ] Create `immigration` Django app
- [ ] Add to `INSTALLED_APPS`
- [ ] Create all Phase 1 models
- [ ] Generate migrations
- [ ] Run migrations
- [ ] Register models in admin
- [ ] Create URL configuration
- [ ] Include in main `urls.py`

**Day 3-4: Dashboard & Quick Save**
- [ ] Create `base.html` template (with navbar)
- [ ] Build dashboard view & template
- [ ] Implement quick save form
- [ ] Create `utils.py` with metadata fetching
- [ ] Test auto-enrichment pipeline
- [ ] Add success/error messages

**Day 5-6: Item Management**
- [ ] Build item list view (with filters)
- [ ] Create item detail view
- [ ] Implement item edit/delete
- [ ] Add favorites toggle
- [ ] Add archive toggle
- [ ] Style with Tailwind/DaisyUI cards

**Day 7-8: Notes & Organization**
- [ ] Build note CRUD views
- [ ] Add markdown rendering
- [ ] Create category system
- [ ] Implement tagging
- [ ] Add search functionality
- [ ] Test full workflow

**Day 9-10: Polish & Testing**
- [ ] Responsive design tweaks
- [ ] Loading states & animations
- [ ] Error handling
- [ ] Write unit tests
- [ ] Create seed demo data
- [ ] Documentation

### Phase 2: AI Integration (Week 3-4)

**Day 11-12: OpenAI Setup**
- [ ] Add OpenAI API key to settings
- [ ] Create `ai_utils.py`
- [ ] Implement summarization function
- [ ] Test with sample items
- [ ] Add cost tracking

**Day 13-14: Summarization UI**
- [ ] Add "Summarize" button to item detail
- [ ] Create AIExtract model
- [ ] Display summaries in collapsible card
- [ ] Add "Save to Notes" feature
- [ ] Show token usage

**Day 15-16: Smart Extraction**
- [ ] Implement entity extraction (forms, fees, deadlines)
- [ ] Parse and structure extracted data
- [ ] Display in badges/tables
- [ ] Make searchable

**Day 17-18: AI Q&A (RAG)**
- [ ] Build chat interface
- [ ] Implement RAG logic
- [ ] Create conversation model
- [ ] Display citations
- [ ] Test with various questions

**Day 19-20: Testing & Refinement**
- [ ] Test all AI features
- [ ] Optimize prompts for accuracy
- [ ] Add rate limiting
- [ ] Cost analysis
- [ ] Documentation

### Phase 3: Advanced Features (Week 5-6)

**Day 21-23: Change Detection**
- [ ] Implement snapshot system
- [ ] Build monitoring scheduler (Celery or django-cron)
- [ ] Create diff view
- [ ] Add notification system

**Day 24-26: Collections & PDF**
- [ ] Build collection system
- [ ] Add PDF upload
- [ ] Implement PDF text extraction
- [ ] Create PDF viewer

**Day 27-28: Comparison & Glossary**
- [ ] Build comparison tool
- [ ] Implement glossary builder
- [ ] Add bookmarklet page

**Day 29-30: Export & Polish**
- [ ] PDF export functionality
- [ ] CSV export
- [ ] Shareable links
- [ ] Final testing

### Phase 4: Browser Extension (Week 7-8)

**Day 31-35: Extension Development**
- [ ] Set up extension project
- [ ] Build manifest.json
- [ ] Create popup UI
- [ ] Implement one-click save
- [ ] Add authentication

**Day 36-40: Features & Testing**
- [ ] Context menu integration
- [ ] Highlight & save
- [ ] Offline sync
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Package for distribution

---

## Success Metrics

### MVP Success Criteria
- [ ] Can save a link in < 5 seconds
- [ ] Auto-fetch works for 90%+ of immigration sites
- [ ] Search returns relevant results instantly
- [ ] Notes are easy to add and edit
- [ ] Mobile-responsive on all pages
- [ ] No critical bugs

### AI Feature Success Criteria
- [ ] Summaries are accurate and useful
- [ ] Entity extraction catches 80%+ of forms/fees
- [ ] Q&A answers are relevant with correct citations
- [ ] AI features cost < $0.10 per 100 items processed

### User Experience Goals
- [ ] New user can start saving links in < 1 minute
- [ ] Dashboard loads in < 500ms
- [ ] Search results appear in < 200ms
- [ ] UI is intuitive (no documentation needed for basics)
- [ ] Works perfectly on mobile devices

---

## Future Enhancements (Post-MVP)

### Integration Ideas
- [ ] Calendar integration (track visa appointment dates)
- [ ] Case tracker integration (link research to specific cases)
- [ ] Document manager integration (attach research to uploaded docs)

### Advanced AI Features
- [ ] Multi-lingual translation
- [ ] Document drafting (cover letters, RFE responses)
- [ ] Personalized recommendations
- [ ] Trend analysis (policy changes over time)

### Collaboration Features
- [ ] Multi-user workspaces
- [ ] Shared annotations
- [ ] Team chat on items
- [ ] Role-based permissions

### Mobile App
- [ ] React Native or Flutter app
- [ ] Offline-first architecture
- [ ] Push notifications
- [ ] Camera OCR (scan paper documents)

---

## Notes & Considerations

### Security
- User data is private by default (scope all queries to `request.user`)
- Sanitize all user input (especially URLs)
- Rate limit API endpoints
- Encrypt API keys (never commit to repo)
- CSP headers to prevent XSS

### Performance
- Index frequently queried fields (`owner`, `created_at`, `source_type`)
- Full-text search with PostgreSQL (later) or Elasticsearch (advanced)
- Cache expensive operations (AI summaries, metadata fetches)
- Lazy-load images and PDFs
- Paginate all lists (25-50 items per page)

### Cost Management (OpenAI)
- Use `gpt-4o-mini` for most tasks (cheaper, faster)
- Limit input text to 4000 chars
- Cache AI responses (don't regenerate)
- Allow users to opt-in to AI features
- Show token usage/cost per action

### Legal & Compliance
- Terms of Service (AI-generated content disclaimer)
- Privacy Policy (user data handling)
- Copyright notice (scraped content is for personal use)
- DMCA compliance (remove content on request)

---

## Getting Started

### Prerequisites
- Django project already set up ✅
- Python 3.12, Django 5.1.4 ✅
- Tailwind CSS / DaisyUI configured ✅
- OpenAI API key (for Phase 2)

### First Steps
1. Read this roadmap completely
2. Review Phase 1 checklist
3. Create `immigration` app: `python manage.py startapp immigration`
4. Copy Phase 1 models into `immigration/models.py`
5. Create migrations: `python manage.py makemigrations`
6. Apply migrations: `python manage.py migrate`
7. Start building dashboard view!

---

**Last Updated**: 2025-11-05  
**Version**: 1.0  
**Status**: Ready to implement Phase 1 MVP

---

## Quick Reference

**App Name**: `immigration`  
**Namespace**: `immigration:`  
**Main URL**: `/immigration/`  
**Templates Dir**: `immigration/templates/immigration/`  
**Static Files**: `immigration/static/immigration/`  

**Key Utilities**:
- `immigration/utils.py` - Metadata fetching, text extraction
- `immigration/ai_utils.py` - OpenAI integration (Phase 2)
- `immigration/admin.py` - Django admin customization

**Management Commands** (to create):
- `immigration_seed_demo` - Create sample data
- `immigration_monitor` - Check for content changes (Phase 3)
- `immigration_cleanup` - Archive old items, clean up orphaned files

---

🎯 **Ready to build!** Start with Phase 1, Day 1-2. Let's create an amazing immigration research tool!

