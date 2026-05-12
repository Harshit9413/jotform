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
from auth import models as auth_models
from auth.router import router as auth_router
from rag import models as rag_models
from rag.router import router as rag_router
from integrations import models as integration_models
from integrations.router import router as integrations_router


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
            # ── CONTACT ──────────────────────────────────────────────────
            {
                "id": "callback_request",
                "title": "Callback Request Form",
                "category": "contact",
                "description": "Let customers request a call-back at their preferred time.",
                "color": "#059669",
                "badge": None,
                "tags": ["contact", "callback", "phone"],
                "score": 74,
                "score_tip": "Add preferred language to score 88+",
                "suggestions": [
                    {"icon": "🌐", "title": "Add Preferred Language", "text": "Route calls to the right agent.", "field": {"type": "select", "label": "Preferred Language", "options": ["English", "Hindi", "Tamil", "Marathi", "Telugu"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "select", "label": "Preferred Call Time", "options": ["9 AM – 11 AM", "11 AM – 1 PM", "2 PM – 4 PM", "4 PM – 6 PM"], "required": True},
                    {"type": "textarea", "label": "What is your query about?", "placeholder": "Brief description...", "required": False},
                    {"type": "submit", "label": "Request Callback", "color": "#059669"},
                ],
            },
            {
                "id": "partnership_inquiry",
                "title": "Partnership Inquiry Form",
                "category": "contact",
                "description": "Collect partnership and collaboration requests from businesses.",
                "color": "#059669",
                "badge": "⭐ New",
                "tags": ["contact", "partnership", "b2b"],
                "score": 78,
                "score_tip": "Add company size to score 90+",
                "suggestions": [
                    {"icon": "🏢", "title": "Add Company Size", "text": "Helps qualify leads faster.", "field": {"type": "select", "label": "Company Size", "options": ["1–10", "11–50", "51–200", "200+"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Full name", "required": True},
                        {"type": "text", "label": "Company Name", "placeholder": "Acme Corp", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Business Email", "placeholder": "you@company.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": False},
                    ]},
                    {"type": "select", "label": "Partnership Type", "options": ["Reseller", "Technology Integration", "Co-Marketing", "Distribution", "Other"], "required": True},
                    {"type": "textarea", "label": "Tell us about your proposal", "placeholder": "What do you have in mind?", "required": True},
                    {"type": "submit", "label": "Submit Inquiry", "color": "#059669"},
                ],
            },
            # ── REGISTRATION ─────────────────────────────────────────────
            {
                "id": "webinar_registration",
                "title": "Webinar Registration Form",
                "category": "registration",
                "description": "Register attendees for online webinars and virtual sessions.",
                "color": "#7c3aed",
                "badge": "🔥 Popular",
                "tags": ["webinar", "online", "registration", "virtual"],
                "score": 82,
                "score_tip": "Add timezone selector to score 92+",
                "suggestions": [
                    {"icon": "🌍", "title": "Add Timezone", "text": "Prevents confusion for global attendees.", "field": {"type": "select", "label": "Your Timezone", "options": ["IST (UTC+5:30)", "EST (UTC-5)", "PST (UTC-8)", "GMT (UTC+0)", "CET (UTC+1)"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "text", "label": "Job Title", "placeholder": "e.g. Product Manager", "required": False},
                    {"type": "text", "label": "Company", "placeholder": "Your company name", "required": False},
                    {"type": "select", "label": "How did you hear about this webinar?", "options": ["Email", "LinkedIn", "Twitter", "Colleague", "Google", "Other"], "required": False},
                    {"type": "submit", "label": "Register for Webinar", "color": "#7c3aed"},
                ],
            },
            {
                "id": "course_enrollment",
                "title": "Course Enrollment Form",
                "category": "registration",
                "description": "Enroll students into courses, bootcamps, or training programs.",
                "color": "#7c3aed",
                "badge": None,
                "tags": ["course", "enrollment", "education", "training"],
                "score": 79,
                "score_tip": "Add prior experience field to score 91+",
                "suggestions": [
                    {"icon": "📚", "title": "Add Prior Experience", "text": "Helps assign students to right batch.", "field": {"type": "select", "label": "Prior Experience", "options": ["Beginner (0–1 yr)", "Intermediate (1–3 yrs)", "Advanced (3+ yrs)"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Student name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Course", "options": ["Web Development", "Data Science", "UI/UX Design", "Digital Marketing", "Python Programming", "Other"], "required": True},
                    {"type": "select", "label": "Preferred Batch", "options": ["Morning (7 AM–9 AM)", "Afternoon (12 PM–2 PM)", "Evening (7 PM–9 PM)", "Weekend only"], "required": True},
                    {"type": "radio", "label": "Mode of Learning", "options": ["Online", "Offline", "Hybrid"], "required": True},
                    {"type": "submit", "label": "Enroll Now", "color": "#7c3aed"},
                ],
            },
            # ── FEEDBACK ─────────────────────────────────────────────────
            {
                "id": "employee_satisfaction",
                "title": "Employee Satisfaction Survey",
                "category": "feedback",
                "description": "Measure employee engagement, morale and workplace satisfaction.",
                "color": "#d97706",
                "badge": None,
                "tags": ["hr", "employee", "satisfaction", "internal"],
                "score": 80,
                "score_tip": "Make survey anonymous for honest answers",
                "suggestions": [
                    {"icon": "🔒", "title": "Anonymous Mode Note", "text": "Add a note that responses are anonymous.", "field": {"type": "section", "label": "This survey is completely anonymous. Your identity will not be shared."}},
                ],
                "fields": [
                    {"type": "select", "label": "Department", "options": ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations", "Other"], "required": False},
                    {"type": "rating", "label": "How satisfied are you with your current role?", "required": True},
                    {"type": "rating", "label": "How would you rate work-life balance?", "required": True},
                    {"type": "radio", "label": "Do you feel your work is recognised?", "options": ["Always", "Often", "Sometimes", "Rarely", "Never"], "required": True},
                    {"type": "textarea", "label": "What can we do to improve your experience?", "placeholder": "Your honest feedback...", "required": False},
                    {"type": "submit", "label": "Submit Survey", "color": "#d97706"},
                ],
            },
            {
                "id": "product_review",
                "title": "Product Review Form",
                "category": "feedback",
                "description": "Collect detailed product reviews with ratings, pros and cons.",
                "color": "#d97706",
                "badge": "🔥 Popular",
                "tags": ["review", "product", "rating", "ecommerce"],
                "score": 83,
                "score_tip": "Add photo upload to reach 95+",
                "suggestions": [
                    {"icon": "📸", "title": "Add Product Photo", "text": "Photo reviews increase trust by 40%.", "field": {"type": "file", "label": "Upload Product Photo", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Product Name / Order ID", "placeholder": "e.g. Wireless Earbuds #ORD12345", "required": True},
                    {"type": "rating", "label": "Overall Rating", "required": True},
                    {"type": "checkbox", "label": "What did you like?", "options": ["Quality", "Value for money", "Fast delivery", "Packaging", "Customer service"], "required": False},
                    {"type": "textarea", "label": "Write your review", "placeholder": "Share your experience...", "required": True},
                    {"type": "radio", "label": "Would you recommend this product?", "options": ["Yes, definitely", "Maybe", "No"], "required": True},
                    {"type": "text", "label": "Your Name (optional)", "placeholder": "Displayed with review", "required": False},
                    {"type": "submit", "label": "Submit Review", "color": "#d97706"},
                ],
            },
            # ── PAYMENT ──────────────────────────────────────────────────
            {
                "id": "donation_form",
                "title": "Donation / Fundraising Form",
                "category": "payment",
                "description": "Accept donations for NGOs, causes, and fundraising campaigns.",
                "color": "#1a56db",
                "badge": None,
                "tags": ["donation", "ngo", "fundraising", "payment"],
                "score": 76,
                "score_tip": "Add tax receipt option to score 90+",
                "suggestions": [
                    {"icon": "🧾", "title": "Add Tax Receipt Option", "text": "Donors expect 80G receipts in India.", "field": {"type": "radio", "label": "Do you need a tax receipt?", "options": ["Yes, send me 80G receipt", "No, thank you"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Donor name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Donation Amount", "options": ["₹500", "₹1,000", "₹2,500", "₹5,000", "₹10,000", "Custom amount"], "required": True},
                    {"type": "radio", "label": "Payment Method", "options": ["UPI", "Net Banking", "Credit / Debit Card", "Cheque"], "required": True},
                    {"type": "textarea", "label": "Message (optional)", "placeholder": "A note with your donation...", "required": False},
                    {"type": "submit", "label": "Donate Now", "color": "#1a56db"},
                ],
            },
            {
                "id": "invoice_request",
                "title": "Invoice / Quote Request Form",
                "category": "payment",
                "description": "Let clients request a quote or invoice for your services.",
                "color": "#1a56db",
                "badge": None,
                "tags": ["invoice", "quote", "b2b", "billing"],
                "score": 73,
                "score_tip": "Add GST number field for B2B to score 88+",
                "suggestions": [
                    {"icon": "🧾", "title": "Add GST Number", "text": "Required for B2B invoicing in India.", "field": {"type": "text", "label": "GST Number", "placeholder": "22AAAAA0000A1Z5", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Company / Client Name", "placeholder": "Acme Pvt Ltd", "required": True},
                        {"type": "email", "label": "Billing Email", "placeholder": "billing@company.com", "required": True},
                    ]},
                    {"type": "text", "label": "Service / Product Required", "placeholder": "e.g. Website Design Package", "required": True},
                    {"type": "number", "label": "Quantity", "placeholder": "1", "required": False},
                    {"type": "textarea", "label": "Additional Requirements", "placeholder": "Any specific details...", "required": False},
                    {"type": "text", "label": "Billing Address", "placeholder": "Full address with PIN", "required": True},
                    {"type": "submit", "label": "Request Invoice", "color": "#1a56db"},
                ],
            },
            # ── HR ───────────────────────────────────────────────────────
            {
                "id": "leave_request",
                "title": "Leave Request Form",
                "category": "hr",
                "description": "Simple employee leave application form for HR approval.",
                "color": "#4f46e5",
                "badge": None,
                "tags": ["hr", "leave", "internal", "employee"],
                "score": 77,
                "score_tip": "Add team lead approval step to score 89+",
                "suggestions": [
                    {"icon": "👤", "title": "Add Manager Name", "text": "Routes leave to the right approver.", "field": {"type": "text", "label": "Reporting Manager", "placeholder": "Manager full name", "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name", "placeholder": "Your full name", "required": True},
                        {"type": "text", "label": "Employee ID", "placeholder": "EMP001", "required": True},
                    ]},
                    {"type": "select", "label": "Leave Type", "options": ["Casual Leave", "Sick Leave", "Earned Leave", "Maternity / Paternity", "Unpaid Leave", "Other"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "From Date", "required": True},
                        {"type": "date", "label": "To Date", "required": True},
                    ]},
                    {"type": "textarea", "label": "Reason for Leave", "placeholder": "Brief reason...", "required": True},
                    {"type": "text", "label": "Contact During Leave", "placeholder": "Phone or email", "required": False},
                    {"type": "submit", "label": "Submit Leave Request", "color": "#4f46e5"},
                ],
            },
            {
                "id": "employee_onboarding",
                "title": "Employee Onboarding Form",
                "category": "hr",
                "description": "Collect new employee details during the onboarding process.",
                "color": "#4f46e5",
                "badge": "⭐ New",
                "tags": ["hr", "onboarding", "new hire", "joining"],
                "score": 85,
                "score_tip": "Add emergency contact to score 95+",
                "suggestions": [
                    {"icon": "🚨", "title": "Add Emergency Contact", "text": "Required for employee safety records.", "field": {"type": "row2", "fields": [{"type": "text", "label": "Emergency Contact Name", "placeholder": "Contact name", "required": True}, {"type": "phone", "label": "Emergency Phone", "placeholder": "+91 98765 43210", "required": True}]}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "As per Aadhaar", "required": True},
                        {"type": "date", "label": "Date of Joining", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Personal Email", "placeholder": "you@gmail.com", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Current Address", "placeholder": "Full address with PIN", "required": True},
                    {"type": "text", "label": "Aadhaar Number", "placeholder": "XXXX XXXX XXXX", "required": True},
                    {"type": "text", "label": "PAN Number", "placeholder": "ABCDE1234F", "required": True},
                    {"type": "text", "label": "Bank Account Number", "placeholder": "For salary transfer", "required": True},
                    {"type": "file", "label": "Upload Aadhaar Card", "required": True},
                    {"type": "submit", "label": "Submit Onboarding Form", "color": "#4f46e5"},
                ],
            },
            # ── BOOKING ──────────────────────────────────────────────────
            {
                "id": "hotel_booking",
                "title": "Hotel Room Booking Form",
                "category": "booking",
                "description": "Accept room reservation requests with check-in / check-out details.",
                "color": "#0891b2",
                "badge": "🔥 Popular",
                "tags": ["hotel", "booking", "room", "travel"],
                "score": 80,
                "score_tip": "Add meal preference to score 91+",
                "suggestions": [
                    {"icon": "🍽️", "title": "Add Meal Preference", "text": "Helps kitchen plan in advance.", "field": {"type": "radio", "label": "Meal Plan", "options": ["Room Only", "Breakfast Included", "Half Board", "Full Board"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Guest Name", "placeholder": "Full name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Room Type", "options": ["Standard Room", "Deluxe Room", "Suite", "Family Room", "Executive Room"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Check-In Date", "required": True},
                        {"type": "date", "label": "Check-Out Date", "required": True},
                    ]},
                    {"type": "number", "label": "Number of Guests", "placeholder": "2", "required": True},
                    {"type": "textarea", "label": "Special Requests", "placeholder": "High floor, early check-in, etc.", "required": False},
                    {"type": "submit", "label": "Book Now", "color": "#0891b2"},
                ],
            },
            {
                "id": "restaurant_reservation",
                "title": "Restaurant Table Reservation",
                "category": "booking",
                "description": "Let diners book tables with date, time, and party size.",
                "color": "#0891b2",
                "badge": None,
                "tags": ["restaurant", "reservation", "dining", "table"],
                "score": 75,
                "score_tip": "Add occasion field to score 88+",
                "suggestions": [
                    {"icon": "🎂", "title": "Add Occasion", "text": "Lets staff arrange surprise decor.", "field": {"type": "select", "label": "Occasion", "options": ["Birthday", "Anniversary", "Business Dinner", "Date Night", "Just Dining", "Other"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Name", "placeholder": "Reservation name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Date", "required": True},
                        {"type": "select", "label": "Time Slot", "options": ["12:00 PM", "1:00 PM", "2:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"], "required": True},
                    ]},
                    {"type": "select", "label": "Party Size", "options": ["1–2", "3–4", "5–6", "7–10", "10+"], "required": True},
                    {"type": "radio", "label": "Seating Preference", "options": ["Indoor", "Outdoor / Terrace", "Private Dining", "No Preference"], "required": False},
                    {"type": "submit", "label": "Reserve Table", "color": "#0891b2"},
                ],
            },
            # ── SURVEY ───────────────────────────────────────────────────
            {
                "id": "nps_survey",
                "title": "Net Promoter Score (NPS) Survey",
                "category": "survey",
                "description": "Measure customer loyalty with the industry-standard NPS framework.",
                "color": "#db2777",
                "badge": "🔥 Popular",
                "tags": ["nps", "survey", "loyalty", "customer"],
                "score": 88,
                "score_tip": "Add follow-up question for detractors to score 96+",
                "suggestions": [
                    {"icon": "📞", "title": "Add Detractor Follow-up", "text": "Reach out to unhappy customers.", "field": {"type": "radio", "label": "May we contact you to resolve your concerns?", "options": ["Yes, please contact me", "No, thank you"], "required": False}},
                ],
                "fields": [
                    {"type": "range", "label": "How likely are you to recommend us to a friend or colleague? (0 = Not at all, 10 = Extremely likely)", "required": True},
                    {"type": "select", "label": "Which product/service are you rating?", "options": ["Core Product", "Customer Support", "Mobile App", "Website", "Overall Experience"], "required": True},
                    {"type": "textarea", "label": "What is the main reason for your score?", "placeholder": "Your honest feedback helps us improve...", "required": False},
                    {"type": "text", "label": "Name (optional)", "placeholder": "Your name", "required": False},
                    {"type": "submit", "label": "Submit Feedback", "color": "#db2777"},
                ],
            },
            {
                "id": "market_research",
                "title": "Market Research Survey",
                "category": "survey",
                "description": "Understand your target market with demographic and preference questions.",
                "color": "#db2777",
                "badge": None,
                "tags": ["market", "research", "demographics", "survey"],
                "score": 72,
                "score_tip": "Add income bracket question to score 85+",
                "suggestions": [
                    {"icon": "💰", "title": "Add Income Bracket", "text": "Key for pricing and segmentation.", "field": {"type": "select", "label": "Monthly Household Income", "options": ["Below ₹25,000", "₹25,000–₹50,000", "₹50,000–₹1,00,000", "Above ₹1,00,000", "Prefer not to say"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Age Group", "options": ["Under 18", "18–24", "25–34", "35–44", "45–54", "55+"], "required": True},
                        {"type": "radio", "label": "Gender", "options": ["Male", "Female", "Non-binary", "Prefer not to say"], "required": False},
                    ]},
                    {"type": "select", "label": "Location (City Tier)", "options": ["Metro (Mumbai, Delhi, Bangalore...)", "Tier-2 (Pune, Jaipur, Lucknow...)", "Tier-3 / Rural"], "required": False},
                    {"type": "select", "label": "Highest Education", "options": ["High School", "Diploma", "Graduate", "Post-Graduate", "Doctorate"], "required": False},
                    {"type": "checkbox", "label": "Which categories do you shop online?", "options": ["Electronics", "Fashion", "Groceries", "Beauty", "Books", "Sports", "Home Decor"], "required": False},
                    {"type": "radio", "label": "How often do you make online purchases?", "options": ["Daily", "Weekly", "Monthly", "Rarely"], "required": True},
                    {"type": "submit", "label": "Submit Survey", "color": "#db2777"},
                ],
            },
            # ── SUPPORT ──────────────────────────────────────────────────
            {
                "id": "it_helpdesk",
                "title": "IT Help Desk Ticket",
                "category": "support",
                "description": "Internal IT support ticket for hardware, software, and access issues.",
                "color": "#dc2626",
                "badge": None,
                "tags": ["it", "helpdesk", "support", "internal", "tech"],
                "score": 79,
                "score_tip": "Add asset tag field to score 91+",
                "suggestions": [
                    {"icon": "🏷️", "title": "Add Asset Tag", "text": "Links ticket to company equipment.", "field": {"type": "text", "label": "Asset / Device Tag", "placeholder": "e.g. LAPTOP-042", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Employee ID", "placeholder": "EMP001", "required": True},
                    ]},
                    {"type": "email", "label": "Work Email", "placeholder": "you@company.com", "required": True},
                    {"type": "select", "label": "Issue Category", "options": ["Hardware Problem", "Software / App Issue", "Network / VPN", "Email / Calendar", "Access / Password", "Printer / Scanner", "Other"], "required": True},
                    {"type": "select", "label": "Priority", "options": ["Critical – I cannot work", "High – Major disruption", "Medium – Workaround available", "Low – Minor inconvenience"], "required": True},
                    {"type": "textarea", "label": "Describe the Issue", "placeholder": "What happened? Steps to reproduce?", "required": True},
                    {"type": "submit", "label": "Raise Ticket", "color": "#dc2626"},
                ],
            },
            {
                "id": "refund_request",
                "title": "Return & Refund Request",
                "category": "support",
                "description": "Process customer return and refund requests with all necessary details.",
                "color": "#dc2626",
                "badge": None,
                "tags": ["refund", "return", "support", "ecommerce"],
                "score": 76,
                "score_tip": "Add bank details for faster refund to score 89+",
                "suggestions": [
                    {"icon": "🏦", "title": "Add Bank Details", "text": "Speeds up direct refund transfers.", "field": {"type": "text", "label": "Bank Account Number (for refund)", "placeholder": "Account number", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "text", "label": "Order ID", "placeholder": "e.g. ORD-20241201-XYZ", "required": True},
                    {"type": "select", "label": "Reason for Return", "options": ["Wrong item received", "Damaged / Defective", "Not as described", "Changed my mind", "Better price elsewhere", "Other"], "required": True},
                    {"type": "radio", "label": "Resolution Preferred", "options": ["Full Refund", "Exchange / Replacement", "Store Credit"], "required": True},
                    {"type": "file", "label": "Upload Photo of Product", "required": False},
                    {"type": "textarea", "label": "Additional Comments", "placeholder": "Any other details...", "required": False},
                    {"type": "submit", "label": "Submit Request", "color": "#dc2626"},
                ],
            },
            # ── MARKETING ────────────────────────────────────────────────
            {
                "id": "lead_generation",
                "title": "Lead Generation Form",
                "category": "marketing",
                "description": "Capture high-quality sales leads with qualification questions.",
                "color": "#f59e0b",
                "badge": "🔥 Popular",
                "tags": ["lead", "sales", "marketing", "crm"],
                "score": 84,
                "score_tip": "Add budget qualifier to score 95+",
                "suggestions": [
                    {"icon": "💰", "title": "Add Budget Range", "text": "Qualifies leads before sales call.", "field": {"type": "select", "label": "Budget Range", "options": ["Under ₹50,000", "₹50,000–₹2,00,000", "₹2,00,000–₹5,00,000", "₹5,00,000+", "Not decided yet"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Company", "placeholder": "Company name", "required": False},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Business Email", "placeholder": "you@company.com", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "select", "label": "What are you interested in?", "options": ["Product Demo", "Pricing Information", "Partnership", "Custom Solution", "Just Exploring"], "required": True},
                    {"type": "select", "label": "Timeline", "options": ["Immediate (this week)", "1–4 weeks", "1–3 months", "3+ months", "Just researching"], "required": False},
                    {"type": "textarea", "label": "Tell us about your requirement", "placeholder": "Brief description...", "required": False},
                    {"type": "submit", "label": "Get in Touch", "color": "#f59e0b"},
                ],
            },
            {
                "id": "event_rsvp",
                "title": "Event RSVP Form",
                "category": "marketing",
                "description": "Collect RSVPs for product launches, meetups, and corporate events.",
                "color": "#f59e0b",
                "badge": "⭐ New",
                "tags": ["event", "rsvp", "marketing", "launch"],
                "score": 78,
                "score_tip": "Add T-shirt size for merchandise to score 88+",
                "suggestions": [
                    {"icon": "👕", "title": "Add T-shirt Size", "text": "Useful for events giving branded merch.", "field": {"type": "select", "label": "T-Shirt Size", "options": ["XS", "S", "M", "L", "XL", "XXL"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "text", "label": "Company / Organisation", "placeholder": "Optional", "required": False},
                    {"type": "radio", "label": "Will you attend?", "options": ["Yes, I will attend", "Maybe", "No, I cannot attend"], "required": True},
                    {"type": "number", "label": "Number of guests (including yourself)", "placeholder": "1", "required": False},
                    {"type": "select", "label": "How did you hear about this event?", "options": ["Email Invite", "Social Media", "Colleague / Friend", "Company Website", "Other"], "required": False},
                    {"type": "submit", "label": "Confirm RSVP", "color": "#f59e0b"},
                ],
            },

            # ── CONTACT ──────────────────────────────────────────────────────
            {
                "id": "complaint_form",
                "title": "Customer Complaint Form",
                "category": "contact",
                "description": "Let customers report issues and complaints with full details for faster resolution.",
                "color": "#dc2626",
                "badge": "🔥 Popular",
                "tags": ["complaint", "grievance", "contact", "support"],
                "score": 82,
                "score_tip": "Add priority level field to reach 90+",
                "suggestions": [
                    {"icon": "🚨", "title": "Add Priority Level", "text": "Helps your team triage complaints faster.", "field": {"type": "select", "label": "Priority Level", "options": ["Low", "Medium", "High", "Critical"], "required": False}},
                    {"icon": "📎", "title": "Add File Attachment", "text": "Let customers attach screenshots or invoices.", "field": {"type": "file", "label": "Attach Evidence (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Complaint Category", "options": ["Product Quality", "Delivery / Shipping", "Billing & Payment", "Customer Service", "Website / App Issue", "Other"], "required": True},
                    {"type": "text", "label": "Order / Reference Number", "placeholder": "e.g. ORD-12345", "required": False},
                    {"type": "textarea", "label": "Describe Your Complaint", "placeholder": "Please describe the issue in detail...", "required": True},
                    {"type": "radio", "label": "How would you like us to resolve this?", "options": ["Refund", "Replacement", "Apology & Correction", "Other"], "required": False},
                    {"type": "file", "label": "Attach Supporting Document (optional)", "required": False},
                    {"type": "submit", "label": "Submit Complaint", "color": "#dc2626"},
                ],
            },
            {
                "id": "vendor_inquiry",
                "title": "Vendor / Supplier Inquiry",
                "category": "contact",
                "description": "Screen potential vendors and suppliers before onboarding them to your business.",
                "color": "#0891b2",
                "badge": None,
                "tags": ["vendor", "supplier", "b2b", "contact", "procurement"],
                "score": 76,
                "score_tip": "Add product catalogue upload for 86+",
                "suggestions": [
                    {"icon": "📋", "title": "Add GST / Tax ID", "text": "Required for vendor verification in India.", "field": {"type": "text", "label": "GST Number", "placeholder": "22AAAAA0000A1Z5", "required": False}},
                    {"icon": "🌍", "title": "Add Service Region", "text": "Know where the vendor can deliver.", "field": {"type": "select", "label": "Service Region", "options": ["Pan India", "North India", "South India", "East India", "West India", "International"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Contact Person Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Company Name", "placeholder": "Business name", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Business Email", "placeholder": "vendor@company.com", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "select", "label": "Product / Service Category", "options": ["Raw Materials", "IT & Software", "Logistics & Shipping", "Marketing & Printing", "Office Supplies", "Manufacturing", "Consulting", "Other"], "required": True},
                    {"type": "textarea", "label": "Describe Your Products / Services", "placeholder": "What do you offer and at what scale?", "required": True},
                    {"type": "text", "label": "Website URL", "placeholder": "https://yourcompany.com", "required": False},
                    {"type": "select", "label": "Minimum Order Value", "options": ["Under ₹10,000", "₹10,000 – ₹50,000", "₹50,000 – ₹2,00,000", "Above ₹2,00,000"], "required": False},
                    {"type": "submit", "label": "Send Inquiry", "color": "#0891b2"},
                ],
            },

            # ── REGISTRATION ─────────────────────────────────────────────────
            {
                "id": "conference_registration",
                "title": "Conference / Summit Registration",
                "category": "registration",
                "description": "Register delegates for conferences, industry summits, and annual conventions.",
                "color": "#7c3aed",
                "badge": "⭐ New",
                "tags": ["conference", "summit", "delegate", "registration"],
                "score": 85,
                "score_tip": "Add session preferences to personalise schedule",
                "suggestions": [
                    {"icon": "🎤", "title": "Add Session Preferences", "text": "Let delegates pick tracks/sessions.", "field": {"type": "checkbox", "label": "Which sessions will you attend?", "options": ["Keynote", "Workshop A", "Workshop B", "Panel Discussion", "Networking Lunch"], "required": False}},
                    {"icon": "🎫", "title": "Add Ticket Type", "text": "Differentiate Early Bird vs Standard.", "field": {"type": "radio", "label": "Ticket Type", "options": ["Early Bird (₹1,999)", "Standard (₹2,999)", "VIP (₹5,999)"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Delegate full name", "required": True},
                        {"type": "text", "label": "Job Title", "placeholder": "e.g. Product Manager", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Work Email", "placeholder": "you@company.com", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Company / Organisation", "placeholder": "Your organisation", "required": True},
                    {"type": "select", "label": "Industry", "options": ["Technology", "Finance & Banking", "Healthcare", "Education", "Retail & E-commerce", "Manufacturing", "Media & Entertainment", "Other"], "required": True},
                    {"type": "radio", "label": "Attendance Mode", "options": ["In-Person", "Online / Virtual"], "required": True},
                    {"type": "textarea", "label": "Any special requirements or questions?", "placeholder": "Dietary needs, accessibility, etc.", "required": False},
                    {"type": "submit", "label": "Register Now", "color": "#7c3aed"},
                ],
            },
            {
                "id": "club_membership",
                "title": "Club / Society Membership Form",
                "category": "registration",
                "description": "Onboard new members for sports clubs, alumni associations, or hobby societies.",
                "color": "#059669",
                "badge": None,
                "tags": ["membership", "club", "society", "alumni", "registration"],
                "score": 74,
                "score_tip": "Add referral field for member-brings-member drives",
                "suggestions": [
                    {"icon": "👥", "title": "Add Referral Field", "text": "Track who referred the new member.", "field": {"type": "text", "label": "Referred by (existing member name)", "placeholder": "Optional", "required": False}},
                    {"icon": "📸", "title": "Add Photo Upload", "text": "Collect member photos for ID cards.", "field": {"type": "file", "label": "Upload Profile Photo", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "First Name", "placeholder": "First name", "required": True},
                        {"type": "text", "label": "Last Name", "placeholder": "Last name", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "date", "label": "Date of Birth", "placeholder": "", "required": True},
                    {"type": "select", "label": "Membership Plan", "options": ["Monthly – ₹499", "Quarterly – ₹1,299", "Annual – ₹4,499", "Lifetime – ₹14,999"], "required": True},
                    {"type": "checkbox", "label": "Areas of Interest", "options": ["Sports & Fitness", "Arts & Culture", "Technology", "Community Service", "Networking", "Education"], "required": False},
                    {"type": "textarea", "label": "Tell us about yourself", "placeholder": "Brief introduction...", "required": False},
                    {"type": "submit", "label": "Apply for Membership", "color": "#059669"},
                ],
            },

            # ── FEEDBACK ─────────────────────────────────────────────────────
            {
                "id": "customer_service_feedback",
                "title": "Customer Service Feedback",
                "category": "feedback",
                "description": "Measure satisfaction with your support team after each customer interaction.",
                "color": "#f59e0b",
                "badge": "🔥 Popular",
                "tags": ["customer service", "support rating", "feedback", "csat"],
                "score": 88,
                "score_tip": "Perfect score! Add open comments for richer insights",
                "suggestions": [
                    {"icon": "💬", "title": "Add Agent Name field", "text": "Link feedback to specific support agents.", "field": {"type": "text", "label": "Agent Name (if known)", "placeholder": "Optional", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
                        {"type": "text", "label": "Ticket / Case Number", "placeholder": "e.g. TKT-00123", "required": False},
                    ]},
                    {"type": "rating", "label": "Overall satisfaction with the support you received", "required": True},
                    {"type": "radio", "label": "Was your issue fully resolved?", "options": ["Yes, completely", "Partially resolved", "No, still open"], "required": True},
                    {"type": "rating", "label": "How easy was it to get help?", "required": True},
                    {"type": "radio", "label": "How long did it take to resolve?", "options": ["Under 1 hour", "1–4 hours", "Same day", "2–3 days", "More than 3 days"], "required": False},
                    {"type": "textarea", "label": "Any comments about the support experience?", "placeholder": "What went well? What could be improved?", "required": False},
                    {"type": "submit", "label": "Submit Feedback", "color": "#f59e0b"},
                ],
            },
            {
                "id": "event_feedback",
                "title": "Post-Event Feedback Form",
                "category": "feedback",
                "description": "Gather attendee feedback right after an event to improve future editions.",
                "color": "#6c63ff",
                "badge": None,
                "tags": ["event", "post-event", "conference feedback", "webinar feedback"],
                "score": 80,
                "score_tip": "Add Net Promoter Score question to reach 90+",
                "suggestions": [
                    {"icon": "📣", "title": "Add NPS Question", "text": "Would you recommend this event? (0–10 scale)", "field": {"type": "range", "label": "How likely are you to recommend this event? (0 = Not at all, 10 = Definitely)", "required": True}},
                    {"icon": "📸", "title": "Add Photo Upload", "text": "Let attendees share event photos.", "field": {"type": "file", "label": "Share an event photo (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Optional", "required": False},
                        {"type": "email", "label": "Email Address", "placeholder": "Optional", "required": False},
                    ]},
                    {"type": "rating", "label": "Overall event experience", "required": True},
                    {"type": "rating", "label": "Quality of speakers / content", "required": True},
                    {"type": "rating", "label": "Venue / platform experience", "required": True},
                    {"type": "rating", "label": "Networking opportunities", "required": True},
                    {"type": "checkbox", "label": "What did you enjoy most?", "options": ["Keynote Sessions", "Workshops", "Panel Discussions", "Networking", "Exhibition / Stalls", "Food & Hospitality"], "required": False},
                    {"type": "textarea", "label": "What could we improve for next time?", "placeholder": "Your suggestions...", "required": False},
                    {"type": "submit", "label": "Submit Feedback", "color": "#6c63ff"},
                ],
            },

            # ── PAYMENT ──────────────────────────────────────────────────────
            {
                "id": "subscription_form",
                "title": "Subscription Sign-Up Form",
                "category": "payment",
                "description": "Sign up customers for monthly or annual subscription plans with billing details.",
                "color": "#0891b2",
                "badge": "⭐ New",
                "tags": ["subscription", "saas", "recurring", "payment", "plan"],
                "score": 79,
                "score_tip": "Add coupon code field for promo campaigns",
                "suggestions": [
                    {"icon": "🎟️", "title": "Add Coupon Code", "text": "Let users apply discount codes.", "field": {"type": "text", "label": "Promo / Coupon Code", "placeholder": "Optional", "required": False}},
                    {"icon": "🔄", "title": "Add Billing Cycle", "text": "Monthly vs annual toggle increases LTV.", "field": {"type": "radio", "label": "Billing Cycle", "options": ["Monthly", "Annual (Save 20%)"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Account holder name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Select Plan", "options": ["Starter – ₹499/mo", "Professional – ₹999/mo", "Business – ₹2,499/mo", "Enterprise – Custom pricing"], "required": True},
                    {"type": "radio", "label": "Billing Cycle", "options": ["Monthly", "Annual (save 20%)"], "required": True},
                    {"type": "text", "label": "Company Name", "placeholder": "For invoicing (optional)", "required": False},
                    {"type": "text", "label": "GST Number", "placeholder": "For business invoices (optional)", "required": False},
                    {"type": "textarea", "label": "Any specific requirements?", "placeholder": "Custom needs, onboarding notes...", "required": False},
                    {"type": "submit", "label": "Start Subscription", "color": "#0891b2"},
                ],
            },
            {
                "id": "expense_claim",
                "title": "Employee Expense Claim Form",
                "category": "payment",
                "description": "Let employees submit reimbursement requests with receipts for quick finance approval.",
                "color": "#b45309",
                "badge": None,
                "tags": ["expense", "reimbursement", "hr", "finance", "payment"],
                "score": 84,
                "score_tip": "Add manager approval field for automated workflow",
                "suggestions": [
                    {"icon": "✅", "title": "Add Manager Name", "text": "Route claim to the correct approver.", "field": {"type": "text", "label": "Reporting Manager Name", "placeholder": "Your manager", "required": False}},
                    {"icon": "📎", "title": "Add Receipt Upload", "text": "Attach bills or receipts for verification.", "field": {"type": "file", "label": "Upload Receipts", "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name", "placeholder": "Full name", "required": True},
                        {"type": "text", "label": "Employee ID", "placeholder": "e.g. EMP-1042", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Department", "placeholder": "e.g. Sales", "required": True},
                        {"type": "date", "label": "Expense Date", "placeholder": "", "required": True},
                    ]},
                    {"type": "select", "label": "Expense Category", "options": ["Travel & Conveyance", "Meals & Entertainment", "Office Supplies", "Client Gifts", "Training & Conferences", "Internet & Phone Bills", "Other"], "required": True},
                    {"type": "number", "label": "Total Amount Claimed (₹)", "placeholder": "0.00", "required": True},
                    {"type": "textarea", "label": "Purpose / Description", "placeholder": "Describe the expense and business justification", "required": True},
                    {"type": "file", "label": "Upload Receipts / Bills", "required": False},
                    {"type": "submit", "label": "Submit Claim", "color": "#b45309"},
                ],
            },

            # ── HR / JOBS ─────────────────────────────────────────────────────
            {
                "id": "performance_review",
                "title": "Employee Performance Review",
                "category": "hr",
                "description": "Annual self-assessment form for employees to reflect on goals and achievements.",
                "color": "#7c3aed",
                "badge": None,
                "tags": ["performance", "appraisal", "hr", "self-assessment", "review"],
                "score": 87,
                "score_tip": "Add peer feedback section to reach 95+",
                "suggestions": [
                    {"icon": "🤝", "title": "Add Peer Feedback", "text": "360-degree reviews improve accuracy.", "field": {"type": "textarea", "label": "Peer Feedback (if applicable)", "placeholder": "What do colleagues say about your work?", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name", "placeholder": "Full name", "required": True},
                        {"type": "text", "label": "Employee ID", "placeholder": "e.g. EMP-1042", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Department", "placeholder": "e.g. Engineering", "required": True},
                        {"type": "text", "label": "Review Period", "placeholder": "e.g. Jan–Dec 2024", "required": True},
                    ]},
                    {"type": "textarea", "label": "Key Achievements this year", "placeholder": "List your top 3–5 accomplishments...", "required": True},
                    {"type": "textarea", "label": "Goals set vs Goals achieved", "placeholder": "How did you perform against targets?", "required": True},
                    {"type": "rating", "label": "Self-rating on overall performance", "required": True},
                    {"type": "textarea", "label": "Areas for Improvement", "placeholder": "What skills or behaviours do you want to develop?", "required": True},
                    {"type": "textarea", "label": "Goals for next year", "placeholder": "3 key goals for the upcoming period...", "required": True},
                    {"type": "submit", "label": "Submit Self-Review", "color": "#7c3aed"},
                ],
            },
            {
                "id": "exit_interview",
                "title": "Employee Exit Interview",
                "category": "hr",
                "description": "Understand why employees leave and capture insights to improve retention.",
                "color": "#dc2626",
                "badge": None,
                "tags": ["exit", "offboarding", "hr", "attrition", "resignation"],
                "score": 83,
                "score_tip": "Make all fields optional to increase completion rate",
                "suggestions": [
                    {"icon": "🔒", "title": "Add Anonymous Option", "text": "Anonymity increases honest responses.", "field": {"type": "radio", "label": "Submit this form", "options": ["With my name", "Anonymously"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name (optional)", "placeholder": "You may leave blank", "required": False},
                        {"type": "text", "label": "Department", "placeholder": "e.g. Marketing", "required": False},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Job Title", "placeholder": "Your role", "required": False},
                        {"type": "date", "label": "Last Working Day", "placeholder": "", "required": False},
                    ]},
                    {"type": "select", "label": "Primary reason for leaving", "options": ["Better opportunity elsewhere", "Compensation & Benefits", "Work-life balance", "Lack of growth", "Team / Management issues", "Relocation", "Personal reasons", "Other"], "required": True},
                    {"type": "rating", "label": "Overall satisfaction with the company", "required": True},
                    {"type": "textarea", "label": "What did you like most about working here?", "placeholder": "Culture, team, projects...", "required": False},
                    {"type": "textarea", "label": "What would you change?", "placeholder": "Honest feedback helps us improve...", "required": False},
                    {"type": "radio", "label": "Would you recommend this company to others?", "options": ["Yes, definitely", "Maybe", "No"], "required": True},
                    {"type": "submit", "label": "Submit Exit Interview", "color": "#dc2626"},
                ],
            },

            # ── BOOKING ──────────────────────────────────────────────────────
            {
                "id": "car_rental",
                "title": "Car Rental Booking Form",
                "category": "booking",
                "description": "Accept online car rental requests with pickup, drop-off, and vehicle preferences.",
                "color": "#1d4ed8",
                "badge": None,
                "tags": ["car rental", "vehicle", "booking", "transport", "self-drive"],
                "score": 81,
                "score_tip": "Add driver's licence upload to auto-verify eligibility",
                "suggestions": [
                    {"icon": "🪪", "title": "Add Licence Upload", "text": "Collect driving licence for verification.", "field": {"type": "file", "label": "Upload Driving Licence", "required": False}},
                    {"icon": "🛡️", "title": "Add Insurance Option", "text": "Offer optional insurance add-on.", "field": {"type": "radio", "label": "Add Rental Insurance?", "options": ["Yes – ₹299/day", "No thanks"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Driver's full name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Vehicle Type", "options": ["Hatchback", "Sedan", "SUV", "Luxury / Premium", "Electric Vehicle", "Mini Bus / Van"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Pickup Date", "placeholder": "", "required": True},
                        {"type": "date", "label": "Return Date", "placeholder": "", "required": True},
                    ]},
                    {"type": "text", "label": "Pickup Location", "placeholder": "City or address", "required": True},
                    {"type": "text", "label": "Drop-off Location", "placeholder": "Same or different location", "required": False},
                    {"type": "select", "label": "Fuel Preference", "options": ["Petrol", "Diesel", "CNG", "Electric", "No preference"], "required": False},
                    {"type": "submit", "label": "Request Booking", "color": "#1d4ed8"},
                ],
            },
            {
                "id": "salon_appointment",
                "title": "Salon / Spa Appointment",
                "category": "booking",
                "description": "Let clients book beauty and wellness appointments with service and stylist selection.",
                "color": "#db2777",
                "badge": "⭐ New",
                "tags": ["salon", "spa", "beauty", "appointment", "booking"],
                "score": 77,
                "score_tip": "Add preferred stylist field to personalise experience",
                "suggestions": [
                    {"icon": "💆", "title": "Add Preferred Stylist", "text": "Clients who book a stylist return more often.", "field": {"type": "text", "label": "Preferred Stylist (if any)", "placeholder": "Optional", "required": False}},
                    {"icon": "🎂", "title": "Add Birthday Field", "text": "Send birthday offers to loyal clients.", "field": {"type": "date", "label": "Date of Birth (for birthday offers)", "placeholder": "", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Client Name", "placeholder": "Your name", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "For booking confirmation", "required": False},
                    {"type": "checkbox", "label": "Services Required", "options": ["Haircut & Styling", "Hair Colour / Highlights", "Facial & Cleanup", "Manicure & Pedicure", "Threading & Waxing", "Massage / Body Treatment", "Bridal Makeup", "Other"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Preferred Date", "placeholder": "", "required": True},
                        {"type": "select", "label": "Preferred Time Slot", "options": ["10:00 AM", "11:00 AM", "12:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"], "required": True},
                    ]},
                    {"type": "textarea", "label": "Special Requests or Allergies", "placeholder": "Any preferences or skin/hair concerns?", "required": False},
                    {"type": "submit", "label": "Book Appointment", "color": "#db2777"},
                ],
            },

            # ── SURVEY ───────────────────────────────────────────────────────
            {
                "id": "employee_pulse",
                "title": "Employee Pulse Survey",
                "category": "survey",
                "description": "Quick weekly check-in to monitor team morale, workload, and engagement levels.",
                "color": "#059669",
                "badge": "🔥 Popular",
                "tags": ["pulse", "engagement", "morale", "hr", "survey", "weekly"],
                "score": 90,
                "score_tip": "Outstanding form! Keep it short for high response rates",
                "suggestions": [
                    {"icon": "📅", "title": "Add Week Number", "text": "Track pulse trends week over week.", "field": {"type": "text", "label": "Week / Period", "placeholder": "e.g. Week 22, May 2025", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Name (optional — can be anonymous)", "placeholder": "Leave blank to stay anonymous", "required": False},
                    {"type": "text", "label": "Team / Department", "placeholder": "e.g. Engineering", "required": False},
                    {"type": "rating", "label": "How happy are you at work this week?", "required": True},
                    {"type": "rating", "label": "How manageable is your workload?", "required": True},
                    {"type": "rating", "label": "How supported do you feel by your manager?", "required": True},
                    {"type": "radio", "label": "Did you face any blockers this week?", "options": ["No blockers", "Minor ones", "Significant blockers"], "required": True},
                    {"type": "textarea", "label": "Anything on your mind? (optional)", "placeholder": "Share wins, concerns, or suggestions...", "required": False},
                    {"type": "submit", "label": "Submit Pulse Check", "color": "#059669"},
                ],
            },
            {
                "id": "customer_satisfaction",
                "title": "Post-Purchase Satisfaction Survey",
                "category": "survey",
                "description": "Measure customer delight right after a purchase to spot issues and improve loyalty.",
                "color": "#f59e0b",
                "badge": None,
                "tags": ["csat", "post-purchase", "satisfaction", "ecommerce", "survey"],
                "score": 86,
                "score_tip": "Add product photo upload for richer UGC feedback",
                "suggestions": [
                    {"icon": "📸", "title": "Add Product Photo", "text": "User photos double as social proof.", "field": {"type": "file", "label": "Share a photo of your purchase (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
                        {"type": "text", "label": "Order Number", "placeholder": "e.g. ORD-98765", "required": False},
                    ]},
                    {"type": "rating", "label": "Overall satisfaction with your purchase", "required": True},
                    {"type": "rating", "label": "Product quality rating", "required": True},
                    {"type": "rating", "label": "Delivery speed & packaging", "required": True},
                    {"type": "radio", "label": "Would you buy from us again?", "options": ["Definitely yes", "Probably yes", "Not sure", "Probably not", "Definitely not"], "required": True},
                    {"type": "range", "label": "How likely are you to recommend us to a friend? (0 = Not at all, 10 = Absolutely)", "required": True},
                    {"type": "textarea", "label": "Tell us more about your experience", "placeholder": "What did you love? What can we do better?", "required": False},
                    {"type": "submit", "label": "Submit Review", "color": "#f59e0b"},
                ],
            },

            # ── SUPPORT ──────────────────────────────────────────────────────
            {
                "id": "bug_report",
                "title": "Bug / Issue Report Form",
                "category": "support",
                "description": "Let users report bugs with full context — OS, browser, steps to reproduce — for faster fixes.",
                "color": "#dc2626",
                "badge": "🔥 Popular",
                "tags": ["bug", "issue", "defect", "software", "support", "QA"],
                "score": 91,
                "score_tip": "Excellent form for engineering teams!",
                "suggestions": [
                    {"icon": "📹", "title": "Add Screen Recording Link", "text": "Video recordings speed up debugging.", "field": {"type": "text", "label": "Screen Recording URL (Loom / Drive)", "placeholder": "Paste link here (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Reporter name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "For follow-up", "required": True},
                    ]},
                    {"type": "text", "label": "Bug / Issue Title", "placeholder": "Short summary, e.g. 'Login button unresponsive on mobile'", "required": True},
                    {"type": "select", "label": "Severity", "options": ["Critical – App unusable", "High – Major feature broken", "Medium – Workaround available", "Low – Minor / cosmetic issue"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Operating System", "options": ["Windows 11", "Windows 10", "macOS", "iOS", "Android", "Linux", "Other"], "required": True},
                        {"type": "select", "label": "Browser", "options": ["Chrome", "Firefox", "Safari", "Edge", "Samsung Internet", "Other", "N/A"], "required": True},
                    ]},
                    {"type": "textarea", "label": "Steps to Reproduce", "placeholder": "1. Go to...\n2. Click on...\n3. See error", "required": True},
                    {"type": "textarea", "label": "Expected vs Actual Behaviour", "placeholder": "Expected: ...\nActual: ...", "required": True},
                    {"type": "file", "label": "Attach Screenshot / Video", "required": False},
                    {"type": "submit", "label": "Report Bug", "color": "#dc2626"},
                ],
            },
            {
                "id": "feature_request",
                "title": "Feature Request Form",
                "category": "support",
                "description": "Collect, prioritise, and track product improvement ideas from users and stakeholders.",
                "color": "#6c63ff",
                "badge": "⭐ New",
                "tags": ["feature", "product", "roadmap", "request", "support"],
                "score": 78,
                "score_tip": "Add business impact field for better prioritisation",
                "suggestions": [
                    {"icon": "📊", "title": "Add Business Impact", "text": "Helps PMs rank requests by value.", "field": {"type": "select", "label": "Business Impact", "options": ["Critical to my workflow", "Would save significant time", "Nice to have", "Minor improvement"], "required": False}},
                    {"icon": "👥", "title": "Add Team Size", "text": "Know how many people this affects.", "field": {"type": "select", "label": "Team / Company Size", "options": ["Just me", "2–10 people", "11–50 people", "50+ people"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Optional", "required": False},
                        {"type": "email", "label": "Email Address", "placeholder": "For updates (optional)", "required": False},
                    ]},
                    {"type": "text", "label": "Feature Title", "placeholder": "Short name for the feature, e.g. 'Bulk CSV export'", "required": True},
                    {"type": "textarea", "label": "Describe the feature", "placeholder": "What should it do? How should it work?", "required": True},
                    {"type": "textarea", "label": "Problem it solves", "placeholder": "What pain point does this address?", "required": True},
                    {"type": "select", "label": "Priority for you", "options": ["Must have – blocking my work", "Important – would use daily", "Nice to have – occasional use", "Just an idea"], "required": True},
                    {"type": "radio", "label": "Are you aware of any workaround?", "options": ["Yes, but it's cumbersome", "No workaround exists"], "required": False},
                    {"type": "submit", "label": "Submit Request", "color": "#6c63ff"},
                ],
            },

            # ── MARKETING ────────────────────────────────────────────────────
            {
                "id": "referral_program",
                "title": "Customer Referral Form",
                "category": "marketing",
                "description": "Capture referrals from happy customers and reward them automatically.",
                "color": "#059669",
                "badge": "🔥 Popular",
                "tags": ["referral", "word of mouth", "growth", "marketing", "loyalty"],
                "score": 83,
                "score_tip": "Add reward selection for higher participation",
                "suggestions": [
                    {"icon": "🎁", "title": "Add Reward Preference", "text": "Let referrers choose their reward.", "field": {"type": "radio", "label": "Preferred Reward", "options": ["₹500 Amazon Gift Card", "10% off next purchase", "Free month of subscription", "Donate to charity"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name (Referrer)", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Your Email", "placeholder": "your@email.com", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Friend's Name", "placeholder": "Who are you referring?", "required": True},
                        {"type": "email", "label": "Friend's Email", "placeholder": "friend@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Friend's Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "textarea", "label": "Why would they benefit from our product?", "placeholder": "Tell us a bit about your friend and their needs...", "required": False},
                    {"type": "radio", "label": "Does your friend know you're referring them?", "options": ["Yes, they're expecting contact", "No, please reach out gently"], "required": True},
                    {"type": "submit", "label": "Submit Referral", "color": "#059669"},
                ],
            },
            {
                "id": "product_waitlist",
                "title": "Product Waitlist / Early Access",
                "category": "marketing",
                "description": "Build hype and capture leads before a product launch with an early access waitlist.",
                "color": "#7c3aed",
                "badge": "⭐ New",
                "tags": ["waitlist", "early access", "launch", "pre-launch", "marketing"],
                "score": 80,
                "score_tip": "Add referral link field for viral waitlist growth",
                "suggestions": [
                    {"icon": "🔗", "title": "Add Share / Referral", "text": "Viral loops can 3x your waitlist size.", "field": {"type": "text", "label": "Referral Code (if you have one)", "placeholder": "Optional", "required": False}},
                    {"icon": "💼", "title": "Add Use Case", "text": "Understand why users want the product.", "field": {"type": "select", "label": "Primary Use Case", "options": ["Personal use", "Small business", "Enterprise / Team", "Developer / Integration", "Research"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email Address", "placeholder": "We'll notify you here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number (optional)", "placeholder": "For SMS updates", "required": False},
                    {"type": "text", "label": "Company / Organisation", "placeholder": "Optional", "required": False},
                    {"type": "select", "label": "How did you hear about us?", "options": ["Twitter / X", "LinkedIn", "Instagram", "Newsletter", "Friend or Colleague", "Search Engine", "Blog / Article", "Other"], "required": False},
                    {"type": "textarea", "label": "What excites you most about this product?", "placeholder": "Tell us what problem it solves for you...", "required": False},
                    {"type": "radio", "label": "Would you pay for early access?", "options": ["Yes, definitely", "Possibly, depending on price", "No, I'd prefer to wait for free version"], "required": False},
                    {"type": "submit", "label": "Join the Waitlist →", "color": "#7c3aed"},
                ],
            },

            # ── FORM TEMPLATES ──────────────────────────────────────────────────
            {
                "id": "ft_simple_contact",
                "title": "Simple Contact Form",
                "category": "form_type",
                "description": "Clean minimal contact form with name, email, and message — ready to embed anywhere.",
                "color": "#1a56db",
                "badge": "📝 Form",
                "tags": ["contact", "form template", "embed"],
                "score": 70,
                "score_tip": "Add phone field to boost reach",
                "suggestions": [
                    {"icon": "📱", "title": "Add Phone", "text": "Reach users via WhatsApp too.", "field": {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Your Name", "placeholder": "Full name", "required": True},
                    {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    {"type": "text", "label": "Subject", "placeholder": "What is this about?", "required": True},
                    {"type": "textarea", "label": "Message", "placeholder": "Write your message here...", "required": True},
                    {"type": "submit", "label": "Send Message", "color": "#1a56db"},
                ],
            },
            {
                "id": "ft_newsletter_signup",
                "title": "Newsletter Signup Form",
                "category": "form_type",
                "description": "Grow your email list fast with a minimal, high-converting newsletter subscription form.",
                "color": "#1a56db",
                "badge": "📝 Form",
                "tags": ["newsletter", "email list", "form template", "marketing"],
                "score": 68,
                "score_tip": "Add interest tags to personalise campaigns",
                "suggestions": [
                    {"icon": "🏷️", "title": "Add Interests", "text": "Segment your audience from day one.", "field": {"type": "checkbox", "label": "Topics you care about", "options": ["Product Updates", "Tutorials", "Case Studies", "Offers"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "First Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Last Name", "placeholder": "Last name", "required": False},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                    {"type": "radio", "label": "Email frequency preference", "options": ["Daily", "Weekly digest", "Monthly only"], "required": False},
                    {"type": "submit", "label": "Subscribe Now", "color": "#1a56db"},
                ],
            },
            {
                "id": "ft_volunteer_signup",
                "title": "Volunteer Registration Form",
                "category": "form_type",
                "description": "Recruit volunteers for events, NGOs, and community drives with this structured signup form.",
                "color": "#059669",
                "badge": "📝 Form",
                "tags": ["volunteer", "ngo", "community", "form template"],
                "score": 75,
                "score_tip": "Add skill tags for better matching",
                "suggestions": [
                    {"icon": "🔧", "title": "Add Skills", "text": "Match volunteers to the right tasks.", "field": {"type": "checkbox", "label": "Your skills", "options": ["Teaching", "Driving", "First Aid", "Cooking", "IT Support", "Photography"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Availability", "options": ["Weekdays only", "Weekends only", "Flexible / Both"], "required": True},
                    {"type": "number", "label": "Hours available per week", "placeholder": "e.g. 5", "required": False},
                    {"type": "textarea", "label": "Why do you want to volunteer?", "placeholder": "Tell us a bit about yourself...", "required": False},
                    {"type": "submit", "label": "Register as Volunteer", "color": "#059669"},
                ],
            },
            {
                "id": "ft_scholarship_apply",
                "title": "Scholarship Application Form",
                "category": "form_type",
                "description": "Collect scholarship applications with academic details, essays, and supporting documents.",
                "color": "#7c3aed",
                "badge": "📝 Form",
                "tags": ["scholarship", "education", "application", "form template"],
                "score": 82,
                "score_tip": "Add referee contact field to score 93+",
                "suggestions": [
                    {"icon": "👤", "title": "Add Referee Contact", "text": "Speeds up background verification.", "field": {"type": "text", "label": "Referee Name & Email", "placeholder": "Name — email@example.com", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Student Full Name", "placeholder": "As per official records", "required": True},
                        {"type": "date", "label": "Date of Birth", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Email Address", "placeholder": "student@email.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Institution / College Name", "placeholder": "Current or last attended", "required": True},
                    {"type": "select", "label": "Course / Programme", "options": ["Engineering", "Medicine", "Arts & Humanities", "Commerce", "Science", "Law", "Other"], "required": True},
                    {"type": "number", "label": "Current CGPA / Percentage", "placeholder": "e.g. 8.5 or 85%", "required": True},
                    {"type": "textarea", "label": "Statement of Purpose", "placeholder": "Why do you deserve this scholarship? (200–300 words)", "required": True},
                    {"type": "file", "label": "Upload Marksheet / Transcript", "required": True},
                    {"type": "submit", "label": "Submit Application", "color": "#7c3aed"},
                ],
            },
            {
                "id": "ft_complaint_box",
                "title": "Anonymous Feedback / Complaint Box",
                "category": "form_type",
                "description": "A safe anonymous channel for employees or students to raise concerns without fear.",
                "color": "#dc2626",
                "badge": "📝 Form",
                "tags": ["anonymous", "complaint", "feedback", "form template", "hr"],
                "score": 76,
                "score_tip": "Keep all fields optional to maximise responses",
                "suggestions": [
                    {"icon": "📎", "title": "Add File Attachment", "text": "Let reporters attach evidence.", "field": {"type": "file", "label": "Attach Supporting File (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "This form is completely anonymous. Your identity will not be recorded or shared."},
                    {"type": "select", "label": "Category of Concern", "options": ["Workplace Harassment", "Discrimination", "Safety Issue", "Policy Violation", "Financial Misconduct", "Other"], "required": True},
                    {"type": "select", "label": "Severity", "options": ["Urgent – needs immediate attention", "Serious – should be addressed soon", "Low – for awareness"], "required": True},
                    {"type": "textarea", "label": "Describe the issue", "placeholder": "Provide as much detail as possible (who, what, when, where)...", "required": True},
                    {"type": "radio", "label": "Would you be willing to speak with HR confidentially?", "options": ["Yes, if needed", "No, prefer to stay anonymous"], "required": False},
                    {"type": "submit", "label": "Submit Anonymously", "color": "#dc2626"},
                ],
            },

            # ── APP TEMPLATES ───────────────────────────────────────────────────
            {
                "id": "app_food_order",
                "title": "Food Order App Form",
                "category": "app_type",
                "description": "Let customers place food orders with menu selection, quantities, and delivery details.",
                "color": "#f59e0b",
                "badge": "📱 App",
                "tags": ["food", "order", "delivery", "app template", "restaurant"],
                "score": 80,
                "score_tip": "Add coupon code field to boost conversions",
                "suggestions": [
                    {"icon": "🎟️", "title": "Add Coupon Code", "text": "Promo codes increase order value.", "field": {"type": "text", "label": "Coupon Code", "placeholder": "Enter code (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Order name", "required": True},
                        {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "checkbox", "label": "Choose your items", "options": ["Veg Burger – ₹149", "Chicken Wrap – ₹199", "Fries – ₹79", "Cold Drink – ₹59", "Dessert – ₹99", "Special Combo – ₹299"], "required": True},
                    {"type": "radio", "label": "Order Type", "options": ["Delivery to my address", "Pick-up from outlet"], "required": True},
                    {"type": "textarea", "label": "Delivery Address", "placeholder": "Full address with landmark", "required": False},
                    {"type": "select", "label": "Payment Method", "options": ["Cash on Delivery", "UPI", "Card on Delivery", "Net Banking"], "required": True},
                    {"type": "textarea", "label": "Special instructions", "placeholder": "No onions, extra spicy, etc.", "required": False},
                    {"type": "submit", "label": "Place Order 🛵", "color": "#f59e0b"},
                ],
            },
            {
                "id": "app_service_request",
                "title": "Home Service Request App",
                "category": "app_type",
                "description": "Book home services like plumbing, electrical, cleaning, or repairs with address and slot.",
                "color": "#0891b2",
                "badge": "📱 App",
                "tags": ["home service", "repair", "booking", "app template"],
                "score": 78,
                "score_tip": "Add photos of the issue for faster diagnosis",
                "suggestions": [
                    {"icon": "📸", "title": "Add Photo Upload", "text": "Technician can prepare before visiting.", "field": {"type": "file", "label": "Photo of the issue (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Customer Name", "placeholder": "Your name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "select", "label": "Service Required", "options": ["Plumbing", "Electrical", "AC Repair / Service", "Carpentry", "Painting", "Deep Cleaning", "Pest Control", "Appliance Repair"], "required": True},
                    {"type": "textarea", "label": "Address", "placeholder": "Flat no., building, street, city, PIN", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Preferred Date", "required": True},
                        {"type": "select", "label": "Time Slot", "options": ["9 AM–11 AM", "11 AM–1 PM", "2 PM–4 PM", "4 PM–6 PM"], "required": True},
                    ]},
                    {"type": "textarea", "label": "Describe the problem", "placeholder": "Brief description of the issue...", "required": False},
                    {"type": "submit", "label": "Book Service →", "color": "#0891b2"},
                ],
            },
            {
                "id": "app_fitness_tracker",
                "title": "Fitness Goal Tracker App",
                "category": "app_type",
                "description": "Help users log fitness goals, track progress, and set weekly targets through a form.",
                "color": "#059669",
                "badge": "📱 App",
                "tags": ["fitness", "health", "tracker", "app template", "goals"],
                "score": 74,
                "score_tip": "Add photo upload for visual progress tracking",
                "suggestions": [
                    {"icon": "📸", "title": "Add Progress Photo", "text": "Before/after photos motivate users.", "field": {"type": "file", "label": "Upload Progress Photo (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "First name", "required": True},
                        {"type": "date", "label": "Date", "required": True},
                    ]},
                    {"type": "select", "label": "Primary Fitness Goal", "options": ["Weight Loss", "Muscle Gain", "Endurance / Stamina", "Flexibility", "General Fitness", "Sports Performance"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "number", "label": "Current Weight (kg)", "placeholder": "e.g. 72", "required": False},
                        {"type": "number", "label": "Target Weight (kg)", "placeholder": "e.g. 65", "required": False},
                    ]},
                    {"type": "checkbox", "label": "Activities this week", "options": ["Running / Jogging", "Gym / Weights", "Yoga", "Swimming", "Cycling", "HIIT", "Sports"], "required": False},
                    {"type": "number", "label": "Total workout minutes this week", "placeholder": "e.g. 180", "required": False},
                    {"type": "rating", "label": "Energy level this week", "required": True},
                    {"type": "textarea", "label": "Notes / Wins this week", "placeholder": "What did you accomplish?", "required": False},
                    {"type": "submit", "label": "Log Progress ✅", "color": "#059669"},
                ],
            },
            {
                "id": "app_travel_itinerary",
                "title": "Travel Itinerary Request App",
                "category": "app_type",
                "description": "Collect trip details to build a custom travel itinerary for your clients.",
                "color": "#7c3aed",
                "badge": "📱 App",
                "tags": ["travel", "itinerary", "trip planning", "app template", "tourism"],
                "score": 79,
                "score_tip": "Add budget range for package personalisation",
                "suggestions": [
                    {"icon": "💰", "title": "Add Budget Range", "text": "Tailor packages to client budgets.", "field": {"type": "select", "label": "Budget per person", "options": ["Under ₹20,000", "₹20,000–₹50,000", "₹50,000–₹1,00,000", "₹1,00,000+"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Lead traveller name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "Itinerary will be sent here", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Destination(s)", "placeholder": "e.g. Goa, Kerala, Ladakh", "required": True},
                        {"type": "number", "label": "Number of Travellers", "placeholder": "e.g. 4", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Departure Date", "required": True},
                        {"type": "date", "label": "Return Date", "required": True},
                    ]},
                    {"type": "checkbox", "label": "Trip preferences", "options": ["Adventure / Trekking", "Beach & Relaxation", "Cultural & Heritage", "Wildlife / Safari", "Honeymoon", "Family-friendly", "Backpacking"], "required": False},
                    {"type": "radio", "label": "Accommodation preference", "options": ["Budget (Hostel / Guesthouse)", "Mid-range (3-star)", "Premium (4–5 star)", "Homestay / Villa"], "required": True},
                    {"type": "textarea", "label": "Any special requirements?", "placeholder": "Dietary needs, accessibility, anniversary, etc.", "required": False},
                    {"type": "submit", "label": "Request My Itinerary ✈️", "color": "#7c3aed"},
                ],
            },
            {
                "id": "app_pet_clinic",
                "title": "Pet Clinic Appointment App",
                "category": "app_type",
                "description": "Schedule vet appointments with pet details, symptoms, and owner contact info.",
                "color": "#db2777",
                "badge": "📱 App",
                "tags": ["vet", "pet", "clinic", "appointment", "app template"],
                "score": 77,
                "score_tip": "Add vaccination record upload to score 90+",
                "suggestions": [
                    {"icon": "💉", "title": "Add Vaccination Record", "text": "Vet can prepare without asking.", "field": {"type": "file", "label": "Upload Vaccination Card (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Pet Owner Name", "placeholder": "Your name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "For appointment confirmation", "required": False},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Pet Name", "placeholder": "e.g. Bruno", "required": True},
                        {"type": "select", "label": "Pet Type", "options": ["Dog", "Cat", "Bird", "Rabbit", "Hamster", "Reptile", "Other"], "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Breed", "placeholder": "e.g. Labrador", "required": False},
                        {"type": "number", "label": "Age (years)", "placeholder": "e.g. 3", "required": False},
                    ]},
                    {"type": "select", "label": "Reason for Visit", "options": ["Routine Check-up", "Vaccination", "Illness / Injury", "Grooming", "Dental Care", "Other"], "required": True},
                    {"type": "textarea", "label": "Symptoms / Notes", "placeholder": "Describe the issue or reason for visit...", "required": False},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Preferred Date", "required": True},
                        {"type": "select", "label": "Time Slot", "options": ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"], "required": True},
                    ]},
                    {"type": "submit", "label": "Book Appointment 🐾", "color": "#db2777"},
                ],
            },

            # ── TABLE TEMPLATES ─────────────────────────────────────────────────
            {
                "id": "tbl_inventory_entry",
                "title": "Inventory Entry Form",
                "category": "table_type",
                "description": "Add new inventory items with SKU, quantity, price, and category for stock management.",
                "color": "#059669",
                "badge": "📊 Table",
                "tags": ["inventory", "stock", "table template", "data entry"],
                "score": 72,
                "score_tip": "Add reorder level field for automatic alerts",
                "suggestions": [
                    {"icon": "🔔", "title": "Add Reorder Level", "text": "Trigger alerts when stock runs low.", "field": {"type": "number", "label": "Reorder Level (units)", "placeholder": "e.g. 20", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Item Name", "placeholder": "Product name", "required": True},
                        {"type": "text", "label": "SKU / Item Code", "placeholder": "e.g. SKU-001", "required": True},
                    ]},
                    {"type": "select", "label": "Category", "options": ["Electronics", "Clothing", "Food & Beverage", "Office Supplies", "Raw Materials", "Spare Parts", "Other"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "number", "label": "Quantity in Stock", "placeholder": "e.g. 100", "required": True},
                        {"type": "number", "label": "Unit Price (₹)", "placeholder": "e.g. 499.00", "required": True},
                    ]},
                    {"type": "select", "label": "Unit of Measurement", "options": ["Pieces", "Kg", "Litres", "Metres", "Box / Carton", "Dozen"], "required": True},
                    {"type": "text", "label": "Supplier / Vendor Name", "placeholder": "Who supplies this item?", "required": False},
                    {"type": "textarea", "label": "Notes", "placeholder": "Any additional details...", "required": False},
                    {"type": "submit", "label": "Add to Inventory", "color": "#059669"},
                ],
            },
            {
                "id": "tbl_daily_expense",
                "title": "Daily Expense Logger",
                "category": "table_type",
                "description": "Track daily business or personal expenses with category, amount, and merchant details.",
                "color": "#b45309",
                "badge": "📊 Table",
                "tags": ["expense", "budget", "finance", "table template", "tracker"],
                "score": 70,
                "score_tip": "Add receipt upload for audit trail",
                "suggestions": [
                    {"icon": "📎", "title": "Add Receipt", "text": "Attach bills for reimbursement claims.", "field": {"type": "file", "label": "Upload Receipt (optional)", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Date", "required": True},
                        {"type": "select", "label": "Category", "options": ["Travel", "Meals", "Office Supplies", "Client Entertainment", "Software / Subscriptions", "Utilities", "Marketing", "Other"], "required": True},
                    ]},
                    {"type": "text", "label": "Merchant / Vendor", "placeholder": "Where was this spent?", "required": True},
                    {"type": "number", "label": "Amount (₹)", "placeholder": "0.00", "required": True},
                    {"type": "radio", "label": "Payment Method", "options": ["Cash", "UPI / QR", "Credit Card", "Debit Card", "Net Banking"], "required": True},
                    {"type": "text", "label": "Project / Cost Centre", "placeholder": "Optional — link to a project", "required": False},
                    {"type": "textarea", "label": "Description", "placeholder": "Brief description of the expense...", "required": False},
                    {"type": "submit", "label": "Log Expense", "color": "#b45309"},
                ],
            },
            {
                "id": "tbl_asset_register",
                "title": "Asset Register Entry",
                "category": "table_type",
                "description": "Record company assets — laptops, furniture, equipment — with purchase and location details.",
                "color": "#4f46e5",
                "badge": "📊 Table",
                "tags": ["assets", "register", "fixed assets", "table template", "finance"],
                "score": 78,
                "score_tip": "Add depreciation rate field for accounting",
                "suggestions": [
                    {"icon": "📉", "title": "Add Depreciation Rate", "text": "Essential for balance sheet accuracy.", "field": {"type": "select", "label": "Depreciation Rate", "options": ["5%", "10%", "15%", "20%", "25%", "33%"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Asset Name", "placeholder": "e.g. Dell Laptop XPS 15", "required": True},
                        {"type": "text", "label": "Asset Tag / Serial No.", "placeholder": "e.g. ASSET-0042", "required": True},
                    ]},
                    {"type": "select", "label": "Asset Category", "options": ["IT Equipment", "Furniture", "Vehicle", "Machinery", "Office Equipment", "Building / Property", "Other"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Purchase Date", "required": True},
                        {"type": "number", "label": "Purchase Cost (₹)", "placeholder": "e.g. 85000", "required": True},
                    ]},
                    {"type": "text", "label": "Assigned To (Employee)", "placeholder": "Name of the user / department", "required": False},
                    {"type": "text", "label": "Location", "placeholder": "e.g. Floor 3, Desk 14", "required": False},
                    {"type": "select", "label": "Condition", "options": ["New", "Good", "Fair", "Needs Repair", "Obsolete"], "required": True},
                    {"type": "submit", "label": "Add Asset Record", "color": "#4f46e5"},
                ],
            },
            {
                "id": "tbl_student_marks",
                "title": "Student Marks Entry Form",
                "category": "table_type",
                "description": "Enter exam scores for students across subjects into a structured data table.",
                "color": "#7c3aed",
                "badge": "📊 Table",
                "tags": ["marks", "grades", "education", "table template", "school"],
                "score": 73,
                "score_tip": "Add grade calculator note to score 85+",
                "suggestions": [
                    {"icon": "🏆", "title": "Add Grade Column", "text": "Auto-grading improves report accuracy.", "field": {"type": "select", "label": "Overall Grade", "options": ["A+ (90–100)", "A (80–89)", "B (70–79)", "C (60–69)", "D (50–59)", "F (Below 50)"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Student Name", "placeholder": "Full name", "required": True},
                        {"type": "text", "label": "Roll Number", "placeholder": "e.g. 2024-CS-042", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Class / Section", "placeholder": "e.g. X-B", "required": True},
                        {"type": "select", "label": "Exam Type", "options": ["Unit Test 1", "Mid-Term", "Unit Test 2", "Final Exam", "Practical"], "required": True},
                    ]},
                    {"type": "number", "label": "Mathematics", "placeholder": "Marks out of 100", "required": False},
                    {"type": "number", "label": "Science", "placeholder": "Marks out of 100", "required": False},
                    {"type": "number", "label": "English", "placeholder": "Marks out of 100", "required": False},
                    {"type": "number", "label": "Social Studies", "placeholder": "Marks out of 100", "required": False},
                    {"type": "number", "label": "Computer Science", "placeholder": "Marks out of 100", "required": False},
                    {"type": "submit", "label": "Save Marks Entry", "color": "#7c3aed"},
                ],
            },
            {
                "id": "tbl_sales_log",
                "title": "Daily Sales Log",
                "category": "table_type",
                "description": "Log daily sales transactions with customer, product, amount, and payment method details.",
                "color": "#0891b2",
                "badge": "📊 Table",
                "tags": ["sales", "revenue", "crm", "table template", "daily log"],
                "score": 75,
                "score_tip": "Add follow-up date field for pipeline tracking",
                "suggestions": [
                    {"icon": "📅", "title": "Add Follow-up Date", "text": "Never miss a follow-up opportunity.", "field": {"type": "date", "label": "Follow-up Date", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Sale Date", "required": True},
                        {"type": "text", "label": "Invoice / Order Number", "placeholder": "e.g. INV-20250101", "required": False},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Customer Name", "placeholder": "Company or individual", "required": True},
                        {"type": "phone", "label": "Customer Phone", "placeholder": "+91 98765 43210", "required": False},
                    ]},
                    {"type": "text", "label": "Product / Service Sold", "placeholder": "Item name or description", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                        {"type": "number", "label": "Total Amount (₹)", "placeholder": "0.00", "required": True},
                    ]},
                    {"type": "select", "label": "Payment Mode", "options": ["Cash", "UPI", "NEFT / RTGS", "Credit Card", "Cheque", "Credit (Due)"], "required": True},
                    {"type": "select", "label": "Sales Rep", "options": ["Self", "Team Member 1", "Team Member 2", "Team Member 3", "Other"], "required": False},
                    {"type": "submit", "label": "Log Sale ✅", "color": "#0891b2"},
                ],
            },

            # ── PDF TEMPLATES ────────────────────────────────────────────────────
            {
                "id": "pdf_invoice_gen",
                "title": "Invoice Generation Form",
                "category": "pdf_type",
                "description": "Collect billing details to generate a professional invoice PDF for clients.",
                "color": "#dc2626",
                "badge": "📄 PDF",
                "tags": ["invoice", "billing", "pdf template", "accounts"],
                "score": 83,
                "score_tip": "Add GST breakdown field for compliance",
                "suggestions": [
                    {"icon": "🧾", "title": "Add GST Details", "text": "Required for B2B billing in India.", "field": {"type": "text", "label": "GST Number (Seller)", "placeholder": "22AAAAA0000A1Z5", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Client / Company Name", "placeholder": "Bill To", "required": True},
                        {"type": "email", "label": "Client Email", "placeholder": "invoice@client.com", "required": True},
                    ]},
                    {"type": "text", "label": "Client Address", "placeholder": "Full billing address", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Invoice Date", "required": True},
                        {"type": "date", "label": "Due Date", "required": True},
                    ]},
                    {"type": "textarea", "label": "Items / Services (list each on a new line)", "placeholder": "Web Design – ₹25,000\nSEO Package – ₹8,000\nDomain & Hosting – ₹3,500", "required": True},
                    {"type": "number", "label": "Subtotal (₹)", "placeholder": "0.00", "required": True},
                    {"type": "number", "label": "GST / Tax %", "placeholder": "18", "required": False},
                    {"type": "textarea", "label": "Payment Instructions / Bank Details", "placeholder": "Account No., IFSC, UPI ID...", "required": False},
                    {"type": "submit", "label": "Generate Invoice PDF", "color": "#dc2626"},
                ],
            },
            {
                "id": "pdf_noc_request",
                "title": "NOC / Certificate Request",
                "category": "pdf_type",
                "description": "Request a No Objection Certificate or official letter from an organisation.",
                "color": "#4f46e5",
                "badge": "📄 PDF",
                "tags": ["noc", "certificate", "letter", "pdf template", "official"],
                "score": 74,
                "score_tip": "Add purpose dropdown for faster processing",
                "suggestions": [
                    {"icon": "🎯", "title": "Add Purpose", "text": "Route request to correct department.", "field": {"type": "select", "label": "Purpose of NOC", "options": ["Visa Application", "Bank Loan", "Educational Admission", "Property Transfer", "Job Change", "Other"], "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Applicant Full Name", "placeholder": "As per official records", "required": True},
                        {"type": "text", "label": "ID / Employee No.", "placeholder": "e.g. EMP-1042 or Roll No.", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Organisation / Institution", "placeholder": "Issuing authority", "required": True},
                    {"type": "select", "label": "Certificate Type", "options": ["No Objection Certificate", "Experience Certificate", "Bonafide Certificate", "Salary Certificate", "Character Certificate", "Other"], "required": True},
                    {"type": "textarea", "label": "Reason / Purpose", "placeholder": "Explain why you need this certificate...", "required": True},
                    {"type": "date", "label": "Required By Date", "required": False},
                    {"type": "submit", "label": "Submit Request", "color": "#4f46e5"},
                ],
            },
            {
                "id": "pdf_medical_report",
                "title": "Patient Medical Report Form",
                "category": "pdf_type",
                "description": "Capture patient vitals, symptoms, and diagnosis details for generating a medical report.",
                "color": "#059669",
                "badge": "📄 PDF",
                "tags": ["medical", "health", "report", "pdf template", "clinic"],
                "score": 86,
                "score_tip": "Add allergy section to score 95+",
                "suggestions": [
                    {"icon": "⚠️", "title": "Add Allergy Section", "text": "Critical for patient safety.", "field": {"type": "textarea", "label": "Known Allergies", "placeholder": "List any known drug or food allergies...", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Patient Name", "placeholder": "Full name", "required": True},
                        {"type": "date", "label": "Date of Birth", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Patient ID", "placeholder": "Hospital / Clinic ID", "required": False},
                        {"type": "date", "label": "Report Date", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "number", "label": "Weight (kg)", "placeholder": "e.g. 70", "required": False},
                        {"type": "number", "label": "Height (cm)", "placeholder": "e.g. 170", "required": False},
                    ]},
                    {"type": "text", "label": "Blood Pressure", "placeholder": "e.g. 120/80 mmHg", "required": False},
                    {"type": "text", "label": "Temperature", "placeholder": "e.g. 98.6°F", "required": False},
                    {"type": "textarea", "label": "Chief Complaints / Symptoms", "placeholder": "Patient-reported symptoms...", "required": True},
                    {"type": "textarea", "label": "Diagnosis", "placeholder": "Doctor's diagnosis...", "required": True},
                    {"type": "textarea", "label": "Prescription / Treatment Plan", "placeholder": "Medicines, dosage, instructions...", "required": False},
                    {"type": "submit", "label": "Generate Report PDF", "color": "#059669"},
                ],
            },
            {
                "id": "pdf_resume_builder",
                "title": "Resume / CV Builder Form",
                "category": "pdf_type",
                "description": "Collect candidate details to generate a formatted resume PDF automatically.",
                "color": "#0891b2",
                "badge": "📄 PDF",
                "tags": ["resume", "cv", "job", "pdf template", "career"],
                "score": 81,
                "score_tip": "Add skills rating for visual resume charts",
                "suggestions": [
                    {"icon": "⭐", "title": "Add Skills Rating", "text": "Visual skill bars make resumes stand out.", "field": {"type": "checkbox", "label": "Technical Skills (select all that apply)", "options": ["JavaScript", "Python", "React", "Node.js", "SQL", "Machine Learning", "UI/UX Design", "Cloud / AWS"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your full name", "required": True},
                        {"type": "text", "label": "Professional Title", "placeholder": "e.g. Full Stack Developer", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "LinkedIn / Portfolio URL", "placeholder": "https://linkedin.com/in/yourname", "required": False},
                    {"type": "textarea", "label": "Professional Summary", "placeholder": "2–3 sentences about your experience and goals...", "required": True},
                    {"type": "textarea", "label": "Work Experience", "placeholder": "Company | Role | Duration\nKey achievements...", "required": True},
                    {"type": "textarea", "label": "Education", "placeholder": "Degree | Institution | Year\nGPA / Percentage", "required": True},
                    {"type": "textarea", "label": "Skills & Certifications", "placeholder": "List your technical and soft skills...", "required": False},
                    {"type": "submit", "label": "Build My Resume PDF", "color": "#0891b2"},
                ],
            },
            {
                "id": "pdf_proposal",
                "title": "Business Proposal Form",
                "category": "pdf_type",
                "description": "Fill in proposal details to generate a professional business or project proposal document.",
                "color": "#7c3aed",
                "badge": "📄 PDF",
                "tags": ["proposal", "business", "project", "pdf template", "client"],
                "score": 79,
                "score_tip": "Add case study references to build credibility",
                "suggestions": [
                    {"icon": "📚", "title": "Add Case Studies", "text": "Proof of past work wins proposals.", "field": {"type": "textarea", "label": "Relevant Case Studies / Past Work", "placeholder": "Briefly describe 1–2 relevant projects you've done...", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Prepared By (Your Name / Company)", "placeholder": "Your name or agency", "required": True},
                        {"type": "date", "label": "Proposal Date", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Client Name / Company", "placeholder": "Proposal recipient", "required": True},
                        {"type": "email", "label": "Client Email", "placeholder": "client@company.com", "required": True},
                    ]},
                    {"type": "text", "label": "Project Title", "placeholder": "Brief project name", "required": True},
                    {"type": "textarea", "label": "Project Overview", "placeholder": "What problem are we solving? What is the goal?", "required": True},
                    {"type": "textarea", "label": "Scope of Work", "placeholder": "List all deliverables and what is included...", "required": True},
                    {"type": "number", "label": "Total Project Budget (₹)", "placeholder": "0.00", "required": True},
                    {"type": "text", "label": "Estimated Timeline", "placeholder": "e.g. 6 weeks from project kickoff", "required": True},
                    {"type": "textarea", "label": "Payment Terms", "placeholder": "e.g. 50% advance, 50% on delivery", "required": False},
                    {"type": "submit", "label": "Generate Proposal PDF", "color": "#7c3aed"},
                ],
            },

            # ── CARD FORM TEMPLATES ──────────────────────────────────────────────
            {
                "id": "card_product_buy",
                "title": "Product Purchase Card",
                "category": "card_form_type",
                "description": "One-page card checkout for single products with quantity, address, and payment.",
                "color": "#1a56db",
                "badge": "💳 Card Form",
                "tags": ["purchase", "checkout", "payment", "card form", "ecommerce"],
                "score": 82,
                "score_tip": "Add UPI payment to boost India conversions by 40%",
                "suggestions": [
                    {"icon": "📱", "title": "Add UPI Payment", "text": "60%+ Indian users prefer UPI.", "field": {"type": "text", "label": "UPI ID", "placeholder": "yourname@upi", "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "📦 Product Details"},
                    {"type": "select", "label": "Product", "options": ["Basic Plan – ₹999", "Pro Plan – ₹2,499", "Enterprise – ₹7,999"], "required": True},
                    {"type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "🚚 Shipping Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Recipient name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "textarea", "label": "Delivery Address", "placeholder": "Flat no., building, street, city, PIN", "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "💳 Payment"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Pay & Order Now", "color": "#1a56db"},
                ],
            },
            {
                "id": "card_event_ticket",
                "title": "Event Ticket Purchase",
                "category": "card_form_type",
                "description": "Sell event tickets with attendee info, ticket tier, and card payment in one clean form.",
                "color": "#7c3aed",
                "badge": "💳 Card Form",
                "tags": ["ticket", "event", "purchase", "card form", "payment"],
                "score": 80,
                "score_tip": "Add seat selection for premium events",
                "suggestions": [
                    {"icon": "🪑", "title": "Add Seat Selection", "text": "Assigned seating reduces day-of chaos.", "field": {"type": "select", "label": "Seat Zone", "options": ["Zone A (Front – Premium)", "Zone B (Middle)", "Zone C (Back – Economy)"], "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "🎟️ Select Your Ticket"},
                    {"type": "radio", "label": "Ticket Type", "options": ["General Entry – ₹499", "VIP Access – ₹1,499", "Table for 4 – ₹4,999"], "required": True},
                    {"type": "number", "label": "Number of Tickets", "placeholder": "1", "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "👤 Attendee Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Lead attendee", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Tickets sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "💳 Payment"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Buy Tickets 🎉", "color": "#7c3aed"},
                ],
            },
            {
                "id": "card_donation",
                "title": "Donation & Fundraising Card",
                "category": "card_form_type",
                "description": "Accept one-time or recurring donations with cause selection and card payment.",
                "color": "#dc2626",
                "badge": "💳 Card Form",
                "tags": ["donation", "charity", "ngo", "card form", "fundraising"],
                "score": 78,
                "score_tip": "Add 80G tax receipt option for India donors",
                "suggestions": [
                    {"icon": "🧾", "title": "Add Tax Receipt", "text": "80G receipt drives larger donations.", "field": {"type": "radio", "label": "Send 80G Tax Receipt?", "options": ["Yes, send me a receipt", "No, thank you"], "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "💝 Choose Your Donation"},
                    {"type": "radio", "label": "Donation Amount", "options": ["₹500", "₹1,000", "₹2,500", "₹5,000", "₹10,000", "Custom amount"], "required": True},
                    {"type": "radio", "label": "Donation Frequency", "options": ["One-time", "Monthly recurring"], "required": True},
                    {"type": "select", "label": "Cause", "options": ["Child Education", "Women Empowerment", "Environment", "Disaster Relief", "Animal Welfare", "Where Needed Most"], "required": False},
                    {"type": "divider"},
                    {"type": "section", "label": "👤 Donor Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Donor name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Receipt sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone (optional)", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "divider"},
                    {"type": "section", "label": "💳 Secure Payment"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Donate Now ❤️", "color": "#dc2626"},
                ],
            },
            {
                "id": "card_membership_join",
                "title": "Membership Signup Card",
                "category": "card_form_type",
                "description": "Onboard members with plan selection, personal details, and card billing in one page.",
                "color": "#059669",
                "badge": "💳 Card Form",
                "tags": ["membership", "subscription", "join", "card form", "billing"],
                "score": 84,
                "score_tip": "Add annual billing toggle for 20% savings to boost upgrades",
                "suggestions": [
                    {"icon": "🔄", "title": "Add Annual Toggle", "text": "Annual plans increase LTV by 3x.", "field": {"type": "radio", "label": "Billing Cycle", "options": ["Monthly", "Annual (Save 20%)"], "required": True}},
                ],
                "fields": [
                    {"type": "section", "label": "🏅 Choose Your Plan"},
                    {"type": "radio", "label": "Membership Tier", "options": ["Silver – ₹499/mo", "Gold – ₹999/mo", "Platinum – ₹2,499/mo"], "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "👤 Personal Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "you@email.com", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "date", "label": "Date of Birth (for birthday perks)", "required": False},
                    {"type": "divider"},
                    {"type": "section", "label": "💳 Billing"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Activate Membership →", "color": "#059669"},
                ],
            },
            {
                "id": "card_course_purchase",
                "title": "Online Course Purchase Card",
                "category": "card_form_type",
                "description": "Sell online courses with course selection, student details, and secure card payment.",
                "color": "#f59e0b",
                "badge": "💳 Card Form",
                "tags": ["course", "education", "purchase", "card form", "online learning"],
                "score": 81,
                "score_tip": "Add instalment option to reduce cart abandonment",
                "suggestions": [
                    {"icon": "💰", "title": "Add EMI Option", "text": "Instalment plans increase conversion by 30%.", "field": {"type": "radio", "label": "Payment Option", "options": ["Full Payment", "3 EMIs (₹0 interest)", "6 EMIs"], "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "📚 Select Your Course"},
                    {"type": "select", "label": "Course", "options": ["Web Development Bootcamp – ₹14,999", "Data Science Masterclass – ₹19,999", "UI/UX Design Course – ₹9,999", "Digital Marketing – ₹7,999", "Python for Beginners – ₹4,999"], "required": True},
                    {"type": "radio", "label": "Access Type", "options": ["Lifetime Access", "6-Month Access", "1-Year Access"], "required": True},
                    {"type": "divider"},
                    {"type": "section", "label": "👤 Student Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Full Name", "placeholder": "Your name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Login credentials sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "text", "label": "Coupon Code", "placeholder": "Optional discount code", "required": False},
                    {"type": "divider"},
                    {"type": "section", "label": "💳 Secure Payment"},
                    {"type": "cardicons"},
                    {"type": "cardnum"},
                    {"type": "row3card"},
                    {"type": "submit", "label": "Enroll & Pay Now 🎓", "color": "#f59e0b"},
                ],
            },

            # ── STORE BUILDER TEMPLATES ──────────────────────────────────────────
            {
                "id": "store_product_order",
                "title": "Product Order Form",
                "category": "store_type",
                "description": "Take product orders with item selection, variants, shipping, and payment method.",
                "color": "#0891b2",
                "badge": "🛒 Store",
                "tags": ["store", "product", "order", "ecommerce", "store builder"],
                "score": 79,
                "score_tip": "Add stock availability check to reduce overselling",
                "suggestions": [
                    {"icon": "📦", "title": "Add Stock Note", "text": "Inform buyers of limited stock.", "field": {"type": "section", "label": "⚠️ Limited stock available — orders processed on first come, first served basis."}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Customer Name", "placeholder": "Your full name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Order confirmation sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": True},
                    {"type": "select", "label": "Product", "options": ["Product A – ₹499", "Product B – ₹999", "Product C – ₹1,499", "Product D – ₹2,999", "Bundle Pack – ₹3,999"], "required": True},
                    {"type": "select", "label": "Variant / Size", "options": ["Small", "Medium", "Large", "XL", "XXL", "One Size"], "required": False},
                    {"type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                    {"type": "textarea", "label": "Delivery Address", "placeholder": "Full address with PIN code", "required": True},
                    {"type": "radio", "label": "Payment Method", "options": ["UPI / QR Code", "Cash on Delivery", "Bank Transfer", "Card (Swipe on Delivery)"], "required": True},
                    {"type": "submit", "label": "Place Order 🛒", "color": "#0891b2"},
                ],
            },
            {
                "id": "store_custom_order",
                "title": "Custom / Personalised Order Form",
                "category": "store_type",
                "description": "Accept orders for personalised or custom-made products with design specifications.",
                "color": "#db2777",
                "badge": "🛒 Store",
                "tags": ["custom", "personalised", "order", "store builder", "handmade"],
                "score": 76,
                "score_tip": "Add design file upload to reduce back-and-forth",
                "suggestions": [
                    {"icon": "🎨", "title": "Add Design Upload", "text": "Customers can share their design files.", "field": {"type": "file", "label": "Upload Design / Reference Image", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Customer name", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "email", "label": "Email Address", "placeholder": "Order updates sent here", "required": True},
                    {"type": "select", "label": "Product Type", "options": ["Personalised Mug", "Custom T-Shirt", "Engraved Jewellery", "Custom Cake", "Handmade Gift Box", "Photo Frame", "Other"], "required": True},
                    {"type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                    {"type": "textarea", "label": "Customisation Details", "placeholder": "Names, messages, colours, design preferences...", "required": True},
                    {"type": "date", "label": "Required By Date", "required": True},
                    {"type": "textarea", "label": "Delivery Address", "placeholder": "Full address with PIN", "required": True},
                    {"type": "select", "label": "Budget Range", "options": ["Under ₹500", "₹500–₹1,000", "₹1,000–₹2,500", "₹2,500+", "Tell me the price"], "required": False},
                    {"type": "submit", "label": "Submit Custom Order ✨", "color": "#db2777"},
                ],
            },
            {
                "id": "store_wholesale",
                "title": "Wholesale / Bulk Order Form",
                "category": "store_type",
                "description": "Capture bulk order inquiries from distributors and retailers with MOQ and pricing.",
                "color": "#059669",
                "badge": "🛒 Store",
                "tags": ["wholesale", "bulk", "b2b", "store builder", "distributor"],
                "score": 80,
                "score_tip": "Add GST field for B2B invoicing compliance",
                "suggestions": [
                    {"icon": "🧾", "title": "Add GST Number", "text": "Required for B2B invoice generation.", "field": {"type": "text", "label": "GST Number", "placeholder": "22AAAAA0000A1Z5", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Business Name", "placeholder": "Company / Shop name", "required": True},
                        {"type": "text", "label": "Contact Person", "placeholder": "Your name", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Business Email", "placeholder": "orders@business.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "select", "label": "Business Type", "options": ["Retailer", "Distributor", "Reseller", "Manufacturer", "Export House", "Other"], "required": True},
                    {"type": "textarea", "label": "Products Required (with quantities)", "placeholder": "Product A – 500 units\nProduct B – 200 units", "required": True},
                    {"type": "select", "label": "Order Value Range", "options": ["Under ₹50,000", "₹50,000–₹2,00,000", "₹2,00,000–₹10,00,000", "Above ₹10,00,000"], "required": False},
                    {"type": "date", "label": "Expected Delivery Date", "required": False},
                    {"type": "text", "label": "Delivery State", "placeholder": "e.g. Maharashtra", "required": True},
                    {"type": "submit", "label": "Request Wholesale Quote", "color": "#059669"},
                ],
            },
            {
                "id": "store_preorder",
                "title": "Pre-Order / Launch Form",
                "category": "store_type",
                "description": "Capture pre-orders for upcoming products to gauge demand before manufacturing.",
                "color": "#7c3aed",
                "badge": "🛒 Store",
                "tags": ["pre-order", "launch", "store builder", "demand", "waitlist"],
                "score": 77,
                "score_tip": "Add referral code for viral pre-order growth",
                "suggestions": [
                    {"icon": "🔗", "title": "Add Referral", "text": "Referral codes grow pre-order lists virally.", "field": {"type": "text", "label": "Referral Code (get ₹100 off)", "placeholder": "Optional", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Your Name", "placeholder": "Full name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Launch update + order link sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone Number", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Product / Variant", "options": ["Standard Edition", "Limited Edition", "Collector's Edition", "Bundle Pack"], "required": True},
                    {"type": "number", "label": "Quantity", "placeholder": "1", "required": True},
                    {"type": "textarea", "label": "Delivery Address", "placeholder": "We'll ship when available", "required": True},
                    {"type": "radio", "label": "Payment Preference", "options": ["Pay full amount now (10% off)", "Pay 50% now, rest on delivery", "Pay full on delivery"], "required": True},
                    {"type": "textarea", "label": "Any customisation requests?", "placeholder": "Optional notes...", "required": False},
                    {"type": "submit", "label": "Pre-Order Now 🚀", "color": "#7c3aed"},
                ],
            },
            {
                "id": "store_service_package",
                "title": "Service Package Booking",
                "category": "store_type",
                "description": "Sell service packages (design, consulting, development) with package selection and brief.",
                "color": "#4f46e5",
                "badge": "🛒 Store",
                "tags": ["service", "package", "consulting", "store builder", "freelance"],
                "score": 82,
                "score_tip": "Add timeline expectations to reduce scope creep",
                "suggestions": [
                    {"icon": "📅", "title": "Add Timeline Expectation", "text": "Aligns client expectations upfront.", "field": {"type": "select", "label": "Expected Start Timeline", "options": ["ASAP", "Within 1 week", "Within 2 weeks", "Next month", "Flexible"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Client Name", "placeholder": "Your / company name", "required": True},
                        {"type": "email", "label": "Email", "placeholder": "Proposal sent here", "required": True},
                    ]},
                    {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": False},
                    {"type": "select", "label": "Service Package", "options": ["Starter Pack – ₹9,999", "Growth Pack – ₹24,999", "Pro Pack – ₹49,999", "Enterprise – Custom Quote"], "required": True},
                    {"type": "checkbox", "label": "Services needed (select all)", "options": ["Website Design", "Mobile App", "SEO / Content", "Social Media", "Branding / Logo", "Backend / API", "Consulting"], "required": True},
                    {"type": "textarea", "label": "Project Brief", "placeholder": "Describe your project, goals, and requirements...", "required": True},
                    {"type": "textarea", "label": "Reference websites / apps you like", "placeholder": "Share links for inspiration (optional)", "required": False},
                    {"type": "submit", "label": "Book This Package 📦", "color": "#4f46e5"},
                ],
            },

            # ── WORKFLOW TEMPLATES ───────────────────────────────────────────────
            {
                "id": "wf_purchase_request",
                "title": "Purchase Request / PR Form",
                "category": "workflow_type",
                "description": "Submit internal purchase requests for approval before buying equipment or services.",
                "color": "#f59e0b",
                "badge": "⚡ Workflow",
                "tags": ["purchase", "procurement", "approval", "workflow", "internal"],
                "score": 81,
                "score_tip": "Add manager name for automatic routing",
                "suggestions": [
                    {"icon": "👤", "title": "Add Approver Name", "text": "Routes the request to the right manager.", "field": {"type": "text", "label": "Reporting Manager / Approver", "placeholder": "Manager full name", "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Requested By", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Department", "placeholder": "e.g. Marketing", "required": True},
                    ]},
                    {"type": "date", "label": "Request Date", "required": True},
                    {"type": "textarea", "label": "Item(s) / Service(s) Required", "placeholder": "Name, description, quantity, specs...", "required": True},
                    {"type": "number", "label": "Estimated Total Cost (₹)", "placeholder": "0.00", "required": True},
                    {"type": "text", "label": "Suggested Vendor / Supplier", "placeholder": "Optional", "required": False},
                    {"type": "select", "label": "Priority", "options": ["Urgent – needed immediately", "High – needed this week", "Normal – within 30 days", "Low – when possible"], "required": True},
                    {"type": "textarea", "label": "Business Justification", "placeholder": "Why is this purchase necessary?", "required": True},
                    {"type": "submit", "label": "Submit Purchase Request", "color": "#f59e0b"},
                ],
            },
            {
                "id": "wf_change_request",
                "title": "Change Request Form",
                "category": "workflow_type",
                "description": "Document scope changes or feature requests in a project with impact and approval workflow.",
                "color": "#0891b2",
                "badge": "⚡ Workflow",
                "tags": ["change request", "scope", "project", "workflow", "approval"],
                "score": 83,
                "score_tip": "Add impact analysis section for better decisions",
                "suggestions": [
                    {"icon": "📊", "title": "Add Impact Analysis", "text": "Helps managers approve with full context.", "field": {"type": "textarea", "label": "Impact Analysis (time, cost, risk)", "placeholder": "Describe how this change affects timeline, budget, and other features...", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Requested By", "placeholder": "Your name", "required": True},
                        {"type": "date", "label": "Date", "required": True},
                    ]},
                    {"type": "text", "label": "Project / Product Name", "placeholder": "Which project does this affect?", "required": True},
                    {"type": "text", "label": "Change Title", "placeholder": "Brief summary of the change", "required": True},
                    {"type": "textarea", "label": "Description of Change", "placeholder": "What needs to change and why?", "required": True},
                    {"type": "select", "label": "Change Type", "options": ["Scope Addition", "Scope Reduction", "Design Change", "Technology Change", "Process Change", "Emergency Fix"], "required": True},
                    {"type": "select", "label": "Priority", "options": ["Critical", "High", "Medium", "Low"], "required": True},
                    {"type": "number", "label": "Estimated Additional Effort (hours)", "placeholder": "0", "required": False},
                    {"type": "textarea", "label": "Proposed Solution / Approach", "placeholder": "How do you suggest implementing this?", "required": False},
                    {"type": "submit", "label": "Submit Change Request", "color": "#0891b2"},
                ],
            },
            {
                "id": "wf_access_request",
                "title": "IT Access / Permission Request",
                "category": "workflow_type",
                "description": "Request access to systems, tools, VPN, or sensitive data through an approval workflow.",
                "color": "#4f46e5",
                "badge": "⚡ Workflow",
                "tags": ["it", "access", "permission", "workflow", "security"],
                "score": 79,
                "score_tip": "Add business justification for audit compliance",
                "suggestions": [
                    {"icon": "📝", "title": "Add Justification", "text": "Required for SOC 2 / ISO 27001 audits.", "field": {"type": "textarea", "label": "Business Justification", "placeholder": "Why do you need this access?", "required": True}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Employee Name", "placeholder": "Your name", "required": True},
                        {"type": "text", "label": "Employee ID", "placeholder": "e.g. EMP-1042", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Work Email", "placeholder": "you@company.com", "required": True},
                        {"type": "text", "label": "Department", "placeholder": "Your department", "required": True},
                    ]},
                    {"type": "checkbox", "label": "Access Required (select all that apply)", "options": ["VPN Access", "Admin Panel", "Database Access", "Financial Systems", "HR Systems", "Cloud Storage", "CRM / Sales Tools", "Development / Code Repo"], "required": True},
                    {"type": "select", "label": "Access Level Required", "options": ["Read Only", "Read / Write", "Admin / Full Control", "Temporary (specify duration)"], "required": True},
                    {"type": "text", "label": "Duration (if temporary)", "placeholder": "e.g. 30 days, until project end", "required": False},
                    {"type": "text", "label": "Approving Manager", "placeholder": "Your manager's name", "required": True},
                    {"type": "submit", "label": "Submit Access Request 🔐", "color": "#4f46e5"},
                ],
            },
            {
                "id": "wf_incident_report",
                "title": "Incident Report Form",
                "category": "workflow_type",
                "description": "Document workplace incidents — accidents, safety hazards, near-misses — for HR review.",
                "color": "#dc2626",
                "badge": "⚡ Workflow",
                "tags": ["incident", "safety", "accident", "workflow", "hr", "compliance"],
                "score": 85,
                "score_tip": "Add witness details to strengthen the report",
                "suggestions": [
                    {"icon": "👁️", "title": "Add Witness Details", "text": "Corroboration speeds up investigations.", "field": {"type": "row2", "fields": [{"type": "text", "label": "Witness Name", "placeholder": "Optional", "required": False}, {"type": "phone", "label": "Witness Contact", "placeholder": "Optional", "required": False}]}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Reporter Name", "placeholder": "Person filing this report", "required": True},
                        {"type": "date", "label": "Date of Incident", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Time of Incident", "placeholder": "e.g. 2:30 PM", "required": True},
                        {"type": "text", "label": "Location", "placeholder": "Where did it happen?", "required": True},
                    ]},
                    {"type": "select", "label": "Incident Type", "options": ["Physical Injury", "Near Miss", "Equipment Damage", "Fire / Electrical Hazard", "Chemical / Spill", "Security Breach", "Verbal / Harassment", "Other"], "required": True},
                    {"type": "select", "label": "Severity", "options": ["Minor – No injury", "Moderate – First Aid needed", "Serious – Medical attention needed", "Critical – Hospitalisation"], "required": True},
                    {"type": "text", "label": "Person(s) Involved", "placeholder": "Names of those involved", "required": False},
                    {"type": "textarea", "label": "Detailed Description", "placeholder": "Describe exactly what happened, sequence of events...", "required": True},
                    {"type": "textarea", "label": "Immediate Actions Taken", "placeholder": "What was done right after the incident?", "required": False},
                    {"type": "file", "label": "Attach Photos / Evidence", "required": False},
                    {"type": "submit", "label": "Submit Incident Report 🚨", "color": "#dc2626"},
                ],
            },
            {
                "id": "wf_content_approval",
                "title": "Content Approval Workflow",
                "category": "workflow_type",
                "description": "Submit blog posts, social content, or ads for review and approval before publishing.",
                "color": "#7c3aed",
                "badge": "⚡ Workflow",
                "tags": ["content", "approval", "marketing", "workflow", "review"],
                "score": 77,
                "score_tip": "Add scheduled publish date for editorial calendar",
                "suggestions": [
                    {"icon": "📅", "title": "Add Publish Date", "text": "Plan content calendar in advance.", "field": {"type": "date", "label": "Requested Publish Date", "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Content Creator", "placeholder": "Your name", "required": True},
                        {"type": "date", "label": "Submission Date", "required": True},
                    ]},
                    {"type": "select", "label": "Content Type", "options": ["Blog Post", "Social Media Post", "Email Campaign", "Ad Copy", "Video Script", "Press Release", "Landing Page Copy", "Other"], "required": True},
                    {"type": "select", "label": "Target Platform", "options": ["Company Website", "LinkedIn", "Instagram", "Twitter / X", "Facebook", "YouTube", "Email Newsletter", "Multiple Platforms"], "required": True},
                    {"type": "text", "label": "Content Title / Headline", "placeholder": "Title of the content piece", "required": True},
                    {"type": "textarea", "label": "Content Body / Script", "placeholder": "Paste the full content here for review...", "required": True},
                    {"type": "text", "label": "CTA (Call to Action)", "placeholder": "e.g. 'Sign up now', 'Learn more'", "required": False},
                    {"type": "text", "label": "Target Reviewer / Editor", "placeholder": "Who should approve this?", "required": True},
                    {"type": "textarea", "label": "Notes for Reviewer", "placeholder": "Context, links, brand guidelines to follow...", "required": False},
                    {"type": "submit", "label": "Submit for Approval ✅", "color": "#7c3aed"},
                ],
            },

            # ── SIGN TEMPLATES ───────────────────────────────────────────────────
            {
                "id": "sign_freelance_contract",
                "title": "Freelance Service Contract",
                "category": "sign_type",
                "description": "A signed agreement between a freelancer and client covering scope, payment, and terms.",
                "color": "#4f46e5",
                "badge": "✍️ Sign",
                "tags": ["contract", "freelance", "agreement", "sign template", "legal"],
                "score": 87,
                "score_tip": "Add IP ownership clause to avoid disputes",
                "suggestions": [
                    {"icon": "⚖️", "title": "Add IP Ownership", "text": "Specifies who owns the final work.", "field": {"type": "radio", "label": "Intellectual Property Ownership", "options": ["Client owns all work on final payment", "Freelancer retains portfolio rights", "Shared ownership (as agreed)"], "required": True}},
                ],
                "fields": [
                    {"type": "section", "label": "📋 Contract Details"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Freelancer Name", "placeholder": "Service provider name", "required": True},
                        {"type": "text", "label": "Client Name / Company", "placeholder": "Client name", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Freelancer Email", "placeholder": "freelancer@email.com", "required": True},
                        {"type": "email", "label": "Client Email", "placeholder": "client@email.com", "required": True},
                    ]},
                    {"type": "date", "label": "Contract Start Date", "required": True},
                    {"type": "text", "label": "Project Title / Scope", "placeholder": "Brief description of the work", "required": True},
                    {"type": "number", "label": "Total Project Value (₹)", "placeholder": "0.00", "required": True},
                    {"type": "textarea", "label": "Payment Terms", "placeholder": "e.g. 50% advance, 50% on delivery within 7 days", "required": True},
                    {"type": "textarea", "label": "Revision Policy", "placeholder": "e.g. 2 rounds of revisions included", "required": False},
                    {"type": "radio", "label": "Confidentiality Agreement", "options": ["I agree to keep all project details confidential", "No confidentiality required"], "required": True},
                    {"type": "text", "label": "Client Signature (Type Full Name)", "placeholder": "Type your name as signature", "required": True},
                    {"type": "date", "label": "Signing Date", "required": True},
                    {"type": "submit", "label": "Sign & Submit Contract ✍️", "color": "#4f46e5"},
                ],
            },
            {
                "id": "sign_nda",
                "title": "Non-Disclosure Agreement (NDA)",
                "category": "sign_type",
                "description": "Protect confidential business information with a mutual or one-way NDA form.",
                "color": "#0f172a",
                "badge": "✍️ Sign",
                "tags": ["nda", "confidentiality", "legal", "sign template", "agreement"],
                "score": 90,
                "score_tip": "Add jurisdiction clause for enforceability",
                "suggestions": [
                    {"icon": "⚖️", "title": "Add Jurisdiction", "text": "Required for legal enforceability.", "field": {"type": "text", "label": "Governing Law / Jurisdiction", "placeholder": "e.g. Laws of Maharashtra, India", "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "🔏 Non-Disclosure Agreement"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Disclosing Party (Company/Person)", "placeholder": "Who is sharing the information", "required": True},
                        {"type": "text", "label": "Receiving Party (Company/Person)", "placeholder": "Who is receiving the information", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Disclosing Party Email", "placeholder": "email@company.com", "required": True},
                        {"type": "email", "label": "Receiving Party Email", "placeholder": "email@recipient.com", "required": True},
                    ]},
                    {"type": "radio", "label": "NDA Type", "options": ["Mutual (both parties share confidential info)", "One-Way (only one party shares info)"], "required": True},
                    {"type": "textarea", "label": "Definition of Confidential Information", "placeholder": "Describe what information is considered confidential...", "required": True},
                    {"type": "select", "label": "NDA Duration", "options": ["1 Year", "2 Years", "3 Years", "5 Years", "Indefinite"], "required": True},
                    {"type": "text", "label": "Purpose of Disclosure", "placeholder": "Why is this information being shared?", "required": True},
                    {"type": "radio", "label": "I agree to the terms of this NDA and provide my signature", "options": ["I agree and sign", "I need to review before signing"], "required": True},
                    {"type": "text", "label": "Signature (Type Full Name)", "placeholder": "Full legal name as signature", "required": True},
                    {"type": "date", "label": "Date of Signing", "required": True},
                    {"type": "submit", "label": "Execute NDA 🔏", "color": "#0f172a"},
                ],
            },
            {
                "id": "sign_rental_agreement",
                "title": "Rental / Lease Agreement Form",
                "category": "sign_type",
                "description": "Formalise rental agreements between landlord and tenant with key terms and signatures.",
                "color": "#059669",
                "badge": "✍️ Sign",
                "tags": ["rental", "lease", "property", "sign template", "agreement"],
                "score": 85,
                "score_tip": "Add security deposit terms to prevent disputes",
                "suggestions": [
                    {"icon": "🏦", "title": "Add Deposit Terms", "text": "Specify refund conditions upfront.", "field": {"type": "textarea", "label": "Security Deposit Refund Terms", "placeholder": "Conditions under which deposit will be refunded...", "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "🏠 Rental Agreement"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Landlord Name", "placeholder": "Property owner name", "required": True},
                        {"type": "text", "label": "Tenant Name", "placeholder": "Tenant / lessee name", "required": True},
                    ]},
                    {"type": "textarea", "label": "Property Address", "placeholder": "Full property address with PIN code", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Lease Start Date", "required": True},
                        {"type": "date", "label": "Lease End Date", "required": True},
                    ]},
                    {"type": "number", "label": "Monthly Rent (₹)", "placeholder": "0.00", "required": True},
                    {"type": "number", "label": "Security Deposit (₹)", "placeholder": "0.00", "required": True},
                    {"type": "select", "label": "Rent Due Date", "options": ["1st of month", "5th of month", "10th of month", "15th of month"], "required": True},
                    {"type": "checkbox", "label": "Utilities included in rent", "options": ["Water", "Electricity", "Internet / Wi-Fi", "Gas", "Maintenance", "None"], "required": False},
                    {"type": "radio", "label": "Subletting Allowed?", "options": ["Yes, with landlord's written consent", "No subletting permitted"], "required": True},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Landlord Signature (Type Name)", "placeholder": "Landlord full name", "required": True},
                        {"type": "text", "label": "Tenant Signature (Type Name)", "placeholder": "Tenant full name", "required": True},
                    ]},
                    {"type": "submit", "label": "Sign Rental Agreement 🏠", "color": "#059669"},
                ],
            },
            {
                "id": "sign_consent_form",
                "title": "Parental / Medical Consent Form",
                "category": "sign_type",
                "description": "Collect informed consent from parents or patients before procedures or activities.",
                "color": "#0891b2",
                "badge": "✍️ Sign",
                "tags": ["consent", "medical", "parental", "sign template", "legal"],
                "score": 82,
                "score_tip": "Add emergency contact for safety compliance",
                "suggestions": [
                    {"icon": "🚨", "title": "Add Emergency Contact", "text": "Critical for medical / school activities.", "field": {"type": "row2", "fields": [{"type": "text", "label": "Emergency Contact Name", "placeholder": "Name", "required": True}, {"type": "phone", "label": "Emergency Phone", "placeholder": "+91 98765 43210", "required": True}]}},
                ],
                "fields": [
                    {"type": "section", "label": "📋 Consent Form"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Participant / Patient Name", "placeholder": "Full name", "required": True},
                        {"type": "date", "label": "Date of Birth", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Parent / Guardian Name (if minor)", "placeholder": "Guardian name", "required": False},
                        {"type": "phone", "label": "Contact Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Activity / Procedure", "placeholder": "What is consent being given for?", "required": True},
                    {"type": "textarea", "label": "Risks Disclosed / Understood", "placeholder": "I understand the following risks and potential outcomes...", "required": True},
                    {"type": "radio", "label": "Medical History — Any serious conditions?", "options": ["No serious medical conditions", "Yes (describe below)"], "required": True},
                    {"type": "textarea", "label": "Medical Conditions (if any)", "placeholder": "Describe conditions, medications, or allergies...", "required": False},
                    {"type": "radio", "label": "I give my informed consent voluntarily", "options": ["Yes, I consent", "No, I do not consent"], "required": True},
                    {"type": "text", "label": "Signature (Type Full Name)", "placeholder": "Full name as signature", "required": True},
                    {"type": "date", "label": "Date of Consent", "required": True},
                    {"type": "submit", "label": "Submit Signed Consent ✅", "color": "#0891b2"},
                ],
            },
            {
                "id": "sign_waiver",
                "title": "Liability Waiver Form",
                "category": "sign_type",
                "description": "Protect your business with a signed liability waiver before high-risk activities.",
                "color": "#dc2626",
                "badge": "✍️ Sign",
                "tags": ["waiver", "liability", "release", "sign template", "legal"],
                "score": 84,
                "score_tip": "Add photo ID capture for identity verification",
                "suggestions": [
                    {"icon": "🪪", "title": "Add ID Upload", "text": "Photo ID strengthens legal enforceability.", "field": {"type": "file", "label": "Upload Photo ID (Aadhaar / Passport)", "required": False}},
                ],
                "fields": [
                    {"type": "section", "label": "⚠️ Liability Waiver & Release"},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Participant Full Name", "placeholder": "Legal name", "required": True},
                        {"type": "date", "label": "Date of Birth", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "email", "label": "Email Address", "placeholder": "you@email.com", "required": True},
                        {"type": "phone", "label": "Phone", "placeholder": "+91 98765 43210", "required": True},
                    ]},
                    {"type": "text", "label": "Activity / Event", "placeholder": "Activity for which waiver applies", "required": True},
                    {"type": "date", "label": "Activity Date", "required": True},
                    {"type": "textarea", "label": "Risks Acknowledged", "placeholder": "I acknowledge the following inherent risks and dangers of this activity: ...", "required": True},
                    {"type": "radio", "label": "I voluntarily waive all claims against the organisation", "options": ["Yes, I waive all liability claims", "I do not agree to this waiver"], "required": True},
                    {"type": "radio", "label": "Photography / Media Release", "options": ["I consent to photos/videos being used", "I do not consent to media capture"], "required": True},
                    {"type": "text", "label": "Signature (Type Full Name)", "placeholder": "Legal signature — full name", "required": True},
                    {"type": "date", "label": "Date of Signing", "required": True},
                    {"type": "submit", "label": "Submit Signed Waiver 📝", "color": "#dc2626"},
                ],
            },

            # ── BOARD TEMPLATES ──────────────────────────────────────────────────
            {
                "id": "board_task_submit",
                "title": "Kanban Task Submission",
                "category": "board_type",
                "description": "Add tasks to your project board with title, description, assignee, and priority.",
                "color": "#4f46e5",
                "badge": "📌 Board",
                "tags": ["kanban", "task", "project", "board template", "agile"],
                "score": 75,
                "score_tip": "Add story points for sprint planning",
                "suggestions": [
                    {"icon": "🎯", "title": "Add Story Points", "text": "Essential for agile sprint planning.", "field": {"type": "select", "label": "Story Points", "options": ["1", "2", "3", "5", "8", "13", "21"], "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Task Title", "placeholder": "Short, action-oriented title", "required": True},
                    {"type": "textarea", "label": "Task Description", "placeholder": "What needs to be done? Include acceptance criteria...", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Status", "options": ["To Do", "In Progress", "In Review", "Done", "Blocked"], "required": True},
                        {"type": "select", "label": "Priority", "options": ["🔴 Critical", "🟠 High", "🟡 Medium", "🟢 Low"], "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Assignee", "placeholder": "Who is responsible?", "required": False},
                        {"type": "date", "label": "Due Date", "required": False},
                    ]},
                    {"type": "select", "label": "Sprint / Milestone", "options": ["Current Sprint", "Next Sprint", "Backlog", "Future"], "required": False},
                    {"type": "text", "label": "Labels / Tags", "placeholder": "e.g. frontend, bug, design, api", "required": False},
                    {"type": "submit", "label": "Add to Board 📌", "color": "#4f46e5"},
                ],
            },
            {
                "id": "board_bug_submit",
                "title": "Bug Board Entry",
                "category": "board_type",
                "description": "Log a bug to the development board with reproduction steps, severity, and assignment.",
                "color": "#dc2626",
                "badge": "📌 Board",
                "tags": ["bug", "issue", "board template", "dev", "qa"],
                "score": 80,
                "score_tip": "Add environment field to speed up reproduction",
                "suggestions": [
                    {"icon": "🌐", "title": "Add Environment", "text": "Staging vs production bugs need different fixes.", "field": {"type": "radio", "label": "Environment", "options": ["Production", "Staging / UAT", "Development / Local"], "required": True}},
                ],
                "fields": [
                    {"type": "text", "label": "Bug Title", "placeholder": "Short description, e.g. 'Login fails on Safari mobile'", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Severity", "options": ["🔴 Critical – App unusable", "🟠 High – Feature broken", "🟡 Medium – Workaround exists", "🟢 Low – Minor issue"], "required": True},
                        {"type": "select", "label": "Status", "options": ["Open", "In Progress", "In Review", "Fixed", "Won't Fix"], "required": True},
                    ]},
                    {"type": "textarea", "label": "Steps to Reproduce", "placeholder": "1. Go to...\n2. Click on...\n3. See error", "required": True},
                    {"type": "textarea", "label": "Expected vs Actual Behaviour", "placeholder": "Expected: ...\nActual: ...", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Browser / Platform", "options": ["Chrome", "Firefox", "Safari", "Edge", "Android App", "iOS App", "Other"], "required": False},
                        {"type": "text", "label": "Assigned Developer", "placeholder": "Who should fix this?", "required": False},
                    ]},
                    {"type": "file", "label": "Attach Screenshot / Recording", "required": False},
                    {"type": "submit", "label": "Log Bug 🐛", "color": "#dc2626"},
                ],
            },
            {
                "id": "board_sprint_story",
                "title": "Sprint Story / User Story Form",
                "category": "board_type",
                "description": "Create user stories in the standard 'As a user...' format for your sprint backlog.",
                "color": "#059669",
                "badge": "📌 Board",
                "tags": ["user story", "sprint", "agile", "board template", "scrum"],
                "score": 82,
                "score_tip": "Add definition of done for clear acceptance criteria",
                "suggestions": [
                    {"icon": "✅", "title": "Add Definition of Done", "text": "Prevents scope debates during review.", "field": {"type": "textarea", "label": "Definition of Done", "placeholder": "What does 'complete' look like for this story?", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Story Title", "placeholder": "Short title for the board card", "required": True},
                    {"type": "section", "label": "📖 User Story Format"},
                    {"type": "text", "label": "As a...", "placeholder": "user role (e.g. logged-in customer)", "required": True},
                    {"type": "text", "label": "I want to...", "placeholder": "goal / feature (e.g. reset my password)", "required": True},
                    {"type": "text", "label": "So that...", "placeholder": "benefit / reason (e.g. I can regain access)", "required": True},
                    {"type": "textarea", "label": "Acceptance Criteria", "placeholder": "Given / When / Then scenarios:\n\nGiven...\nWhen...\nThen...", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Story Points", "options": ["1", "2", "3", "5", "8", "13"], "required": True},
                        {"type": "select", "label": "Priority", "options": ["Must Have (P0)", "Should Have (P1)", "Could Have (P2)", "Won't Have (P3)"], "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Assigned To", "placeholder": "Developer / designer", "required": False},
                        {"type": "select", "label": "Sprint", "options": ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Backlog"], "required": True},
                    ]},
                    {"type": "submit", "label": "Add Story to Board 📝", "color": "#059669"},
                ],
            },
            {
                "id": "board_content_plan",
                "title": "Content Calendar Entry",
                "category": "board_type",
                "description": "Plan and track content pieces on a marketing board with channel, date, and status.",
                "color": "#db2777",
                "badge": "📌 Board",
                "tags": ["content", "calendar", "marketing", "board template", "social media"],
                "score": 76,
                "score_tip": "Add performance target for ROI tracking",
                "suggestions": [
                    {"icon": "🎯", "title": "Add Target KPI", "text": "Link content to goals for reporting.", "field": {"type": "text", "label": "Target KPI / Goal", "placeholder": "e.g. 500 clicks, 1000 impressions", "required": False}},
                ],
                "fields": [
                    {"type": "text", "label": "Content Title / Topic", "placeholder": "What is this content about?", "required": True},
                    {"type": "row2", "fields": [
                        {"type": "select", "label": "Content Type", "options": ["Blog Post", "Social Media Post", "Video", "Infographic", "Email Newsletter", "Podcast Episode", "Case Study", "Ad Campaign"], "required": True},
                        {"type": "select", "label": "Platform / Channel", "options": ["Website / Blog", "LinkedIn", "Instagram", "Twitter / X", "Facebook", "YouTube", "Email", "Multiple"], "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "date", "label": "Planned Publish Date", "required": True},
                        {"type": "select", "label": "Status", "options": ["Idea / Planned", "In Production", "Review / Editing", "Scheduled", "Published", "Cancelled"], "required": True},
                    ]},
                    {"type": "text", "label": "Content Creator / Owner", "placeholder": "Who is creating this?", "required": True},
                    {"type": "text", "label": "SEO Keywords / Hashtags", "placeholder": "Main keywords or hashtags", "required": False},
                    {"type": "textarea", "label": "Brief / Notes", "placeholder": "Key messages, tone, references, assets needed...", "required": False},
                    {"type": "submit", "label": "Add to Content Board 📅", "color": "#db2777"},
                ],
            },
            {
                "id": "board_deal_pipeline",
                "title": "Sales Deal / Pipeline Entry",
                "category": "board_type",
                "description": "Track sales deals through your pipeline with stage, value, and next action.",
                "color": "#f59e0b",
                "badge": "📌 Board",
                "tags": ["sales", "crm", "pipeline", "board template", "deal"],
                "score": 79,
                "score_tip": "Add win probability for revenue forecasting",
                "suggestions": [
                    {"icon": "📊", "title": "Add Win Probability", "text": "Key for sales forecasting and quotas.", "field": {"type": "select", "label": "Win Probability", "options": ["10% – Early Stage", "25% – Qualified", "50% – Proposal Sent", "75% – Negotiating", "90% – Verbal Commitment", "100% – Closed Won"], "required": False}},
                ],
                "fields": [
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Deal / Opportunity Name", "placeholder": "e.g. Acme Corp – CRM Implementation", "required": True},
                        {"type": "text", "label": "Company / Client", "placeholder": "Prospect company name", "required": True},
                    ]},
                    {"type": "row2", "fields": [
                        {"type": "text", "label": "Contact Person", "placeholder": "Decision maker name", "required": True},
                        {"type": "phone", "label": "Contact Phone", "placeholder": "+91 98765 43210", "required": False},
                    ]},
                    {"type": "email", "label": "Contact Email", "placeholder": "contact@company.com", "required": False},
                    {"type": "select", "label": "Pipeline Stage", "options": ["Lead / Enquiry", "Qualified", "Demo / Presentation", "Proposal Sent", "Negotiation", "Closed Won", "Closed Lost"], "required": True},
                    {"type": "number", "label": "Deal Value (₹)", "placeholder": "0.00", "required": True},
                    {"type": "date", "label": "Expected Close Date", "required": False},
                    {"type": "text", "label": "Assigned Sales Rep", "placeholder": "Who owns this deal?", "required": True},
                    {"type": "textarea", "label": "Next Action / Notes", "placeholder": "What is the next step? Any notes from last interaction?", "required": False},
                    {"type": "submit", "label": "Add Deal to Pipeline 💼", "color": "#f59e0b"},
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
    from sqlalchemy import text
    fc_models.Base.metadata.create_all(bind=fc_engine)
    auth_models.Base.metadata.create_all(bind=fc_engine)
    rag_models.Base.metadata.create_all(bind=fc_engine)
    integration_models.Base.metadata.create_all(bind=fc_engine)
    # Migration: add user_id column to custom_forms if it doesn't exist
    try:
        with fc_engine.connect() as conn:
            conn.execute(text("ALTER TABLE custom_forms ADD COLUMN user_id INTEGER"))
            conn.commit()
    except Exception:
        pass  # column already exists
    seed_templates()
    yield


app = FastAPI(title="FormCraft + QueryMind API", version="1.0.0", lifespan=lifespan)

_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "https://formcraft-app.onrender.com,http://localhost:3000,http://localhost:5173",
    ).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(formcraft_router)
app.include_router(querymind_router)
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(integrations_router)

# Serve React frontend (production)
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    _assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
