import pytest
from fastapi.testclient import TestClient
from findex.web.app import app, get_index, get_settings


class MockIndex:
    """Легковаговий мік-індекс для ізольованого тестування API."""

    def __init__(self):
        self.docs = {
            "doc_1": {"title": "Python Basics", "content": "Introduction to Python programming language."}
        }
        self.vocab_size = 1500
        self.size_bytes = 10240

    def search(self, q: str, k: int, scorer: str):
        return [
            {
                "doc_id": "doc_1",
                "title": "Python Basics",
                "score": 1.25,
                "snippet": "Introduction to Python..."
            }
        ]

    def get_doc(self, doc_id: str):
        return self.docs.get(doc_id)


@pytest.fixture
def client():
    # Перевизначаємо залежності для тестів
    app.dependency_overrides[get_index] = lambda: MockIndex()
    app.dependency_overrides[get_settings] = lambda: {"index_path": "mock_path"}

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_unavailable():
    # Без перевизначення індексу (index = None) має повернути 503
    with TestClient(app) as client_no_index:
        response = client_no_index.get("/health")
        assert response.status_code == 503


def test_search_success(client):
    response = client.get("/search?q=python&k=5&scorer=bm25&page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "python"
    assert data["total"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["doc_id"] == "doc_1"


@pytest.mark.parametrize(
    "params",
    [
        {"k": 0},  # k менше за 1
        {"k": 101},  # k більше за 100
        {"scorer": "bad"},  # невалідний скорер
        {"page": 0},  # невалідна сторінка
    ],
)
def test_search_validation_errors(client, params):
    # Перевірка валідації Pydantic / Query parameters (422 Unprocessable Entity)
    query_params = {"q": "test", **params}
    response = client.get("/search", params=query_params)
    assert response.status_code == 422


def test_get_document_success(client):
    response = client.get("/docs/doc_1")
    assert response.status_code == 200
    assert response.json()["doc_id"] == "doc_1"


def test_get_document_not_found(client):
    response = client.get("/docs/nonexistent_id")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_stats(client):
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "doc_count" in data
    assert "vocabulary_size" in data
    assert "uptime_seconds" in data