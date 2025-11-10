# Invoice Management Backend

Django REST API backend for the Invoice Management System.

## Setup

1. **Activate the virtual environment:**
   ```bash
   .\venv\Scripts\activate
   ```

2. **Install dependencies (if needed):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   
   Or use the batch file:
   ```bash
   runserver.bat
   ```

## Important Notes

⚠️ **Always use the virtual environment when running the server!**

The server must be run with the virtual environment activated. If you see `cryptography` import errors, it means the server is using the system Python instead of the venv.

**To fix:**
1. Stop the current server (Ctrl+C)
2. Activate the venv: `.\venv\Scripts\activate`
3. Run: `python manage.py runserver`

## API Endpoints

- `POST /api/token/` - Get JWT token (login)
- `POST /api/token/refresh/` - Refresh JWT token
- `GET /api/invoices/` - List all invoices (requires authentication)
- `POST /api/invoices/` - Create new invoice (requires authentication)
- `GET /api/invoices/:id/` - Get invoice details (requires authentication)
- `PUT /api/invoices/:id/` - Update invoice (requires authentication)
- `DELETE /api/invoices/:id/` - Delete invoice (requires authentication)

## Admin Panel

Access the Django admin at: `http://localhost:8000/admin/`


