"""Pre-built IT knowledge base with common issue resolutions."""

from __future__ import annotations

KNOWLEDGE_BASE: list[dict] = [
    # ── Network & Connectivity ────────────────────────────────────────────────
    {
        "id": "NET-001",
        "category": "Network & Connectivity",
        "title": "VPN connection fails or disconnects",
        "keywords": ["vpn", "connect", "remote", "office network", "tunnel"],
        "solution": (
            "1. Verify your internet connection is working by opening any website.\n"
            "2. Restart the VPN client (close completely, reopen).\n"
            "3. Disconnect and reconnect — wait 30 seconds between attempts.\n"
            "4. Try a different VPN server/gateway if multiple are available.\n"
            "5. Disable your firewall/antivirus temporarily and retry.\n"
            "6. Restart your computer, then retry VPN.\n"
            "7. If an error code appears, note it and raise an IT ticket."
        ),
        "escalate_if": "Error code persists or all gateways fail.",
    },
    {
        "id": "NET-002",
        "category": "Network & Connectivity",
        "title": "Cannot connect to Wi-Fi",
        "keywords": ["wifi", "wi-fi", "wireless", "no signal", "ssid"],
        "solution": (
            "1. Turn Wi-Fi off and on from system tray or settings.\n"
            "2. Forget the network and reconnect: Settings → Wi-Fi → [Network] → Forget.\n"
            "3. Restart your laptop — Wi-Fi adapter resets on boot.\n"
            "4. Check if others nearby are connected (could be AP issue).\n"
            "5. Update the Wi-Fi driver: Device Manager → Network Adapters → Update.\n"
            "6. Run the Windows network troubleshooter: Settings → System → Troubleshoot."
        ),
        "escalate_if": "Multiple users affected in the same area.",
    },
    {
        "id": "NET-003",
        "category": "Network & Connectivity",
        "title": "Slow internet or high latency",
        "keywords": ["slow", "speed", "latency", "buffering", "lag", "bandwidth"],
        "solution": (
            "1. Run a speed test at fast.com to measure actual bandwidth.\n"
            "2. Close unused browser tabs, streaming apps, and large downloads.\n"
            "3. Disconnect from VPN temporarily (VPN adds overhead).\n"
            "4. Move closer to the Wi-Fi access point or use an ethernet cable.\n"
            "5. Restart your router/switch if you have access.\n"
            "6. Check for background Windows updates consuming bandwidth."
        ),
        "escalate_if": "Speed is below 5 Mbps consistently or issue affects the whole office.",
    },
    {
        "id": "NET-004",
        "category": "Network & Connectivity",
        "title": "Cannot access a specific website or internal portal",
        "keywords": ["website", "portal", "blocked", "dns", "cannot open", "access denied"],
        "solution": (
            "1. Check if the site is blocked by opening it on mobile data.\n"
            "2. Clear browser cache: Ctrl+Shift+Delete → Clear all.\n"
            "3. Try a different browser (Chrome, Edge, Firefox).\n"
            "4. Flush DNS: open Command Prompt → type 'ipconfig /flushdns'.\n"
            "5. Disable browser extensions temporarily.\n"
            "6. Check if the URL is correct and the site is not down globally."
        ),
        "escalate_if": "Internal company portal unreachable — may need proxy/firewall rule update.",
    },
    # ── Hardware ─────────────────────────────────────────────────────────────
    {
        "id": "HW-001",
        "category": "Hardware",
        "title": "Laptop will not turn on",
        "keywords": ["turn on", "power", "boot", "black screen", "won't start", "dead"],
        "solution": (
            "1. Hold power button for 10 seconds to force shutdown, then press again.\n"
            "2. Remove the power cable, hold power for 15 seconds, reconnect and try.\n"
            "3. Check the charging indicator light — ensure the battery is charging.\n"
            "4. Try a different power outlet or cable.\n"
            "5. Connect an external monitor to rule out display failure.\n"
            "6. If the laptop has a removable battery, reseat it."
        ),
        "escalate_if": "Laptop still does not power on — hardware fault suspected.",
    },
    {
        "id": "HW-002",
        "category": "Hardware",
        "title": "Printer not working or offline",
        "keywords": ["printer", "print", "offline", "stuck", "queue", "paper jam"],
        "solution": (
            "1. Check printer is powered on and shows 'Ready' on its display.\n"
            "2. Clear any paper jams — open all trays and check for obstructions.\n"
            "3. On Windows: Settings → Printers → right-click printer → 'See what's printing' → cancel all jobs.\n"
            "4. Right-click printer → 'Set as Default Printer'.\n"
            "5. Restart the Print Spooler: Services → Print Spooler → Restart.\n"
            "6. Remove and re-add the printer: Settings → Printers → Add a printer.\n"
            "7. Reinstall printer driver from the manufacturer's website."
        ),
        "escalate_if": "Printer hardware error code displayed or driver reinstall fails.",
    },
    {
        "id": "HW-003",
        "category": "Hardware",
        "title": "External monitor not detected",
        "keywords": ["monitor", "display", "screen", "hdmi", "not detected", "second screen"],
        "solution": (
            "1. Press Windows + P and select 'Extend' or 'Duplicate'.\n"
            "2. Disconnect and reconnect the HDMI/DisplayPort cable.\n"
            "3. Try a different cable or port.\n"
            "4. Right-click desktop → Display Settings → Detect.\n"
            "5. Update graphics driver: Device Manager → Display Adapters → Update.\n"
            "6. Restart the laptop with the monitor already connected."
        ),
        "escalate_if": "Cable and driver updates do not resolve — hardware port may be faulty.",
    },
    {
        "id": "HW-004",
        "category": "Hardware",
        "title": "Keyboard or mouse not working",
        "keywords": ["keyboard", "mouse", "typing", "cursor", "not responding", "bluetooth"],
        "solution": (
            "1. For USB devices: unplug and replug into a different USB port.\n"
            "2. For wireless/Bluetooth: turn off and on, re-pair the device.\n"
            "3. Try the device on another computer to confirm if it is faulty.\n"
            "4. Update drivers: Device Manager → Human Interface Devices → Update.\n"
            "5. For laptop keyboard: press Fn + NumLock to toggle keyboard mode.\n"
            "6. Restart the computer."
        ),
        "escalate_if": "Device confirmed working on another PC but not this one.",
    },
    # ── Software & Applications ───────────────────────────────────────────────
    {
        "id": "SW-001",
        "category": "Software & Applications",
        "title": "Microsoft Office crashes or does not open",
        "keywords": ["office", "word", "excel", "powerpoint", "crash", "not opening", "freezes"],
        "solution": (
            "1. Close all Office apps → open Task Manager (Ctrl+Shift+Esc) → end any WINWORD/EXCEL tasks.\n"
            "2. Open the application in Safe Mode: hold Ctrl while clicking the app icon.\n"
            "3. Disable add-ins: File → Options → Add-ins → Manage COM Add-ins → uncheck all.\n"
            "4. Repair Office: Control Panel → Programs → Microsoft 365 → Change → Quick Repair.\n"
            "5. Check for Office updates: any Office app → File → Account → Update Options → Update Now.\n"
            "6. Delete Office cache: %localappdata%\\Microsoft\\Office\\16.0\\OfficeFileCache"
        ),
        "escalate_if": "Quick Repair and Safe Mode both fail — online repair or reinstall needed.",
    },
    {
        "id": "SW-002",
        "category": "Software & Applications",
        "title": "Browser is slow, crashing, or not loading pages",
        "keywords": ["browser", "chrome", "edge", "firefox", "slow", "crash", "pages"],
        "solution": (
            "1. Clear cache and cookies: Ctrl+Shift+Delete → Clear all time → Clear data.\n"
            "2. Disable extensions: Settings → Extensions → turn off all, then re-enable one by one.\n"
            "3. Open a new Incognito/InPrivate window (Ctrl+Shift+N) — if it works, an extension is the issue.\n"
            "4. Update the browser to the latest version.\n"
            "5. Reset browser settings: Settings → Reset settings → Restore defaults.\n"
            "6. Try a different browser to isolate if it's browser-specific."
        ),
        "escalate_if": "All browsers fail — likely a network or OS-level issue.",
    },
    {
        "id": "SW-003",
        "category": "Software & Applications",
        "title": "Cannot install software or application",
        "keywords": ["install", "software", "application", "setup", "admin", "permission denied"],
        "solution": (
            "1. Check if you have admin rights: right-click installer → 'Run as Administrator'.\n"
            "2. Temporarily disable antivirus during installation.\n"
            "3. Ensure enough disk space: open File Explorer → C: drive → check free space (need >5 GB).\n"
            "4. Download the installer again — previous download may be corrupt.\n"
            "5. Check Windows Event Viewer for installation error codes."
        ),
        "escalate_if": "Software requires IT-approved admin credentials for installation.",
    },
    {
        "id": "SW-004",
        "category": "Software & Applications",
        "title": "Windows update stuck or failing",
        "keywords": ["windows update", "update", "stuck", "failed", "0x", "error"],
        "solution": (
            "1. Restart your computer and let it complete any pending updates.\n"
            "2. Run Windows Update Troubleshooter: Settings → System → Troubleshoot → Windows Update.\n"
            "3. Clear update cache: stop Windows Update service → delete C:\\Windows\\SoftwareDistribution → restart service.\n"
            "4. Note the error code (e.g., 0x80070002) and search Microsoft support for it.\n"
            "5. Run 'sfc /scannow' in Command Prompt (as Administrator) to fix system files."
        ),
        "escalate_if": "Update fails repeatedly with error code — may need IT to push update remotely.",
    },
    # ── Security & Access ─────────────────────────────────────────────────────
    {
        "id": "SEC-001",
        "category": "Security & Access",
        "title": "Account locked out",
        "keywords": ["locked out", "account locked", "cannot login", "too many attempts", "locked"],
        "solution": (
            "1. Wait 15–30 minutes — most accounts auto-unlock after a cooldown.\n"
            "2. Use the self-service password reset portal (check company intranet for the link).\n"
            "3. Contact your IT helpdesk by phone — they can unlock the account immediately.\n"
            "4. After unlock, change your password to something new.\n"
            "5. Check all devices (phone, tablet) for saved wrong passwords causing repeated lockouts."
        ),
        "escalate_if": "Account unlocks but locks again immediately — possible security incident.",
    },
    {
        "id": "SEC-002",
        "category": "Security & Access",
        "title": "Password reset required",
        "keywords": ["password", "reset", "forgot", "expired", "change password"],
        "solution": (
            "1. Press Ctrl+Alt+Delete → 'Change a password' (when logged in).\n"
            "2. Use the self-service password reset portal on your company intranet.\n"
            "3. Password requirements: min. 12 characters, uppercase, lowercase, number, and symbol.\n"
            "4. Do not reuse your last 10 passwords.\n"
            "5. After reset, update the password on your phone/tablet email accounts."
        ),
        "escalate_if": "Self-service portal is not working or you do not have access to your registered email.",
    },
    {
        "id": "SEC-003",
        "category": "Security & Access",
        "title": "Suspected phishing email received",
        "keywords": ["phishing", "suspicious email", "scam", "clicked link", "fake email"],
        "solution": (
            "⚠️ IMPORTANT — Treat this as a potential security incident.\n"
            "1. Do NOT click any links or download attachments in the email.\n"
            "2. Do NOT reply to the sender.\n"
            "3. Forward the email to your IT Security team (check intranet for the address).\n"
            "4. If you already clicked a link: disconnect from the network immediately and call IT.\n"
            "5. Report the email as phishing in Outlook: Report Message → Phishing.\n"
            "6. Change your password immediately if you entered credentials."
        ),
        "escalate_if": "Always escalate phishing incidents — IT Security must investigate.",
    },
    {
        "id": "SEC-004",
        "category": "Security & Access",
        "title": "Multi-factor authentication (MFA) not working",
        "keywords": ["mfa", "two factor", "2fa", "authenticator", "otp", "code", "microsoft authenticator"],
        "solution": (
            "1. Ensure your phone's date and time are set to 'Automatic'.\n"
            "2. Open the Authenticator app → tap the three dots → Refresh codes.\n"
            "3. If you have a new phone, use backup codes from when you set up MFA.\n"
            "4. Try the 'I can't use my authenticator app' option on the login screen.\n"
            "5. Contact IT helpdesk — they can temporarily disable MFA for one login."
        ),
        "escalate_if": "Lost access to authenticator app with no backup — IT must verify identity in person.",
    },
    # ── Email & Collaboration ─────────────────────────────────────────────────
    {
        "id": "COL-001",
        "category": "Email & Collaboration",
        "title": "Outlook not syncing or emails not loading",
        "keywords": ["outlook", "email", "sync", "not loading", "stuck", "offline"],
        "solution": (
            "1. Check connection status at the bottom of Outlook — should say 'Connected to: Microsoft Exchange'.\n"
            "2. Click Send/Receive → Send/Receive All Folders (F9).\n"
            "3. If 'Disconnected': File → Account Settings → Email → Repair.\n"
            "4. Restart Outlook.\n"
            "5. Check your mailbox is not full: File → Mailbox Settings → view size.\n"
            "6. Try Outlook Web (outlook.office.com) — if it works, the issue is with the desktop app."
        ),
        "escalate_if": "Outlook Web also fails — Exchange server issue requiring IT intervention.",
    },
    {
        "id": "COL-002",
        "category": "Email & Collaboration",
        "title": "Microsoft Teams audio or video issues in meetings",
        "keywords": ["teams", "audio", "video", "microphone", "camera", "meeting", "no sound"],
        "solution": (
            "1. In Teams: click profile picture → Settings → Devices — verify correct mic/speaker/camera selected.\n"
            "2. Check Windows sound settings: right-click speaker icon → Sound Settings → Input/Output devices.\n"
            "3. Join the meeting → use 'Test call' option to verify audio before the actual meeting.\n"
            "4. Quit and rejoin the meeting — this refreshes the media session.\n"
            "5. Check if other apps (Zoom, browser) are using the microphone simultaneously.\n"
            "6. Update Teams: profile picture → Check for updates."
        ),
        "escalate_if": "Hardware confirmed working in other apps but not in Teams — may need Teams reinstall.",
    },
    {
        "id": "COL-003",
        "category": "Email & Collaboration",
        "title": "Cannot access SharePoint files or shared drive",
        "keywords": ["sharepoint", "shared drive", "files", "access denied", "cannot open", "permissions"],
        "solution": (
            "1. Confirm you are logged in with your work account (check top-right corner).\n"
            "2. Clear browser cache and try again in an Incognito window.\n"
            "3. Ask your manager or the file owner to verify your permissions on the shared folder.\n"
            "4. Try accessing via the SharePoint web URL directly.\n"
            "5. For mapped network drives: disconnect and remap — right-click 'This PC' → Map network drive."
        ),
        "escalate_if": "Permission change required — must be approved by file owner and IT.",
    },
    {
        "id": "COL-004",
        "category": "Email & Collaboration",
        "title": "Cannot join or schedule a Zoom meeting",
        "keywords": ["zoom", "join", "meeting", "schedule", "link", "not working"],
        "solution": (
            "1. Update Zoom to the latest version: zoom.us/download.\n"
            "2. If link does not open: copy the Meeting ID and Password → open Zoom → Join Meeting → enter ID.\n"
            "3. Check firewall is not blocking Zoom (ports 80, 443, 8801–8802).\n"
            "4. Sign out of Zoom and sign back in with your work email.\n"
            "5. Try Zoom Web (zoom.us/join) as a fallback — no app needed."
        ),
        "escalate_if": "Zoom blocked by company firewall — IT must add an exception.",
    },
    # ── Other ─────────────────────────────────────────────────────────────────
    {
        "id": "OTH-001",
        "category": "Other",
        "title": "Computer is very slow or freezing",
        "keywords": ["slow", "freezing", "hanging", "performance", "unresponsive", "laggy"],
        "solution": (
            "1. Open Task Manager (Ctrl+Shift+Esc) → check CPU, Memory, Disk usage.\n"
            "2. Close unused applications and browser tabs.\n"
            "3. Restart your computer — clears memory and pending processes.\n"
            "4. Check disk space: need at least 15% free on C: drive.\n"
            "5. Run Disk Cleanup: search 'Disk Cleanup' in Start menu.\n"
            "6. Check for malware: run a Windows Defender Quick Scan.\n"
            "7. Disable startup programs: Task Manager → Startup → disable non-essential items."
        ),
        "escalate_if": "RAM or SSD hardware failure suspected — performance persists after cleanup.",
    },
    {
        "id": "OTH-002",
        "category": "Other",
        "title": "Need software or tool not installed on my device",
        "keywords": ["request software", "need application", "install request", "new tool"],
        "solution": (
            "1. Check the company software catalog on the intranet — many tools are pre-approved.\n"
            "2. Raise a software request ticket with: software name, version, business justification.\n"
            "3. Get manager approval — IT will require it before installation.\n"
            "4. IT will deploy approved software via the endpoint management system (typically within 2 business days)."
        ),
        "escalate_if": "Always raise a formal request — unauthorized software installs are a security risk.",
    },
]


