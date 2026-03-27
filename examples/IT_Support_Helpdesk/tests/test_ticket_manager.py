"""Unit tests for TicketManager — uses a temporary JSON file."""

import sys
import os
import json

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ticket_manager import TicketManager, TicketNotFoundError
from config import TICKET_STATUSES, PRIORITY_LEVELS


@pytest.fixture
def tmp_path_file(tmp_path):
    """Return a path inside pytest's tmp_path that does not exist yet."""
    return str(tmp_path / "test_tickets.json")


@pytest.fixture
def manager(tmp_path_file):
    return TicketManager(storage_path=tmp_path_file)


@pytest.fixture
def sample_ticket(manager):
    return manager.create(
        title="Cannot connect to VPN",
        description="VPN shows error 800 when connecting from home.",
        category="Network & Connectivity",
        priority="High",
        user_name="Aisha Sharma",
        user_language="en-IN",
        resolution_notes="Restart the VPN client and retry.",
    )


# ── create ───────────────────────────────────────────────────────────────────

class TestCreate:
    def test_returns_ticket_dict(self, manager):
        ticket = manager.create(
            title="Printer offline",
            description="Printer shows offline status.",
            category="Hardware",
            priority="Medium",
            user_name="Ravi Kumar",
        )
        assert isinstance(ticket, dict)
        assert ticket["title"] == "Printer offline"

    def test_ticket_has_required_fields(self, manager, sample_ticket):
        for field in ["id", "title", "description", "category", "priority",
                      "status", "user_name", "user_language", "created_at", "updated_at"]:
            assert field in sample_ticket, f"Missing field: {field}"

    def test_id_has_tkt_prefix(self, manager, sample_ticket):
        assert sample_ticket["id"].startswith("TKT-")

    def test_initial_status_is_open(self, manager, sample_ticket):
        assert sample_ticket["status"] == "Open"

    def test_two_tickets_have_different_ids(self, manager):
        t1 = manager.create("Issue 1", "desc", "Hardware", "Low", "User A")
        t2 = manager.create("Issue 2", "desc", "Hardware", "Low", "User B")
        assert t1["id"] != t2["id"]

    def test_invalid_category_defaults_to_other(self, manager):
        ticket = manager.create("issue", "desc", category="Invalid Category", priority="Low", user_name="X")
        assert ticket["category"] == "Other"

    def test_invalid_priority_defaults_to_medium(self, manager):
        ticket = manager.create("issue", "desc", category="Hardware", priority="SuperUrgent", user_name="X")
        assert ticket["priority"] == "Medium"

    def test_ticket_persisted_to_file(self, manager, tmp_path_file, sample_ticket):
        with open(tmp_path_file) as f:
            data = json.load(f)
        assert sample_ticket["id"] in data


# ── get ──────────────────────────────────────────────────────────────────────

class TestGet:
    def test_retrieves_existing_ticket(self, manager, sample_ticket):
        fetched = manager.get(sample_ticket["id"])
        assert fetched["id"] == sample_ticket["id"]
        assert fetched["title"] == sample_ticket["title"]

    def test_raises_for_nonexistent_id(self, manager):
        with pytest.raises(TicketNotFoundError):
            manager.get("TKT-DOESNOTEXIST")


# ── update_status ─────────────────────────────────────────────────────────────

class TestUpdateStatus:
    def test_status_updated_successfully(self, manager, sample_ticket):
        updated = manager.update_status(sample_ticket["id"], "In Progress")
        assert updated["status"] == "In Progress"

    def test_all_valid_statuses_accepted(self, manager, sample_ticket):
        for status in TICKET_STATUSES:
            updated = manager.update_status(sample_ticket["id"], status)
            assert updated["status"] == status

    def test_raises_for_invalid_status(self, manager, sample_ticket):
        with pytest.raises(ValueError):
            manager.update_status(sample_ticket["id"], "Pending Approval")

    def test_raises_for_nonexistent_ticket(self, manager):
        with pytest.raises(TicketNotFoundError):
            manager.update_status("TKT-GHOST", "Closed")

    def test_updated_at_changes_after_status_update(self, manager, sample_ticket):
        original_updated_at = sample_ticket["updated_at"]
        import time; time.sleep(0.01)
        updated = manager.update_status(sample_ticket["id"], "Resolved")
        assert updated["updated_at"] >= original_updated_at

    def test_update_persisted_to_file(self, manager, tmp_path_file, sample_ticket):
        manager.update_status(sample_ticket["id"], "Closed")
        with open(tmp_path_file) as f:
            data = json.load(f)
        assert data[sample_ticket["id"]]["status"] == "Closed"


