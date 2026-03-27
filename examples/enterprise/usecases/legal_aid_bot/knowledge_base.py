"""Legal rights knowledge base — structured legal information for Indian citizens."""

from __future__ import annotations

LEGAL_TOPICS: dict[str, dict[str, str]] = {
    "fir_filing": {
        "title": "How to File an FIR",
        "summary": (
            "An FIR (First Information Report) is a written document prepared by police "
            "when they receive information about a cognizable offence. Any person can file "
            "an FIR — the police cannot refuse under Section 154 of CrPC."
        ),
        "key_points": (
            "1. Go to the nearest police station — it does not have to be your local station.\n"
            "2. You can file the FIR verbally or in writing. The police must write it down.\n"
            "3. You have the right to receive a FREE copy of your FIR.\n"
            "4. For women-related offences, a female officer should record the FIR.\n"
            "5. Zero FIR: Any police station must accept your FIR and transfer it later.\n"
            "6. If police refuse, complain to the Superintendent of Police or a Magistrate."
        ),
        "related_laws": "CrPC Section 154, Section 155; IPC relevant sections",
    },
    "land_rights": {
        "title": "Land Rights & Property",
        "summary": (
            "Land records and property ownership in India are governed by state-specific laws. "
            "Common issues include boundary disputes, encroachment, and succession rights."
        ),
        "key_points": (
            "1. Always verify land ownership through official revenue records (7/12 extract, khata).\n"
            "2. Registration of sale deeds is mandatory under the Registration Act, 1908.\n"
            "3. Women have equal inheritance rights under the Hindu Succession (Amendment) Act, 2005.\n"
            "4. Tribal land cannot be transferred to non-tribals in Scheduled Areas.\n"
            "5. For disputes, approach the Tehsildar / Revenue Court first.\n"
            "6. Digitized land records are available through state Bhulekh/Bhoomi portals."
        ),
        "related_laws": "Transfer of Property Act 1882, Registration Act 1908, Hindu Succession Act",
    },
    "consumer_rights": {
        "title": "Consumer Rights & Complaints",
        "summary": (
            "The Consumer Protection Act, 2019 protects buyers against unfair trade practices, "
            "defective goods, and deficient services."
        ),
        "key_points": (
            "1. Six basic consumer rights: Safety, Information, Choice, Redressal, Hearing, Education.\n"
            "2. File complaints at the District Consumer Forum (up to ₹1 crore).\n"
            "3. E-filing available at https://edaakhil.nic.in.\n"
            "4. No lawyer needed — you can represent yourself.\n"
            "5. Complaints must be filed within 2 years of the cause of action.\n"
            "6. Consumer helpline: 1800-11-4000 (toll-free)."
        ),
        "related_laws": "Consumer Protection Act 2019, E-Commerce Rules 2020",
    },
    "domestic_violence": {
        "title": "Protection from Domestic Violence",
        "summary": (
            "The Protection of Women from Domestic Violence Act, 2005 provides civil remedies "
            "to women facing physical, emotional, sexual, or economic abuse."
        ),
        "key_points": (
            "1. Domestic violence includes physical, emotional, verbal, sexual, and economic abuse.\n"
            "2. Any woman — wife, live-in partner, sister, mother — can seek protection.\n"
            "3. Protection Officers in every district help file applications.\n"
            "4. Courts can issue Protection Orders, Residence Orders, and Monetary Relief.\n"
            "5. Women's helpline: 181 (toll-free), Police: 100.\n"
            "6. Filing is free — no court fee required."
        ),
        "related_laws": "PWDVA 2005, IPC Section 498A, Dowry Prohibition Act 1961",
    },
    "labour_rights": {
        "title": "Worker and Labour Rights",
        "summary": (
            "Indian labour laws protect workers' rights to fair wages, safe working conditions, "
            "and social security."
        ),
        "key_points": (
            "1. Minimum wages are state-specific — employers cannot pay below the notified rate.\n"
            "2. Working hours: max 48 hours/week; overtime must be paid at double the rate.\n"
            "3. EPFO (PF) is mandatory for establishments with 20+ employees.\n"
            "4. ESI provides medical care for workers earning up to ₹21,000/month.\n"
            "5. Contract workers have equal rights to basic amenities.\n"
            "6. Complaints: Labour Commissioner's office or eSHRAM portal."
        ),
        "related_laws": "Code on Wages 2019, EPFO Act 1952, ESIC Act 1948",
    },
}


def get_topic_names() -> list[str]:
    return list(LEGAL_TOPICS.keys())


def get_topic(topic_key: str) -> dict[str, str] | None:
    return LEGAL_TOPICS.get(topic_key)


def format_topic_for_prompt(topic_key: str) -> str:
    """Format a legal topic as context for the LLM."""
    topic = LEGAL_TOPICS.get(topic_key)
    if not topic:
        return ""
    return (
        f"TOPIC: {topic['title']}\n"
        f"SUMMARY: {topic['summary']}\n"
        f"KEY POINTS:\n{topic['key_points']}\n"
        f"RELATED LAWS: {topic['related_laws']}"
    )
