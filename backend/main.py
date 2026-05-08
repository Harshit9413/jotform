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
            {
                "id": "job_application",
                "title": "Job Application Form",
                "category": "hr",
                "description": "Collect resumes and details from job applicants.",
                "color": "#4f46e5",
                "badge": "⭐ New",
                "tags": ["hr", "jobs", "hiring", "recruitment"],
                "score": 82,
                "score_tip": "Add cover letter field to reach 95+",
                "suggestions": [
                    {"icon": "📝", "title": "Add Cover Letter", "text": "Helps assess communication skills.", "field": {"type": "textarea", "label": "Cover Letter", "placeholder": "Tell us why you're a great fit...", "required": False}},
                    {"icon": "🔗", "title": "Add LinkedIn Profile", "text": "Speeds up background checks.", "field": {"type": "text", "label": "LinkedIn Profile URL", "placeholder": "https://linkedin.com/in/yourname", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Position Applied For", "options": ["Frontend Developer", "Backend Developer", "Full Stack Developer", "UI/UX Designer", "Product Manager", "Data Analyst", "Other"], "required": True},
                    {"type": "select", "label": "Years of Experience", "options": ["Fresher (0 years)", "1-2 years", "3-5 years", "5-10 years", "10+ years"], "required": True},
                    {"type": "text", "label": "Current Company (if any)", "placeholder": "Leave blank if not applicable", "required": False},
                    {"type": "file", "label": "Upload Resume (PDF)", "required": True},
                    {"type": "textarea", "label": "Why do you want to join us?", "placeholder": "In 2-3 sentences...", "required": False},
                    {"type": "submit", "label": "Submit Application", "color": "#4f46e5"},
                ],
            },
            {
                "id": "appointment",
                "title": "Appointment Booking Form",
                "category": "booking",
                "description": "Let clients book appointments, consultations or slots.",
                "color": "#0891b2",
                "badge": "🔥 Popular",
                "tags": ["booking", "appointment", "schedule", "clinic"],
                "score": 77,
                "score_tip": "Add time slot picker for 90+",
                "suggestions": [
                    {"icon": "🕐", "title": "Add Preferred Time Slot", "text": "Reduces back-and-forth scheduling.", "field": {"type": "select", "label": "Preferred Time", "options": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"], "required": True}},
                    {"icon": "💬", "title": "Add Notes field", "text": "Lets clients share special requests.", "field": {"type": "textarea", "label": "Additional Notes", "placeholder": "Anything we should know?", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": False},
                    {"type": "select", "label": "Service Type", "options": ["General Consultation", "Follow-up Visit", "Specialist Appointment", "Lab / Test", "Other"], "required": True},
                    {"type": "date", "label": "Preferred Date", "required": True},
                    {"type": "radio", "label": "Mode of Appointment", "options": ["In-Person", "Video Call", "Phone Call"], "required": True},
                    {"type": "submit", "label": "Book Appointment", "color": "#0891b2"},
                ],
            },
            {
                "id": "survey",
                "title": "Customer Survey Form",
                "category": "survey",
                "description": "Run quick polls and surveys to gather audience opinions.",
                "color": "#db2777",
                "badge": None,
                "tags": ["survey", "poll", "research", "opinion"],
                "score": 70,
                "score_tip": "Add rating question to reach 88+",
                "suggestions": [
                    {"icon": "⭐", "title": "Add Star Rating", "text": "Quick rating increases response rate.", "field": {"type": "rating", "label": "Overall Satisfaction", "required": True}},
                    {"icon": "📊", "title": "Add NPS Question", "text": "Industry-standard satisfaction metric.", "field": {"type": "range", "label": "How likely are you to recommend us? (0–10)", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
                    {"type": "radio", "label": "How did you hear about us?", "options": ["Social Media", "Friend / Referral", "Google Search", "Advertisement", "Other"], "required": True},
                    {"type": "checkbox", "label": "Which features do you use?", "options": ["Forms", "Analytics", "Integrations", "Templates", "API"], "required": False},
                    {"type": "select", "label": "How often do you use our product?", "options": ["Daily", "Weekly", "Monthly", "Rarely", "First time"], "required": True},
                    {"type": "textarea", "label": "What can we improve?", "placeholder": "Your honest feedback...", "required": False},
                    {"type": "submit", "label": "Submit Survey", "color": "#db2777"},
                ],
            },
            {
                "id": "support",
                "title": "Bug Report / Support Form",
                "category": "support",
                "description": "Let users report bugs, issues or request help from support.",
                "color": "#dc2626",
                "badge": None,
                "tags": ["bug", "support", "help", "issue", "tech"],
                "score": 74,
                "score_tip": "Add screenshot upload to reach 91+",
                "suggestions": [
                    {"icon": "📸", "title": "Add Screenshot Upload", "text": "Speeds up bug resolution by 3×.", "field": {"type": "file", "label": "Attach Screenshot", "required": False}},
                    {"icon": "🔁", "title": "Add Steps to Reproduce", "text": "Critical for developers to debug.", "field": {"type": "textarea", "label": "Steps to Reproduce", "placeholder": "1. Go to...\n2. Click on...\n3. See error", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "select", "label": "Issue Type", "options": ["Bug / Error", "Feature Request", "Account Problem", "Payment Issue", "Performance", "Other"], "required": True},
                    {"type": "select", "label": "Severity", "options": ["Critical (app unusable)", "High (major feature broken)", "Medium (workaround exists)", "Low (minor inconvenience)"], "required": True},
                    {"type": "textarea", "label": "Describe the Issue", "placeholder": "What happened? What did you expect?", "required": True},
                    {"type": "text", "label": "Browser / Device", "placeholder": "e.g. Chrome 120 on Windows 11", "required": False},
                    {"type": "submit", "label": "Submit Report", "color": "#dc2626"},
                ],
            },
            {
                "id": "newsletter",
                "title": "Newsletter Signup Form",
                "category": "marketing",
                "description": "Grow your email list with a simple, conversion-optimised signup form.",
                "color": "#f59e0b",
                "badge": None,
                "tags": ["newsletter", "email", "marketing", "signup"],
                "score": 65,
                "score_tip": "Add interest tags to reach 85+",
                "suggestions": [
                    {"icon": "🏷️", "title": "Add Interest Tags", "text": "Enables personalised email campaigns.", "field": {"type": "checkbox", "label": "Interests (select all that apply)", "options": ["Product Updates", "Blog Posts", "Offers & Discounts", "Events", "Case Studies"], "required": False}},
                    {"icon": "📱", "title": "Add Phone for SMS", "text": "Multi-channel outreach boosts CTR.", "field": {"type": "phone", "label": "Mobile Number (for SMS updates)", "placeholder": "+91 98765 43210", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "First Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Last Name", "placeholder": "Last name", "required": False},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    {"type": "select", "label": "How often would you like to hear from us?", "options": ["Daily", "Weekly digest", "Monthly newsletter", "Only special offers"], "required": False},
                    {"type": "submit", "label": "Subscribe Now", "color": "#f59e0b"},
                ],
            },
        ]
        added = 0
        for t in templates:
            existing = db.query(Template).filter(Template.id == t["id"]).first()
            if existing:
                for k, v in t.items():
                    setattr(existing, k, v)
            else:
                db.add(Template(**t))
                added += 1
        db.commit()
        print(f"✅ Seeded templates: {added} new, {len(templates) - added} updated")
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
