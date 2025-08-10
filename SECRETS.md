# Secrets to set

## GitHub → Settings → Secrets and variables → Actions
- `DATABASE_URL` = your Supabase Postgres URI (e.g., `postgresql://...:5432/postgres?sslmode=require`)

## Streamlit Cloud → App → Settings → Secrets
```
DATABASE_URL = "postgresql://...:5432/postgres?sslmode=require"
APP_PASSWORD = "your-password-here"   # optional; omit to make public
```
