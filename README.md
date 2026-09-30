# ShopEase — Django + HTMX Performance Task

A presentation-ready server-rendered e-commerce interface built for **IT 424: Professional Elective 4 — Advanced Web Programming**.

## Requirements covered
- Django 5.x + SQLite
- Session-based cart; no customer accounts
- Simulated Cash on Delivery / Pay Later
- Product catalog, detail page, staff product management, cart, checkout, confirmation
- Django templates with inheritance and reusable partials
- Responsive custom CSS for mobile, tablet and desktop
- Media uploads via `MEDIA_ROOT` / `MEDIA_URL`
- Server-side validation including Philippine mobile format, price/stock ranges, cross-field Express shipping rule, and stock checks at add/update/checkout
- HTMX interactions: live catalog search/filter/sort, add-to-cart badge update, cart quantity update, cart removal, management search/delete, form validation swaps, shipping-total refresh, pagination, and loading indicator

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Then open `http://127.0.0.1:8000/`.

If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Demo data
The `seed_demo` command creates realistic sample categories and products so the interface is populated immediately. Re-running the command is safe: it uses `update_or_create` for the named sample records.

## HTMX hosting decision
HTMX is loaded from the official CDN in `templates/base.html`. The task permits a local static file or CDN. A CDN avoids bundling a third-party library into the submission and makes the version explicit (`2.0.6`), while the project’s own JavaScript remains under `static/store/js/`.

## HTMX map
| Interaction | Server response | Main attributes |
|---|---|---|
| Catalog search | Product grid partial | `hx-get`, `hx-trigger="keyup changed delay:300ms"`, `hx-target`, `hx-indicator` |
| Category/sort | Product grid partial | `hx-get`, `hx-trigger="change"`, `hx-include` |
| Add to cart | Inline feedback + OOB badge | `hx-post`, `hx-target`, `hx-swap-oob`, `hx-indicator` |
| Cart quantity | Cart container | `hx-post`, `hx-target`, `hx-indicator` |
| Remove cart item | Cart container | `hx-delete`, `hx-confirm`, `hx-target` |
| Staff search/delete | Management table | `hx-get` / `hx-delete`, `hx-target` |
| Product/checkout validation | Form partial | `hx-post`, `hx-swap="innerHTML"` |
| Pagination | Product grid area | `hx-get`, `hx-target` |
| Loading feedback | Global indicator | `hx-indicator` |

## Submission materials
- `analysis/Part_1_Interface_and_Data_Entry_Analysis.docx`
- `analysis/Reflection.docx`
- `submission/ShopEase_Submission_Checklist.docx`
- `fixtures/demo_data.json`
- `requirements.txt`

The screen recording must be captured by the student because it needs to show the student’s live environment. The checklist includes the exact 3–4 minute demo sequence and failed-validation cases required by the task.
