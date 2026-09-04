from fastapi import FastAPI

from app.routers import auth, customers, tickets, categories, comments, attachments, notifications, sla, ticket_history, dashboard,audit_logs
from app.services import sla_service


app = FastAPI(
    title="CRM & Customer Support Management System",
    description="Backend API for CRM and Customer Support Management",
    version="1.0.0",
    docs_url="/",
    redoc_url=None
)


app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(tickets.router)
app.include_router(categories.router)
app.include_router(comments.router)
app.include_router(attachments.router)
app.include_router(notifications.router)
app.include_router(sla.router)
app.include_router(ticket_history.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy"
    }