<div align="center">

#  Property Rental Backend

FastAPI + Tortoise ORM backend for a property rental platform featuring authentication, property & media management, team management, contact system, and customizable screening (application) forms.

![Stack](https://img.shields.io/badge/FastAPI-0.117+-009688?logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) ![DB](https://img.shields.io/badge/PostgreSQL-Supabase-336791?logo=postgresql&logoColor=white) ![Auth](https://img.shields.io/badge/Auth-JWT-green) ![Images](https://img.shields.io/badge/Images-Base64-orange)

</div>

---

##  Features

-  JWT auth with role-based access (user/admin) & cookie sessions
-  User profiles with base64 image storage
-  Property CRUD with media gallery & cover image selection
-  Base64 image ingestion (Pillow compression + validation)
-  Team member management (public showcase)
-  Contact system with admin replies + email notifications
-  Customizable screening/application question forms (text/number/date)
-  Fully documented APIs (see `PROPERTY_API.md`, `CONTACT_API.md`, `SCREENING_API.md`)
-  Email service with templated messages (auth + contact)

---

##  Project Structure

```
Backend/
├── main.py                     # FastAPI entrypoint
├── pyproject.toml              # Dependencies (managed with uv)
├── uv.lock                     # Lock file
├── .env                        # Environment variables (NOT committed)
│
├── authMiddleware/             # Auth & role middlewares
│   ├── authMiddleware.py
│   └── roleMiddleware.py
│
├── config/                     # Config utilities
│   ├── fileUpload.py           # Image processing & base64 conversion
│   └── nodemailer.py           # Email SMTP setup
│
├── controller/                 # Business logic controllers
│   ├── userController.py
│   ├── propertyController.py
│   ├── propertyMediaController.py
│   ├── teamController.py
│   ├── contactController.py
│   └── screeningQuestionController.py
│
├── dbConnection/               # DB init / ORM config
│   └── dbConfig.py
│
├── emailService/               # Email templates/services
│   ├── authEmail.py
│   └── contactEmail.py
│
├── model/                      # Tortoise ORM models
│   ├── userModel.py
│   ├── propertyModel.py
│   ├── propertyMediaModel.py
│   ├── teamModel.py
│   ├── contactModel.py
│   └── screeningQuestionModel.py
│
├── routes/                     # API routers
│   ├── authRoute.py
│   ├── profileRoute.py
│   ├── propertyRoute.py
│   ├── teamRoute.py
│   ├── contactRoute.py
│   └── screeningQuestionRoute.py
│
├── schemas/                    # Pydantic schemas
│   ├── userSchemas.py
│   ├── propertySchemas.py
│   ├── propertyMediaSchemas.py
│   ├── teamSchemas.py
│   ├── contactSchemas.py
│   └── screeningQuestionSchemas.py
│
├── services/                   # Service helpers
│   ├── authServices.py
│   └── cookieServices.py
│
├── CONTACT_API.md              # Contact endpoints docs
├── PROPERTY_API.md             # Property & media docs
├── SCREENING_API.md            # Screening form system docs
├── SYSTEM_OVERVIEW.md          # High-level architecture
└── README.md                   # This file
```

---

##  Tech Stack

| Layer            | Tools |
|------------------|-------|
| Web Framework    | FastAPI |
| ORM              | Tortoise ORM (async) |
| Database         | PostgreSQL (Supabase) |
| Auth             | JWT + Cookie sessions |
| Email            | SMTP (aiosmtplib) |
| Media            | Pillow + base64 storage |
| Validation       | Pydantic V2 |
| Environment      | python-dotenv |
| Runtime          | uvicorn / uv |

---

##  Environment Variables (`.env`)

Create a `.env` file at project root:

```
PORT=8001
FRONTEND_URL=http://localhost:3000

# Postgres / Supabase
DB_USER=postgres
DB_PASS=yourpassword
DB_HOST=your-host.supabase.co
DB_PORT=5432
DB_NAME=postgres

# JWT / Auth
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Email / SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=youremail@gmail.com
EMAIL_PASS=your_app_password
EMAIL_FROM=Property Rentals <youremail@gmail.com>
```

---

##  Quick Start (Using `uv`)

### 1. Clone Repository
```bash
git clone https://github.com/PropertyRent/Backend-Server.git
cd Backend-Server/Backend
```

### 2. Install uv (if missing)
```bash
pip install uv
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Setup Environment
```bash
copy .env.example .env   # (or create manually)
```

### 5. Run Server
```bash
uv run python main.py
# or hot reload (if you add --reload support)
uv run uvicorn main:app --reload --port 8001
```

### 6. API Docs
- Swagger: http://localhost:8001/docs  
- ReDoc: http://localhost:8001/redoc

---

##  Automatic DB Initialization
On startup Tortoise ORM connects and (with `generate_schemas=True` in `dbConfig.py` via `register_tortoise`) creates tables for all listed models in `TORTOISE_ORM['apps']['models']['models']`.

Ensure `statement_cache_size=0` (already set) for Supabase PgBouncer compatibility.

---

##  Authentication Flow
1. User registers → record created → optional verification email
2. User logs in → JWT created → stored in `token` HTTP-only cookie
3. Protected routes read cookie → middleware validates token → role enforced
4. Admin-only endpoints use `authorize_roles(["admin"])`

Sequence (simplified):
```
Client → POST /api/auth/login → JWT → Set-Cookie(token)
Client → GET /api/user/profile → Cookie sent → Middleware validates → 200 OK
```

---

##  Property & Media Flow

```
User (auth) → POST /api/properties → Property created
		  → POST /api/properties/{id}/media (base64 image)
		  → GET /api/properties?filters=... (public or protected depending design)
Admin → DELETE /api/admin/properties/{id}
```

Media Handling:
- Image uploaded → validated (MIME) → compressed (Pillow) → stored as base64 TEXT
- Cover image flagged via specific field (`is_cover_image`)

---

##  Team Management Flow
```
Admin → POST /api/team/members → add team member (base64 photo)
Public → GET /api/team/members → list team
Admin → PUT/DELETE /api/team/members/{id}
```

---

##  Contact System Flow
```
Visitor → POST /api/public/contact
	→ DB store (status=pending)
	→ Email: user confirmation + admin notification
Admin → GET /api/admin/contact → list
Admin → POST /api/admin/contact/{id}/reply → sets status=replied & emails user
Admin → PUT /api/admin/contact/{id}/status → mark resolved
```

---

##  Screening (Custom Form) Flow
```
Admin → POST /api/admin/screening/questions (create many questions: text/number/date)
Public → GET /api/public/screening/questions (only active, ordered)
User  → POST /api/public/screening/responses (answers validated per type)
Admin → GET /api/admin/screening/responses → list w/ counts
Admin → GET /api/admin/screening/responses/{id} → full detail
```

Answer Storage:
- One `ScreeningResponse` per submission
- Each question answered via `ScreeningAnswer` with typed column (text/number/date)

---

##  High-Level Architecture

```
[ FastAPI Routers ] → [ Controllers ] → [ Models (Tortoise ORM) ] → PostgreSQL
			 ↓                ↓                 
		 Schemas         Services (auth, email, file)
			 ↓                ↓
		Request ↔ Response  External (SMTP)
```

Data Flow Example (Property Image Upload):
```
Client → POST /api/properties/{id}/media (multipart/base64) →
 fileUpload.py (validate + compress + base64) →
 propertyMediaController.py → Tortoise Model → DB
```

---

##  Route Reference

### Auth (`/api/auth`)
| Method | Route | Description |
|--------|-------|-------------|
| POST | /register | Register user |
| POST | /login | Login & set cookie |
| POST | /logout | (If implemented) Clear cookie |

### User Profile (`/api/user`)
| Method | Route | Description |
|--------|-------|-------------|
| GET | /profile | Get profile |
| PUT | /profile | Update profile (with optional photo) |

### Properties (`/api`)
(Representative; see `PROPERTY_API.md` for detailed filters)
| Method | Route | Description |
|--------|-------|-------------|
| POST | /properties | Create property |
| GET | /properties | List/filter properties |
| GET | /properties/{id} | Get property |
| PUT | /properties/{id} | Update property |
| DELETE | /properties/{id} | Delete (owner/admin) |
| POST | /properties/{id}/media | Add media |
| PUT | /properties/{id}/media/{media_id}/cover | Set cover image |
| DELETE | /properties/{id}/media/{media_id} | Remove media |

### Team (`/api`)
| Method | Route | Description |
|--------|-------|-------------|
| GET | /team/members | Public list |
| POST | /team/members | Create (admin) |
| PUT | /team/members/{id} | Update (admin) |
| DELETE | /team/members/{id} | Delete (admin) |

### Contact (`/api`)
| Method | Route | Description |
|--------|-------|-------------|
| POST | /public/contact | Submit inquiry |
| GET | /admin/contact | List (admin) |
| GET | /admin/contact/{id} | Detail (admin) |
| POST | /admin/contact/{id}/reply | Reply & email user |
| PUT | /admin/contact/{id}/status | Update status (admin) |
| DELETE | /admin/contact/{id} | Delete (admin) |

### Screening (`/api`)
| Method | Route | Description |
|--------|-------|-------------|
| GET | /public/screening/questions | Active questions |
| POST | /public/screening/responses | Submit answers |
| POST | /admin/screening/questions | Create question |
| GET | /admin/screening/questions | List (opt inactive) |
| PUT | /admin/screening/questions/{id} | Update |
| DELETE | /admin/screening/questions/{id} | Delete |
| PUT | /admin/screening/questions/reorder | Bulk reorder |
| GET | /admin/screening/responses | List submissions |
| GET | /admin/screening/responses/{id} | Detailed view |
| DELETE | /admin/screening/responses/{id} | Delete submission |

---

##  Suggested Improvements / Next Steps

- Add pagination & filtering docs to README for properties
- Add refresh token strategy (long-lived sessions)
- Add background tasks for email sending
- Introduce Alembic migrations (instead of auto-generate)
- Add structured logging (loguru / stdlib)
- Implement rate limiting (slowapi)
- Add unit/integration tests (pytest + httpx)
- Dockerize (compose: app + db + mailhog)

---

##  Security Notes
- Use HTTPS in production
- Rotate `JWT_SECRET` regularly
- Store images outside DB for scale (future S3/GCS option)
- Sanitize all user-generated HTML (if rendering anywhere)

---

##  Contributing
1. Fork repo
2. Create feature branch
3. Run lint/tests (if added)
4. Submit PR with description

---

##  License
Add your preferred license (e.g., MIT) here.

---

##  Support
Open an issue or email the maintainer at `youremail@example.com`.

---

Happy building! 

