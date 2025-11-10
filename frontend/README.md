# Invoice Management Frontend

A modern Vue.js/Nuxt 3 frontend for the Invoice Management System.

## Features

- 🔐 JWT Authentication
- 📊 Dashboard to view all invoices
- ➕ Create new invoices
- ✏️ Edit existing invoices
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file (optional, defaults to `http://localhost:8000/api`):
```
API_BASE_URL=http://localhost:8000/api
```

3. Run the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── assets/          # CSS and static assets
├── components/      # Vue components
├── composables/    # Composable functions
├── layouts/         # Layout components
├── middleware/      # Route middleware
├── pages/           # Application pages
│   ├── login.vue           # Login page
│   ├── dashboard.vue       # Dashboard (invoice list)
│   └── invoices/
│       ├── new.vue          # Create invoice
│       └── [id]/edit.vue    # Edit invoice
├── stores/          # Pinia stores
└── nuxt.config.ts   # Nuxt configuration
```

## Pages

- **Login** (`/login`) - User authentication
- **Dashboard** (`/dashboard`) - View all invoices
- **New Invoice** (`/invoices/new`) - Create a new invoice
- **Edit Invoice** (`/invoices/:id/edit`) - Edit an existing invoice

## Authentication

The app uses JWT tokens stored in localStorage. The auth middleware protects routes that require authentication.

## API Integration

The frontend communicates with the Django REST API backend. Make sure the backend is running on `http://localhost:8000` (or update the API_BASE_URL in the config).


