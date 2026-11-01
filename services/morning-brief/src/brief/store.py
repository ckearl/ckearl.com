"""One JSON brief per date in DynamoDB."""

import json
import os
import time

import boto3
from boto3.dynamodb.conditions import Key

KEEP_SECONDS = 90 * 24 * 60 * 60
PARTITION = "brief"
TODOS_PARTITION = "todos"
TODOS_DATE = "latest"


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


def save_todos(todos: dict) -> None:
    table().put_item(
        Item={
            "pk": TODOS_PARTITION,
            "date": TODOS_DATE,
            "body": json.dumps(todos, ensure_ascii=False),
            "expiresAt": int(time.time()) + KEEP_SECONDS,
        }
    )


def latest_todos() -> dict | None:
    item = table().get_item(Key={"pk": TODOS_PARTITION, "date": TODOS_DATE}).get("Item")
    return json.loads(item["body"]) if item else None
