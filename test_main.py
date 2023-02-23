from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "test"}


def test_get_stock_price():
    response = client.post("/stocks/", json={
        "currency": "EUR",
        "stock_symbol": "AAPL",
        "date_range": "11/11/2022-12/11/2022"
    })

    assert response.status_code == 200
    assert "symbol" in response.json()
    assert "currency" in response.json()
    assert "daily_close" in response.json()
