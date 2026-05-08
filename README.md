# FormCraft + QueryMind

This repo contains two separate applications:

| App | Location | Purpose |
|-----|----------|---------|
| **FormCraft** | root `/` | Form builder with templates, submissions & stats |
| **QueryMind** | `backend/` + `frontend/` | Chat with any SQL database using plain English (AI-powered) |

---

## FormCraft

A FastAPI backend for building and managing forms.

### Setup

1. **Create `.env`** at the root:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/formcraft
   ```

2. **Install dependencies**:
   ```bash
   pip install -r "Requirements .txt"
   ```

3. **Create tables & seed templates**:
   ```bash
   python seed.py
   ```

4. **Run the server**:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/templates` | List all form templates |
| GET | `/api/templates/{id}` | Get a single template |
| GET | `/api/public/{form_id}` | Get any form by ID (template or custom) — used by public share links |
| POST | `/api/submissions` | Submit a form |
| GET | `/api/submissions` | List submissions (filter by `status`, `form_id`) |
| GET | `/api/submissions/{id}` | Get a submission |
| PATCH | `/api/submissions/{id}/read` | Mark submission as read |
| DELETE | `/api/submissions/{id}` | Delete a submission |
| DELETE | `/api/submissions` | Delete all submissions |
| GET | `/api/stats` | Dashboard stats |
| POST | `/api/forms` | Save a custom form (from Builder) |
| GET | `/api/forms` | List custom forms |
| GET | `/api/forms/{id}` | Get a custom form |

### Shareable Form Links

Every form gets a public URL that anyone can open and submit — no login required:

| Form type | Share URL format | Example |
|-----------|-----------------|---------|
| Template | `/form/{template-id}` | `http://localhost:3000/form/contact` |
| Custom (Builder) | `/form/custom_{id}` | `http://localhost:3000/form/custom_5` |

Click the **🔗 Share** button on any form card to copy the link to clipboard.

---

## QueryMind

Ask questions about any database in plain English — the AI generates and runs the SQL for you.

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example`):
```
GROQ_API_KEY=gsk_your_groq_api_key_here
```
Get your free Groq API key at [console.groq.com](https://console.groq.com).

Run the backend:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev        # starts at http://localhost:3000
```

The Vite dev server proxies `/api/*` requests to the backend at `http://localhost:8000`.

### Supported Databases

- PostgreSQL: `postgresql://user:password@host:5432/dbname`
- MySQL: `mysql+pymysql://user:password@host:3306/dbname`
- SQLite: `sqlite:///path/to/database.db`

---

## Project Structure

```
jotform/
├── start.sh         # Starts both backend and frontend
│
├── backend/         # FastAPI backend (FormCraft + QueryMind)
│   ├── main.py
│   ├── formcraft/
│   │   ├── router.py    # All /api/* routes
│   │   ├── models.py    # Template, Submission, CustomForm
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── database.py
│   ├── querymind/
│   ├── seed.py          # Seeds templates into DB
│   └── requirements.txt
│
└── frontend/        # React + Vite frontend
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   └── Navbar.jsx
    │   └── pages/
    │       ├── formcraft/
    │       │   ├── TemplatesPage.jsx   # Browse & use templates
    │       │   ├── BuilderPage.jsx     # Drag-and-drop form builder
    │       │   ├── SubmissionsPage.jsx # View all submissions
    │       │   ├── FormPage.jsx        # Public shareable form page
    │       │   └── formcraft.css
    │       └── querymind/
    │           └── QueryMindPage.jsx
    ├── vite.config.js
    └── package.json
```
