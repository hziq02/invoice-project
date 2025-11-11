# Invoice Project

This is a monorepo containing the Invoice Management System with user tracking functionality.

## Project Structure

```
invoice-project/
├── backend/            # Django REST API Backend
│   ├── core/           # Django core settings
│   ├── invoices/       # Invoice app with tracking models
│   └── manage.py       # Django management script
│
└── frontend/           # Nuxt.js Frontend
    ├── pages/          # Vue pages
    ├── stores/         # Pinia stores
    ├── middleware/     # Nuxt middleware
    └── src/utils/      # Utility functions (tracking)
```

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Features

- Invoice Management (CRUD operations)
- User Authentication (JWT)
- User Tracking System:
  - Session tracking
  - Page event tracking
  - Event-based session end detection (browser events)

## Notes

- Backend and frontend are in separate folders for better organization
- Both can be developed and deployed independently

