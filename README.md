# 📝 Markdown Note-Taking & Grammar Checker API

A robust RESTful API built with **Django** and **Django REST Framework (DRF)** for creating, managing, and rendering Markdown notes with automated multi-pass grammar and spell checking powered by **LanguageTool**.

---

## 🌟 Key Features

- **Markdown Notes Management**: Full CRUD (Create, Read, Update, Delete) support for notes with title, markdown content, and timestamps.
- **File Upload Support**: Upload `.md` or `.txt` markdown files directly via `multipart/form-data`.
- **Multi-Pass Grammar & Spell Check**:
  - Automatically checks grammar and spelling with detailed rule descriptions, offset positions, error context, and replacement suggestions.
  - Multi-pass analysis: Fixes detected spelling typos on a shadow pass to reveal dependent grammatical mistakes.
  - Remote LanguageTool API integration — **no local Java installation required**.
- **Markdown to HTML Rendering**:
  - Convert markdown notes to clean HTML formatted JSON.
  - Direct raw HTML rendering (`?raw=true` or `?view=html`) to preview notes directly in any web browser.
- **Fully Tested**: Built-in automated test suite covering all endpoints, file uploads, grammar verification, and HTML rendering.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Django (>= 5.0 / 6.1) |
| **API Framework** | Django REST Framework (DRF >= 3.14) |
| **Markdown Engine** | Python-Markdown (>= 3.5) |
| **Grammar Engine** | `language-tool-python` (LanguageTool Cloud API) |
| **Database** | SQLite3 (default, zero-configuration) |
| **HTTP Client** | Requests (>= 2.31) |

---

## 📁 Project Structure

```text
note taking/
├── Note_markdown/               # Django project root
│   ├── manage.py                # Django management script
│   ├── db.sqlite3               # SQLite database
│   ├── Note_markdown/           # Project configuration
│   │   ├── settings.py          # App settings & installed apps
│   │   ├── urls.py              # Root URL routing
│   │   ├── wsgi.py              # WSGI entry point
│   │   └── asgi.py              # ASGI entry point
│   └── grammer/                 # Main Django application
│       ├── models.py            # Notes model (title, content, timestamp)
│       ├── Serializer.py        # NotesSerializer with note/content aliases
│       ├── views.py             # Views for grammar, notes CRUD & markdown render
│       ├── tests.py             # Test suite (9 test cases)
│       └── admin.py             # Django admin integration
├── requirements.txt             # Project dependencies
├── .gitignore                   # Git ignore rules
└── readme.md                    # Project documentation
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites

- **Python**: Version 3.10 or higher installed on your system.
- **Git** (optional): For version control.

---

### 2. Setup Virtual Environment

Navigate to the project directory:

```bash
cd "note taking"
```

Create a virtual environment:

**Windows (PowerShell / CMD):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

Install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### 4. Apply Database Migrations

Set up the SQLite database schema:

```bash
python Note_markdown/manage.py migrate
```

*(Or navigate into `cd Note_markdown` and run `python manage.py migrate`)*

---

### 5. Run the Development Server

Start the Django local development server:

```bash
python Note_markdown/manage.py runserver
```

The server will start at: **`http://127.0.0.1:8000/`**

---

### 6. Run the Test Suite

Run the automated tests to verify that everything works properly:

```bash
python Note_markdown/manage.py test grammer
```

Expected output:
```text
Ran 9 tests in ...s

OK
```

---

## 📚 API Documentation & Endpoints

Base URL: `http://127.0.0.1:8000`

### Summary of Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/notes/` | List all saved notes (newest first) |
| `POST` | `/notes/` | Create a note (via JSON or `.md` file upload) |
| `GET` | `/notes/<id>/` | Retrieve a specific note by ID |
| `PUT` | `/notes/<id>/` | Update a note's title or content |
| `DELETE` | `/notes/<id>/` | Delete a note |
| `POST` | `/check-grammar/` | Check grammar of text or a saved note |
| `GET` / `POST` | `/notes/<id>/grammar/` | Check grammar of a specific saved note |
| `GET` | `/notes/<id>/render/` | Render note markdown to HTML (JSON response) |
| `GET` | `/notes/<id>/render/?raw=true` | Render note directly as a formatted HTML webpage |

