"""One JSON brief per date in DynamoDB."""

import json
import os
import time

import boto3
from boto3.dynamodb.conditions import Key

KEEP_SECONDS = 90 * 24 * 60 * 60
PARTITION = "brief"
PUSHED_DATE = "latest"


def table():
    return boto3.resource("dynamodb").Table(os.environ["BRIEF_TABLE"])


def save(brief: dict) -> None:
    table().put_item(
        Item={
            "pk": PARTITION,
            "date": brief["date"],
            "body": json.dumps(brief, ensure_ascii=False),
            "expiresAt": int(time.time()) + KEEP_SECONDS,
        }
    )


def latest() -> dict | None:
    result = table().query(KeyConditionExpression=Key("pk").eq(PARTITION), ScanIndexForward=False, Limit=1)
    items = result.get("Items", [])
    return json.loads(items[0]["body"]) if items else None


def save_pushed(kind: str, body: dict) -> None:
    """The newest list an iPhone Shortcut sent, such as "todos" or "work". Each send replaces the last."""
    table().put_item(
        Item={
            "pk": kind,
            "date": PUSHED_DATE,
            "body": json.dumps(body, ensure_ascii=False),
            "expiresAt": int(time.time()) + KEEP_SECONDS,
        }
    )


def latest_pushed(kind: str) -> dict | None:
    item = table().get_item(Key={"pk": kind, "date": PUSHED_DATE}).get("Item")
    return json.loads(item["body"]) if item else None


def since(day: str) -> list[dict]:
    """Every saved brief from this date ("YYYY-MM-DD") on, oldest first."""
    result = table().query(KeyConditionExpression=Key("pk").eq(PARTITION) & Key("date").gte(day))
    return [json.loads(item["body"]) for item in result.get("Items", [])]
