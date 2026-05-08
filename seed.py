"""
Run this ONCE to insert all templates into PostgreSQL:
  python seed.py
"""
import sys
sys.path.append(".")
import database, models

db = database.SessionLocal()
models.Base.metadata.create_all(bind=database.engine)

TEMPLATES = [
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
            {"icon": "💳", "title": "Add UPI / Wallet field", "text": "Indian users prefer UPI. Add a payment method selector."},
            {"icon": "🎁", "title": "Add promo code field", "text": "Promo codes increase conversions by 12%."},
            {"icon": "📦", "title": "Add delivery date picker", "text": "Reduces failed deliveries by 30%."},
        ],
        "fields": [
            {"type": "section", "label": "📦 Shipping Address"},
            {"type": "row2", "fields": [
                {"type": "text", "label": "First name", "placeholder": "Rahul", "required": True},
                {"type": "text", "label": "Last name", "placeholder": "Sharma", "required": True}
            ]},
            {"type": "text", "label": "Street address", "placeholder": "123, MG Road, Jaipur", "required": True},
            {"type": "row2", "fields": [
                {"type": "text", "label": "City", "placeholder": "Jaipur", "required": True},
                {"type": "text", "label": "PIN code", "placeholder": "302001", "required": True}
            ]},
            {"type": "section", "label": "💳 Payment Details"},
            {"type": "cardicons"},
            {"type": "text", "label": "Cardholder name", "placeholder": "Rahul Sharma", "required": True},
            {"type": "cardnum"},
            {"type": "row3card"},
            {"type": "submit", "label": "Place Order — ₹2,499", "color": "#1a56db"}
        ]
    },
    {
        "id": "contact",
        "title": "Contact Us Form",
        "category": "contact",
        "description": "Clean contact form with subject, message and file upload.",
        "color": "#7c3aed",
        "badge": "",
        "tags": ["contact", "support", "inquiry"],
        "score": 70,
        "score_tip": "Add file upload & priority to improve to 90+",
        "suggestions": [
            {"icon": "⭐", "title": "Add priority selector", "text": "Mark Low / Medium / High priority."},
            {"icon": "📎", "title": "Add file attachment", "text": "Reduces back-and-forth by 40%."},
            {"icon": "🕐", "title": "Add preferred callback time", "text": "Users appreciate being called at their time."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "Your name", "placeholder": "Priya Singh", "required": True},
                {"type": "email", "label": "Email", "placeholder": "priya@email.com", "required": True}
            ]},
            {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": False},
            {"type": "select", "label": "Subject", "options": ["General Inquiry", "Technical Support", "Billing Question", "Partnership"], "required": True},
            {"type": "textarea", "label": "Message", "placeholder": "Describe your query...", "required": True},
            {"type": "file", "label": "Attachment (optional)", "required": False},
            {"type": "submit", "label": "Send Message", "color": "#7c3aed"}
        ]
    },
    {
        "id": "registration",
        "title": "Event Registration",
        "category": "registration",
        "description": "Register attendees with ticket type and dietary preferences.",
        "color": "#059669",
        "badge": "✨ New",
        "tags": ["event", "ticket", "registration"],
        "score": 65,
        "score_tip": "Add ticket qty & WhatsApp opt-in to reach 88+",
        "suggestions": [
            {"icon": "🎫", "title": "Add ticket quantity", "text": "Increases group bookings significantly."},
            {"icon": "🥗", "title": "Add dietary preference", "text": "Avoids last-minute logistics issues."},
            {"icon": "📱", "title": "Add WhatsApp opt-in", "text": "90%+ open rate vs email."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "Full name", "placeholder": "Amit Kumar", "required": True},
                {"type": "email", "label": "Email", "placeholder": "amit@email.com", "required": True}
            ]},
            {"type": "phone", "label": "Phone", "placeholder": "+91 9876543210", "required": True},
            {"type": "select", "label": "Ticket type", "options": ["General — ₹499", "VIP — ₹1,499", "Student — ₹199"], "required": True},
            {"type": "radio", "label": "Dietary preference", "options": ["Vegetarian", "Non-Vegetarian", "Vegan"], "required": False},
            {"type": "submit", "label": "Register Now", "color": "#059669"}
        ]
    },
    {
        "id": "feedback",
        "title": "Customer Feedback",
        "category": "feedback",
        "description": "NPS-style survey with star rating and open feedback.",
        "color": "#d97706",
        "badge": "",
        "tags": ["feedback", "survey", "nps"],
        "score": 72,
        "score_tip": "Add NPS & incentive to boost response rate",
        "suggestions": [
            {"icon": "📊", "title": "Add category ratings", "text": "Rate Speed, Quality, Support separately."},
            {"icon": "🎁", "title": "Add reward incentive", "text": "Increases response rate by 35%."},
        ],
        "fields": [
            {"type": "rating", "label": "Overall experience", "required": True},
            {"type": "range", "label": "How likely to recommend us? (0–10)", "required": True},
            {"type": "textarea", "label": "What did you like most?", "placeholder": "The team was...", "required": False},
            {"type": "textarea", "label": "What can we improve?", "placeholder": "It would be great if...", "required": False},
            {"type": "submit", "label": "Submit Feedback", "color": "#d97706"}
        ]
    },
    {
        "id": "job",
        "title": "Job Application Form",
        "category": "business",
        "description": "Screen candidates with experience, skills and resume upload.",
        "color": "#0f172a",
        "badge": "⚡ Pro",
        "tags": ["job", "hiring", "HR"],
        "score": 80,
        "score_tip": "Add salary expectation to reach 95+",
        "suggestions": [
            {"icon": "💰", "title": "Add salary expectation", "text": "Avoids mismatched expectations."},
            {"icon": "📅", "title": "Add notice period", "text": "Critical for hiring timeline."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "Full name", "placeholder": "Sneha Patel", "required": True},
                {"type": "email", "label": "Email", "placeholder": "sneha@email.com", "required": True}
            ]},
            {"type": "select", "label": "Position", "options": ["Frontend Developer", "Backend Developer", "Designer", "Product Manager"], "required": True},
            {"type": "select", "label": "Experience", "options": ["0–1 years", "1–3 years", "3–5 years", "5+ years"], "required": True},
            {"type": "file", "label": "Resume / CV", "required": True},
            {"type": "textarea", "label": "Cover letter", "placeholder": "Tell us why you're a great fit...", "required": False},
            {"type": "submit", "label": "Submit Application", "color": "#0f172a"}
        ]
    },
    {
        "id": "business",
        "title": "Business Enquiry",
        "category": "business",
        "description": "Qualify B2B leads with company size, budget and project details.",
        "color": "#be123c",
        "badge": "",
        "tags": ["B2B", "leads", "sales"],
        "score": 68,
        "score_tip": "Add budget & timeline to qualify leads better",
        "suggestions": [
            {"icon": "💼", "title": "Add company size", "text": "Prioritize enterprise vs SMB leads."},
            {"icon": "💸", "title": "Add budget range", "text": "Saves sales team from unqualified calls."},
        ],
        "fields": [
            {"type": "row2", "fields": [
                {"type": "text", "label": "Your name", "placeholder": "Vikram Mehta", "required": True},
                {"type": "text", "label": "Company", "placeholder": "Acme Pvt Ltd", "required": True}
            ]},
            {"type": "email", "label": "Business email", "placeholder": "vikram@acme.com", "required": True},
            {"type": "select", "label": "Budget", "options": ["Under ₹50K", "₹50K–₹2L", "₹2L–₹10L", "₹10L+"], "required": False},
            {"type": "textarea", "label": "Project details", "placeholder": "Brief us on your project...", "required": True},
            {"type": "submit", "label": "Send Enquiry", "color": "#be123c"}
        ]
    },
]

# Delete existing and re-seed
db.query(models.Template).delete()
for t in TEMPLATES:
    db.add(models.Template(**t))
db.commit()
print(f"✅ Seeded {len(TEMPLATES)} templates into PostgreSQL!")
db.close()