"""Tests for the shared AI response parser."""

from __future__ import annotations

import json

import pytest

from app.models.dish import Category
from app.services.ai.base import APICallError, InvalidMenuImageError
from app.services.ai.response_parser import parse_dishes


def _dish(name: str = "Pad Thai", number: int | None = 1) -> dict:
    d = {
        "original_name": name,
        "translated_name": name,
        "description": f"desc {name}",
        "spiciness": 2,
        "sweetness": 3,
        "ingredients": ["x"],
        "allergens": [],
        "category": "main",
    }
    if number is not None:
        d["number"] = number
    return d


class TestParseDishesHappyPath:
    def test_plain_json(self):
        dishes = parse_dishes(json.dumps({"dishes": [_dish("Pad Thai", 1)]}))
        assert len(dishes) == 1
        assert dishes[0].original_name == "Pad Thai"
        assert dishes[0].category == Category.MAIN

    def test_json_fenced(self):
        body = json.dumps({"dishes": [_dish("Tom Yum", 1)]})
        assert len(parse_dishes(f"```json\n{body}\n```")) == 1
        assert len(parse_dishes(f"```\n{body}\n```")) == 1


class TestParseDishesErrors:
    def test_invalid_json_raises(self):
        with pytest.raises(APICallError, match="Failed to parse JSON"):
            parse_dishes("not json")

    def test_missing_dishes_key_raises(self):
        with pytest.raises(APICallError, match="'dishes' key"):
            parse_dishes(json.dumps({"menu": []}))

    def test_array_root_raises(self):
        with pytest.raises(APICallError, match="'dishes' key"):
            parse_dishes(json.dumps(["not", "a", "dict"]))

    def test_all_dishes_invalid_raises_invalid_menu(self):
        with pytest.raises(InvalidMenuImageError, match="Could not detect menu"):
            parse_dishes(json.dumps({"dishes": []}))


class TestParseDishesResilience:
    def test_skips_invalid_dishes(self):
        payload = {"dishes": [{"original_name": "Bad"}, _dish("Good", 1)]}
        dishes = parse_dishes(json.dumps(payload))
        assert [d.original_name for d in dishes] == ["Good"]


class TestParseDishesNumbering:
    def test_sorts_by_number_when_sequential(self):
        payload = {
            "dishes": [_dish("Third", 3), _dish("First", 1), _dish("Second", 2)]
        }
        dishes = parse_dishes(json.dumps(payload))
        assert [d.number for d in dishes] == [1, 2, 3]
        assert [d.original_name for d in dishes] == ["First", "Second", "Third"]

    def test_reassigns_on_missing_number(self):
        payload = {
            "dishes": [_dish("A", 1), _dish("B", None), _dish("C", 3)]
        }
        dishes = parse_dishes(json.dumps(payload))
        assert [d.number for d in dishes] == [1, 2, 3]

    def test_reassigns_on_duplicate(self):
        payload = {
            "dishes": [_dish("A", 1), _dish("B", 1), _dish("C", 2)]
        }
        dishes = parse_dishes(json.dumps(payload))
        assert [d.number for d in dishes] == [1, 2, 3]

    def test_reassigns_on_non_sequential_gap(self):
        payload = {
            "dishes": [_dish("A", 1), _dish("C", 3), _dish("D", 4)]
        }
        dishes = parse_dishes(json.dumps(payload))
        assert [d.number for d in dishes] == [1, 2, 3]
        assert [d.original_name for d in dishes] == ["A", "C", "D"]