# ── update_resolution ─────────────────────────────────────────────────────────

class TestUpdateResolution:
    def test_resolution_notes_updated(self, manager, sample_ticket):
        updated = manager.update_resolution(sample_ticket["id"], "Issue resolved by restarting VPN.")
        assert updated["resolution_notes"] == "Issue resolved by restarting VPN."


# ── list_all ──────────────────────────────────────────────────────────────────

class TestListAll:
    def test_returns_all_tickets_when_no_filter(self, manager):
        manager.create("T1", "d", "Hardware", "Low", "U1")
        manager.create("T2", "d", "Network & Connectivity", "High", "U2")
        assert len(manager.list_all()) == 2

    def test_filter_by_status(self, manager, sample_ticket):
        manager.update_status(sample_ticket["id"], "Resolved")
        manager.create("Open ticket", "d", "Hardware", "Low", "U1")
        resolved = manager.list_all(status="Resolved")
        assert all(t["status"] == "Resolved" for t in resolved)
        assert len(resolved) == 1

    def test_filter_by_category(self, manager):
        manager.create("Net issue", "d", "Network & Connectivity", "Low", "U1")
        manager.create("HW issue", "d", "Hardware", "Low", "U2")
        net_tickets = manager.list_all(category="Network & Connectivity")
        assert all(t["category"] == "Network & Connectivity" for t in net_tickets)

    def test_filter_by_priority(self, manager):
        manager.create("Critical issue", "d", "Security & Access", "Critical", "U1")
        manager.create("Low issue", "d", "Other", "Low", "U2")
        critical = manager.list_all(priority="Critical")
        assert len(critical) == 1
        assert critical[0]["priority"] == "Critical"

    def test_sorted_newest_first(self, manager):
        import time
        manager.create("First", "d", "Other", "Low", "U1")
        time.sleep(0.01)
        manager.create("Second", "d", "Other", "Low", "U2")
        results = manager.list_all()
        assert results[0]["title"] == "Second"

    def test_returns_empty_list_when_no_tickets(self, manager):
        assert manager.list_all() == []


# ── stats ─────────────────────────────────────────────────────────────────────

class TestStats:
    def test_empty_manager_returns_zero_total(self, manager):
        s = manager.stats()
        assert s["total"] == 0

    def test_total_matches_created_count(self, manager):
        for i in range(3):
            manager.create(f"T{i}", "d", "Hardware", "Low", "U")
        assert manager.stats()["total"] == 3

    def test_by_status_counts_open(self, manager):
        manager.create("T1", "d", "Hardware", "Low", "U")
        manager.create("T2", "d", "Hardware", "Low", "U")
        s = manager.stats()
        assert s["by_status"]["Open"] == 2

    def test_by_category_counts_correctly(self, manager):
        manager.create("T1", "d", "Hardware", "Low", "U")
        manager.create("T2", "d", "Hardware", "Medium", "U")
        manager.create("T3", "d", "Other", "Low", "U")
        s = manager.stats()
        assert s["by_category"]["Hardware"] == 2
        assert s["by_category"]["Other"] == 1

    def test_by_priority_counts_correctly(self, manager):
        manager.create("T1", "d", "Other", "Critical", "U")
        manager.create("T2", "d", "Other", "Low", "U")
        s = manager.stats()
        assert s["by_priority"]["Critical"] == 1
        assert s["by_priority"]["Low"] == 1

    def test_stats_has_all_status_keys(self, manager):
        s = manager.stats()
        for status in TICKET_STATUSES:
            assert status in s["by_status"]

    def test_stats_has_all_priority_keys(self, manager):
        s = manager.stats()
        for priority in PRIORITY_LEVELS:
            assert priority in s["by_priority"]