class ITKnowledgeBase:
    """Search and retrieve solutions from the pre-built IT knowledge base."""

    def __init__(self):
        self._entries = KNOWLEDGE_BASE

    def search(self, query: str, max_results: int = 3) -> list[dict]:
        """Return up to max_results entries whose keywords match the query.

        Scoring: 2 points per keyword hit in title, 1 point per hit in keywords list.
        """
        query_lower = query.lower()
        scored: list[tuple[int, dict]] = []

        for entry in self._entries:
            score = 0
            for kw in entry["keywords"]:
                if kw in query_lower:
                    score += 1
            if any(word in entry["title"].lower() for word in query_lower.split()):
                score += 2
            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:max_results]]

    def get_all_categories(self) -> list[str]:
        """Return all unique categories in the knowledge base."""
        seen: set[str] = set()
        categories: list[str] = []
        for entry in self._entries:
            cat = entry["category"]
            if cat not in seen:
                seen.add(cat)
                categories.append(cat)
        return categories

    def get_by_category(self, category: str) -> list[dict]:
        """Return all entries for the given category."""
        return [e for e in self._entries if e["category"] == category]

    def get_by_id(self, article_id: str) -> dict | None:
        """Return a single KB entry by its ID, or None if not found."""
        for entry in self._entries:
            if entry["id"] == article_id:
                return entry
        return None
