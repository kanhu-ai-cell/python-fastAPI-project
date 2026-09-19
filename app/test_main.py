from fastapi.testclient import TestClient
from main import app


client = TestClient(app)

# Test for getData api
def test_getdata():
    response=client.get("/about")
    # status code
    assert response.status_code==200
    # response body
    assert response.json()=={
        "message":"this is about pages"
    }

