"""Unit tests for ITKnowledgeBase — no external dependencies."""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from knowledge_base import ITKnowledgeBase


@pytest.fixture
def kb():
    return ITKnowledgeBase()


class TestSearch:
    def test_returns_results_for_known_keyword(self, kb):
        results = kb.search("vpn")
        assert len(results) > 0
        assert any("VPN" in r["title"] for r in results)

    def test_search_is_case_insensitive(self, kb):
        results_lower = kb.search("vpn")
        results_upper = kb.search("VPN")
        assert len(results_lower) == len(results_upper)

    def test_returns_empty_for_no_match(self, kb):
        results = kb.search("xyzzy_no_match_quantum")
        assert results == []

    def test_respects_max_results(self, kb):
        results = kb.search("issue", max_results=2)
        assert len(results) <= 2

    def test_default_max_results_is_three(self, kb):
        # "password" should match multiple entries
        results = kb.search("password")
        assert len(results) <= 3

    def test_most_relevant_result_first(self, kb):
        results = kb.search("printer not working")
        assert len(results) > 0
        # The printer article should rank highly
        assert any("printer" in r["title"].lower() or "printer" in r["id"].lower() for r in results[:2])

    def test_multi_keyword_query(self, kb):
        results = kb.search("outlook email not syncing")
        assert len(results) > 0
        assert any("Outlook" in r["title"] or "email" in r["title"].lower() for r in results)


class TestGetAllCategories:
    def test_returns_list_of_strings(self, kb):
        categories = kb.get_all_categories()
        assert isinstance(categories, list)
        assert all(isinstance(c, str) for c in categories)

    def test_no_duplicates(self, kb):
        categories = kb.get_all_categories()
        assert len(categories) == len(set(categories))

    def test_contains_expected_categories(self, kb):
        categories = kb.get_all_categories()
        assert "Network & Connectivity" in categories
        assert "Hardware" in categories
        assert "Software & Applications" in categories
        assert "Security & Access" in categories
        assert "Email & Collaboration" in categories


class TestGetByCategory:
    def test_returns_only_entries_for_category(self, kb):
        entries = kb.get_by_category("Hardware")
        assert len(entries) > 0
        assert all(e["category"] == "Hardware" for e in entries)

    def test_returns_empty_for_unknown_category(self, kb):
        entries = kb.get_by_category("Quantum Computing")
        assert entries == []

    def test_entries_have_required_fields(self, kb):
        entries = kb.get_by_category("Network & Connectivity")
        for entry in entries:
            assert "id" in entry
            assert "title" in entry
            assert "solution" in entry
            assert "keywords" in entry
            assert "escalate_if" in entry


class TestGetById:
    def test_returns_entry_for_valid_id(self, kb):
        entry = kb.get_by_id("NET-001")
        assert entry is not None
        assert entry["id"] == "NET-001"

    def test_returns_none_for_invalid_id(self, kb):
        entry = kb.get_by_id("NONEXISTENT-999")
        assert entry is None

    def test_all_ids_are_retrievable(self, kb):
        for cat in kb.get_all_categories():
            for entry in kb.get_by_category(cat):
                fetched = kb.get_by_id(entry["id"])
                assert fetched is not None
                assert fetched["id"] == entry["id"]


class TestKnowledgeBaseIntegrity:
    def test_all_entries_have_unique_ids(self, kb):
        all_ids = []
        for cat in kb.get_all_categories():
            all_ids.extend(e["id"] for e in kb.get_by_category(cat))
        assert len(all_ids) == len(set(all_ids)), "Duplicate IDs found in knowledge base"

    def test_minimum_entry_count(self, kb):
        total = sum(len(kb.get_by_category(c)) for c in kb.get_all_categories())
        assert total >= 10, "Knowledge base should have at least 10 entries"

    def test_solutions_are_non_empty(self, kb):
        for cat in kb.get_all_categories():
            for entry in kb.get_by_category(cat):
                assert entry["solution"].strip(), f"Empty solution for {entry['id']}"
