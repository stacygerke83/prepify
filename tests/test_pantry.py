cat > tests/test_pantry.py << 'EOF'
import pytest
from prepify import create_app, db

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_add_item(client):
    r = client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    assert r.status_code == 201
    assert r.get_json()['message'] == 'Item added'

def test_get_items(client):
    client.post('/pantry', json={'name': 'Rice', 'quantity': '2 cups'})
    r = client.get('/pantry')
    data = r.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'Rice'
EOF
