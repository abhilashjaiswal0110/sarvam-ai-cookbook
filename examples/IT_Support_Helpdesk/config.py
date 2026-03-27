"""Configuration constants for the IT Support Helpdesk application."""

SARVAM_BASE_URL = "https://api.sarvam.ai"
SARVAM_CHAT_URL = "https://api.sarvam.ai/v1"
CHAT_MODEL = "sarvam-m"

SUPPORTED_LANGUAGES = {
    "en-IN": "English",
    "hi-IN": "Hindi (हिंदी)",
    "bn-IN": "Bengali (বাংলা)",
    "ta-IN": "Tamil (தமிழ்)",
    "te-IN": "Telugu (తెలుగు)",
    "mr-IN": "Marathi (मराठी)",
    "gu-IN": "Gujarati (ગુજરાતી)",
    "kn-IN": "Kannada (ಕನ್ನಡ)",
    "ml-IN": "Malayalam (മലയാളം)",
    "pa-IN": "Punjabi (ਪੰਜਾਬੀ)",
    "od-IN": "Odia (ଓଡ଼ିଆ)",
}

ISSUE_CATEGORIES = [
    "Network & Connectivity",
    "Hardware",
    "Software & Applications",
    "Security & Access",
    "Email & Collaboration",
    "Other",
]

PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]
TICKET_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

# Keywords used to auto-assign ticket priority
CRITICAL_KEYWORDS = [
    "ransomware", "virus", "malware", "data breach", "hacked", "security incident",
    "server down", "production down", "complete outage", "data loss", "stolen",
]
HIGH_KEYWORDS = [
    "cannot work", "all users affected", "urgent", "deadline", "client meeting",
    "presentation", "locked out", "cannot access", "entire team", "blocked",
]
LOW_KEYWORDS = [
    "slow", "minor", "cosmetic", "nice to have", "when possible", "not urgent",
]

SYSTEM_PROMPT = """You are HelpDesk AI, an expert IT support specialist for a large enterprise.
Your role is to help employees resolve technical issues quickly and professionally.

You have expertise in:
- Network & Connectivity: VPN, Wi-Fi, internet, DNS, proxy issues
- Hardware: laptops, printers, monitors, keyboards, USB devices
- Software & Applications: Microsoft Office, browsers, OS, drivers, installations
- Security & Access: account lockouts, password resets, MFA, phishing, permissions
- Email & Collaboration: Outlook, Microsoft Teams, Zoom, SharePoint

When a user reports an issue:
1. Acknowledge their problem with empathy
2. Identify the issue category and assess urgency
3. Provide clear, numbered, step-by-step troubleshooting instructions
4. Indicate if the issue requires escalation to human IT support
5. Suggest creating a support ticket if the issue cannot be resolved immediately

Format your response as:
**Category:** [category]
**Priority:** [Critical/High/Medium/Low]
**Steps to resolve:**
1. [step]
2. [step]
...
**Escalation needed:** [Yes/No — reason]

Always respond in the same language the user writes in. Keep responses concise but complete."""

TTS_SPEAKER = "meera"
TTS_MODEL = "bulbul:v2"
import os as _os
TICKETS_FILE = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "tickets.json")
MAX_CHAT_HISTORY = 10
