"""Ticket management with JSON-file persistence."""

from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from typing import Optional

from config import TICKET_STATUSES, PRIORITY_LEVELS, ISSUE_CATEGORIES, TICKETS_FILE


class TicketNotFoundError(Exception):
    """Raised when a ticket ID does not exist."""


class TicketManager:
    """CRUD operations for IT support tickets backed by a local JSON file.

    Args:
        storage_path: Path to the JSON file used for persistence.
            Defaults to TICKETS_FILE from config.
    """

    def __init__(self, storage_path: str = TICKETS_FILE):
        self._path = storage_path
        self._logger = logging.getLogger(__name__)
        self._tickets: dict[str, dict] = self._load()

    # ── Persistence helpers ─────────────────────────────────────────────────

    def _load(self) -> dict[str, dict]:
        if os.path.exists(self._path):
            try:
                with open(self._path, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                backup = self._path + ".corrupt"
                try:
                    os.replace(self._path, backup)
                    self._logger.warning(
                        "Tickets file corrupt — backed up to %s: %s", backup, exc
                    )
                except OSError:
                    self._logger.error("Tickets file corrupt and backup failed: %s", exc)
                return {}
        return {}

    def _save(self) -> None:
        dir_name = os.path.dirname(self._path) or "."
        fd, tmp = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._tickets, f, ensure_ascii=False, indent=2)
            try:
                os.replace(tmp, self._path)
            except PermissionError:
                # On Windows, os.replace may fail with locked files;
                # fall back to a direct overwrite.
                with open(self._path, "w", encoding="utf-8") as f:
                    json.dump(self._tickets, f, ensure_ascii=False, indent=2)
                os.unlink(tmp)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    # ── Public API ──────────────────────────────────────────────────────────

    def create(
        self,
        title: str,
        description: str,
        category: str,
        priority: str,
        user_name: str,
        user_language: str = "en-IN",
        resolution_notes: str = "",
    ) -> dict:
        """Create a new ticket and persist it.

        Args:
            title: Short summary of the issue.
            description: Full description of the issue.
            category: One of ISSUE_CATEGORIES.
            priority: One of PRIORITY_LEVELS.
            user_name: Name of the person reporting the issue.
            user_language: Language code of the reporter.
            resolution_notes: Optional AI-suggested resolution steps.

        Returns:
            The created ticket dict.
        """
        if category not in ISSUE_CATEGORIES:
            category = "Other"
        if priority not in PRIORITY_LEVELS:
            priority = "Medium"

        ticket_id = "TKT-" + uuid.uuid4().hex[:8].upper()
        now = datetime.now(timezone.utc).isoformat()
        ticket = {
            "id": ticket_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": "Open",
            "user_name": user_name,
            "user_language": user_language,
            "resolution_notes": resolution_notes,
            "created_at": now,
            "updated_at": now,
        }
        self._tickets[ticket_id] = ticket
        self._save()
        return ticket

    def get(self, ticket_id: str) -> dict:
        """Return a ticket by ID.

        Raises:
            TicketNotFoundError: if the ID does not exist.
        """
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(f"Ticket {ticket_id!r} not found.")
        return ticket

    def update_status(self, ticket_id: str, status: str) -> dict:
        """Update the status of an existing ticket.

        Args:
            ticket_id: The ticket to update.
            status: New status — must be one of TICKET_STATUSES.

        Returns:
            The updated ticket dict.

        Raises:
            TicketNotFoundError: if the ID does not exist.
            ValueError: if the status is invalid.
        """
        if status not in TICKET_STATUSES:
            raise ValueError(f"Invalid status {status!r}. Must be one of {TICKET_STATUSES}.")
        ticket = self.get(ticket_id)
        ticket["status"] = status
        ticket["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return ticket

    def update_resolution(self, ticket_id: str, notes: str) -> dict:
        """Append or replace resolution notes on a ticket."""
        ticket = self.get(ticket_id)
        ticket["resolution_notes"] = notes
        ticket["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
        return ticket

    def list_all(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> list[dict]:
        """Return tickets, optionally filtered by status, category, or priority.

        Results are sorted newest-first by created_at.
        """
        tickets = list(self._tickets.values())
        if status:
            tickets = [t for t in tickets if t["status"] == status]
        if category:
            tickets = [t for t in tickets if t["category"] == category]
        if priority:
            tickets = [t for t in tickets if t["priority"] == priority]
        return sorted(tickets, key=lambda t: t["created_at"], reverse=True)

    def stats(self) -> dict:
        """Return aggregate counts by status, category, and priority."""
        all_tickets = list(self._tickets.values())
        total = len(all_tickets)

        by_status = {s: 0 for s in TICKET_STATUSES}
        by_category = {c: 0 for c in ISSUE_CATEGORIES}
        by_priority = {p: 0 for p in PRIORITY_LEVELS}

        for t in all_tickets:
            by_status[t.get("status", "Open")] = by_status.get(t.get("status", "Open"), 0) + 1
            cat = t.get("category", "Other")
            by_category[cat] = by_category.get(cat, 0) + 1
            pri = t.get("priority", "Medium")
            by_priority[pri] = by_priority.get(pri, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
            "by_priority": by_priority,
        }
