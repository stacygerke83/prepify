import pytest
from prepify import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_post_put_delete(client):
    # Start: GET should be empty
    resp = client.get('/pantry')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

    # POST: create an item
    resp = client.post('/pantry', json={'name': 'CRUD', 'quantity': '1', 'category': 'test'})
    assert resp.status_code == 201
    item = resp.get_json()['item']
    item_id = item['id']

    # GET: item appears in listing
    resp = client.get('/pantry')
    items = resp.get_json()
    assert any(i['id'] == item_id for i in items)

    # PUT: update quantity
    resp = client.put(f'/pantry/{item_id}', json={'quantity': '5'})
    assert resp.status_code == 200
    assert resp.get_json()['item']['quantity'] == '5'

    # DELETE: remove item
    resp = client.delete(f'/pantry/{item_id}')
    assert resp.status_code == 200

    # GET: item no longer present
    resp = client.get('/pantry')
    items = resp.get_json()
    assert all(i['id'] != item_id for i in items)
