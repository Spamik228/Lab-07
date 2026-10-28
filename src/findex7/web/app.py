from pathlib import Path
from fastapi import Request, responses
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Шляхи до шаблонів та статики всередині пакету
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=responses.HTMLResponse)
def index_page(request: Request, q: Optional[str] = None, scorer: str = "bm25", k: int = 10):
    results = []
    total = 0
    took_ms = 0.0

    if q:
        # Тут викликається реальний пошук з індексу
        # results = index.search(q, k=k, scorer=scorer)
        pass

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "query": q,
            "scorer": scorer,
            "results": results,
            "total": total,
            "took_ms": took_ms,
        },
    )


@app.get("/search-partial", response_class=responses.HTMLResponse)
def search_partial(request: Request, q: str = "", scorer: str = "bm25", k: int = 10):
    # Ендпоінт для htmx живого пошуку (повертає лише частину з результатами)
    results = []
    total = 0
    took_ms = 0.0

    if q:
        # results = index.search(q, k=k, scorer=scorer)
        pass

    return templates.TemplateResponse(
        "partials/results.html",
        {
            "request": request,
            "query": q,
            "scorer": scorer,
            "results": results,
            "total": total,
            "took_ms": took_ms,
        },
    )


@app.get("/doc/{doc_id}", response_class=responses.HTMLResponse)
def document_page(request: Request, doc_id: str, index: Any = Depends(get_index)):
    document = index.get_doc(doc_id) if hasattr(index, "get_doc") else None

    if not document:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    return templates.TemplateResponse(
        "doc.html",
        {
            "request": request,
            "doc_id": doc_id,
            "document": document,
        },
    )