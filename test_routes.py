from urllib.parse import urlencode

import pytest
import requests

from app import app
from strapi_model_mixin import *


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_entries(client):
    response = client.get('/messages?sort=content&filters={"content": "value"}&pagination={"limit": 10}&get_all=true')
    assert response.status_code == 200


# The fixture for the client is already defined in your previous code.
# We'll just write pytest functions that test various API query parameters for the Message model.

# Test 1: Fetching all messages with no extra parameters.
def test_get_all_messages_no_params(client):
    response = client.get('/messages')
    assert response.status_code == 200

# Test 2: Fetching all messages, ignoring pagination (if get_all=True is supported by your API).
def test_get_all_messages_get_all(client):
    response = client.get('/messages?get_all=true')
    assert response.status_code == 200

# Test 3: Fetching all messages, sorted by 'content' in ascending order.
def test_get_messages_sorted(client):
    response = client.get('/messages?sort=content')
    assert response.status_code == 200

# Test 4: Fetching messages filtered by a specific content.
def test_get_messages_filtered(client):
    filter_data = {"content": {"$eq": "Hello World!"}}
    response = client.get(f'/messages?filters={urlencode(filter_data)}')
    assert response.status_code == 200

# Test 5: Fetching all messages and populating all related fields.
def test_get_messages_populate_all(client):
    response = client.get('/messages?populate=*')
    assert response.status_code == 200

# Test 6: Fetching all messages and selecting only the 'content' and 'createdAt' fields.
def test_get_messages_fields(client):
    response = client.get('/messages?fields=content,createdAt')
    assert response.status_code == 200

# Test 7: Fetching messages with pagination limited to 3 entries.
def test_get_messages_pagination(client):
    pagination_data = {"limit": 3}
    response = client.get(f'/messages?pagination={urlencode(pagination_data)}')
    assert response.status_code == 200

# Test 8: Fetching messages in the 'preview' publication state.
def test_get_messages_publication_state(client):
    response = client.get('/messages?publication_state=preview')
    assert response.status_code == 200

# These are just example tests and they assume that your backend API behaves as expected.
# In a real-world scenario, you'd also want to check the content of the response, not just the status code.
