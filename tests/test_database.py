import pytest
import sqlite3
import os
import sys
import database.database as database

TEST_DB = "test_chatroom.db"

@pytest.fixture(autouse=True)
def fixture_function():
    #Setup
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    database.create_messages_table(TEST_DB)
    database.create_users_table(TEST_DB)
    yield
    
    #Teardown
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def test_create_message_table():
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
    assert cursor.fetchone() is not None


def test_create_users_table():
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    assert cursor.fetchone() is not None