---

### Detailed Endpoint Specifications

#### 1. List All Notes
- **URL**: `GET /notes/`
- **Response**: `200 OK`
```json
[
  {
    "id": 1,
    "title": "Meeting Notes",
    "content": "# Sprint Planning\n- Discuss roadmap\n- Assign tasks",
    "note": "# Sprint Planning\n- Discuss roadmap\n- Assign tasks",
    "timestamp": "2026-09-27T09:30:00Z"
  }
]
```

---

#### 2. Create Note (JSON)
- **URL**: `POST /notes/`
- **Header**: `Content-Type: application/json`
- **Body**:
```json
{
  "title": "Docker Setup Guide",
  "content": "# Docker\nDocker simplify application deployment."
}
```
*(Note: You can also use `"note"` instead of `"content"`)*
- **Response**: `201 Created`
```json
{
  "id": 2,
  "title": "Docker Setup Guide",
  "content": "# Docker\nDocker simplify application deployment.",
  "note": "# Docker\nDocker simplify application deployment.",
  "timestamp": "2026-09-27T09:35:12Z"
}
```

---

#### 3. Upload Note as File (.md / .txt)
- **URL**: `POST /notes/`
- **Header**: `Content-Type: multipart/form-data`
- **Form Data**:
  - `file`: `<your_document.md>` (Binary file)
  - `title`: *(Optional)* Note title. If omitted, the uploaded filename will be used.
- **Response**: `201 Created`

---

#### 4. Retrieve Single Note
- **URL**: `GET /notes/<id>/`
- **Response**: `200 OK`
```json
{
  "id": 2,
  "title": "Docker Setup Guide",
  "content": "# Docker\nDocker simplify application deployment.",
  "note": "# Docker\nDocker simplify application deployment.",
  "timestamp": "2026-09-27T09:35:12Z"
}
```

---

#### 5. Update Note
- **URL**: `PUT /notes/<id>/`
- **Header**: `Content-Type: application/json`
- **Body** (partial updates allowed):
```json
{
  "title": "Updated Docker Guide",
  "content": "# Docker\nDocker simplifies application deployment."
}
```
- **Response**: `200 OK`

---

#### 6. Delete Note
- **URL**: `DELETE /notes/<id>/`
- **Response**: `204 No Content`

---

#### 7. Check Grammar (Ad-hoc Text or Note ID)
- **URL**: `POST /check-grammar/`
- **Header**: `Content-Type: application/json`
- **Body Option A (Raw Text)**:
```json
{
  "text": "This are bad test."
}
```
- **Body Option B (Existing Note ID)**:
```json
{
  "note_id": 2
}
```
- **Response**: `200 OK`
```json
{
  "text": "This are bad test.",
  "grammar_errors_count": 2,
  "issues": [
    {
      "error_word": "This",
      "rule_id": "THIS_NNS",
      "message": "The singular demonstrative pronoun 'this' does not agree with the plural verb 'are'. Did you mean 'these'?",
      "suggestions": ["These"],
      "offset": 0,
      "error_length": 4,
      "context": "This are bad test."
    },
    {
      "error_word": "are",
      "rule_id": "PLURAL_VERB_AFTER_THIS",
      "message": "The verb 'are' is plural. Did you mean: 'is'?",
      "suggestions": ["is"],
      "offset": 5,
      "error_length": 3,
      "context": "This are bad test."
    }
  ]
}
```

---

#### 8. Check Grammar of a Saved Note
- **URL**: `GET /notes/<id>/grammar/` or `POST /notes/<id>/grammar/`
- **Response**: `200 OK`
```json
{
  "note_id": 2,
  "title": "Docker Setup Guide",
  "text": "# Docker\nDocker simplify application deployment.",
  "grammar_errors_count": 1,
  "issues": [
    {
      "error_word": "simplify",
      "rule_id": "PERS_PRON_AGREEMENT",
      "message": "Did you mean 'simplifies'?",
      "suggestions": ["simplifies"],
      "offset": 16,
      "error_length": 8,
      "context": "Docker simplify application deployment."
    }
  ]
}
```

