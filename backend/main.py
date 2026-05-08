import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from formcraft.router import router as formcraft_router
from formcraft import models as fc_models
from formcraft.database import engine as fc_engine, SessionLocal
from querymind.router import router as querymind_router


def seed_templates():
    from formcraft.models import Template
    db = SessionLocal()
    try:
        if db.query(Template).count() > 0:
            return
        templates = [
            {
                "id": "contact",
                "title": "Contact Us Form",
                "category": "contact",
                "description": "Simple contact form with name, email and message.",
                "color": "#059669",
                "badge": None,
                "tags": ["contact", "enquiry"],
                "score": 72,
                "score_tip": "Add phone field to increase reach",
                "suggestions": [
                    {"icon": "📱", "title": "Add Phone field", "text": "Reach users on WhatsApp too.", "field": {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "First Name", "placeholder": "John", "required": True},
                        {"type": "text", "label": "Last Name", "placeholder": "Doe", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    {"type": "textarea", "label": "Message", "placeholder": "Write your message here...", "required": True},
                    {"type": "submit", "label": "Send Message", "color": "#059669"},
                ],
            },
            {
                "id": "registration",
                "title": "Event Registration Form",
                "category": "registration",
                "description": "Register attendees for events, workshops or webinars.",
                "color": "#7c3aed",
                "badge": "⭐ New",
                "tags": ["event", "registration", "workshop"],
                "score": 80,
                "score_tip": "Add dietary preferences for 90+",
                "suggestions": [
                    {"icon": "🍽️", "title": "Add Dietary Preferences", "text": "Important for catered events.", "field": {"type": "select", "label": "Dietary Preference", "options": ["Vegetarian", "Vegan", "Non-Vegetarian", "Jain", "No Preference"], "required": False}},
                    {"icon": "👥", "title": "Add +1 / Guest option", "text": "Allow attendees to bring guests.", "field": {"type": "radio", "label": "Bringing a Guest?", "options": ["Yes", "No"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Session", "options": ["Morning (9am-12pm)", "Afternoon (2pm-5pm)", "Evening (6pm-9pm)"], "required": True},
                    {"type": "submit", "label": "Register Now", "color": "#7c3aed"},
                ],
            },
            {
                "id": "feedback",
                "title": "Customer Feedback Form",
                "category": "feedback",
                "description": "Collect ratings and feedback from customers.",
                "color": "#d97706",
                "badge": None,
                "tags": ["feedback", "rating", "review"],
                "score": 75,
                "score_tip": "Add NPS score question for 92+",
                "suggestions": [
                    {"icon": "📊", "title": "Add NPS Score", "text": "Net Promoter Score is industry standard.", "field": {"type": "range", "label": "How likely are you to recommend us? (0-10)", "required": False}},
                    {"icon": "📸", "title": "Add Photo Upload", "text": "Visual feedback increases credibility.", "field": {"type": "file", "label": "Upload a Photo", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
                    {"type": "rating", "label": "Overall Rating", "required": True},
                    {"type": "select", "label": "What did you purchase?", "options": ["Product", "Service", "Subscription", "Other"], "required": True},
                    {"type": "textarea", "label": "Your Feedback", "placeholder": "Tell us what you think...", "required": True},
                    {"type": "submit", "label": "Submit Feedback", "color": "#d97706"},
                ],
            },
            {
                "id": "payment",
                "title": "Order & Payment Form",
                "category": "payment",
                "description": "Complete checkout with shipping, card details & order summary.",
                "color": "#1a56db",
                "badge": "🔥 Popular",
                "tags": ["checkout", "payment", "order"],
                "score": 78,
                "score_tip": "Add UPI & promo code to reach 95+",
                "suggestions": [
                    {"icon": "💳", "title": "Add UPI / Wallet field", "text": "Indian users prefer UPI.", "field": {"type": "radio", "label": "Payment Method", "options": ["UPI", "Credit Card", "Debit Card", "Net Banking"], "required": True}},
                    {"icon": "🎁", "title": "Add promo code field", "text": "Promo codes increase conversions by 12%.", "field": {"type": "text", "label": "Promo Code", "placeholder": "Enter promo code", "required": False}},
                    {"icon": "📦", "title": "Add delivery date picker", "text": "Reduces failed deliveries by 30%.", "field": {"type": "date", "label": "Preferred Delivery Date", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "John Doe", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "text", "label": "Shipping Address", "placeholder": "123 Main St, City", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "City", "placeholder": "Mumbai", "required": True},
                        {"type": "text", "label": "PIN Code", "placeholder": "400001", "required": True},
                    ]},
                    {"type": "divider"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Place Order", "color": "#1a56db"},
                ],
            },
        ]
        for t in templates:
            db.add(Template(**t))
        db.commit()
        print(f"✅ Auto-seeded {len(templates)} templates")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    fc_models.Base.metadata.create_all(bind=fc_engine)
    seed_templates()
    yield


app = FastAPI(title="FormCraft + QueryMind API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(formcraft_router)
app.include_router(querymind_router)

# Serve React frontend (production)
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
