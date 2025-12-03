import pytest
from app import create_app, db
from app.models import PantryItem

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_add_item(client):
    response = client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    assert response.status_code == 201
    assert b'Item added' in response.data

def test_get_items(client):
    # Add an item first
    client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    response = client.get('/pantry')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Rice'

def test_update_item(client):
    # Add item
    client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    # Update item
    response = client.put('/pantry/1', json={'quantity': '3 cups'})
    assert response.status_code == 200
    assert b'Item updated' in response.data

def test_delete_item(client):
    # Add item
    client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    # Delete item
    response = client.delete('/pantry/1')
    assert response.status_code == 200
    assert b'Item deleted' in response.data