---

#### 9. Render Markdown as HTML

##### A. Structured JSON:
- **URL**: `GET /notes/<id>/render/` (or `GET /notes/<id>/html/`)
- **Response**: `200 OK`
```json
{
  "id": 2,
  "title": "Docker Setup Guide",
  "markdown": "# Docker\nDocker simplifies application deployment.",
  "html": "<h1>Docker</h1>\n<p>Docker simplifies application deployment.</p>"
}
```

##### B. Raw HTML Browser View:
- **URL**: `GET /notes/<id>/render/?raw=true` (or `?view=html`)
- **Headers**: `Content-Type: text/html`
- **Response**: Directly renders HTML in your browser tab for visual preview.

---

## 💻 Example Usage

### Using cURL

#### 1. Create a note:
```bash
curl -X POST http://127.0.0.1:8000/notes/ \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Quick Note\", \"content\": \"# Meeting\\nThis are an important note.\"}"
```

#### 2. Upload a markdown file:
```bash
curl -X POST http://127.0.0.1:8000/notes/ \
  -F "file=@my_notes.md" \
  -F "title=Uploaded Notes"
```

#### 3. Check grammar of arbitrary text:
```bash
curl -X POST http://127.0.0.1:8000/check-grammar/ \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"She do not likes apples.\"}"
```

#### 4. Check grammar of saved note #1:
```bash
curl http://127.0.0.1:8000/notes/1/grammar/
```

#### 5. Render note #1 markdown as raw HTML:
Open in browser or run:
```bash
curl http://127.0.0.1:8000/notes/1/render/?raw=true
```

---

### Using Python Requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000"

# 1. Create a Note
response = requests.post(f"{BASE_URL}/notes/", json={
    "title": "Grammar Test Note",
    "content": "# Intro\nThere is many issues with this sentences."
})
note_id = response.json()["id"]
print(f"Created note ID: {note_id}")

# 2. Check Grammar
grammar_resp = requests.get(f"{BASE_URL}/notes/{note_id}/grammar/")
print("Grammar issues detected:", grammar_resp.json()["grammar_errors_count"])

# 3. Render HTML
render_resp = requests.get(f"{BASE_URL}/notes/{note_id}/render/")
print("Rendered HTML:\n", render_resp.json()["html"])
```

---

## 🧪 Testing

The project includes unit and integration tests located in `Note_markdown/grammer/tests.py`.

Run tests with:
```bash
python Note_markdown/manage.py test grammer
```

The test suite validates:
1. `test_grammar_check_empty`: Rejection of empty input.
2. `test_grammar_check_saved_note_by_id`: Grammar analysis of saved note.
3. `test_grammar_check_endpoint_with_note_id`: Grammar check via POST payload with `note_id`.
4. `test_get_notes`: Notes retrieval and listing.
5. `test_create_note_with_content`: Note creation with title and markdown body.
6. `test_create_note_with_file_upload`: Multipart file upload for `.md` files.
7. `test_note_detail_and_delete`: Single note retrieval and deletion (HTTP 204).
8. `test_render_markdown_json`: Markdown converted to HTML within JSON response.
9. `test_render_markdown_raw_html`: Markdown converted and returned with `text/html` header.

---

## 💡 Notes & Best Practices

- **Zero-Setup LanguageTool**: The API defaults to LanguageTool's official cloud service (`https://api.languagetool.org/`), with automated fallback to local Java if configured. No Java runtime is required on the host system.
- **Port Conflicts**: If port `8000` is in use, start the server on a custom port:
  ```bash
  python Note_markdown/manage.py runserver 8080
  ```
- **Admin Panel**: You can access Django's admin panel at `http://127.0.0.1:8000/admin/`. Create a superuser with:
  ```bash
  python Note_markdown/manage.py createsuperuser
  ```

https://roadmap.sh/projects/markdown-note-taking-app
