from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
import json
import os

app = FastAPI(title="pyapi-serv")

# --- CORS (allow your React dev server) ---
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class Item(BaseModel):
    id: int
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    role: str = Field(min_length=1)

class ItemCreate(BaseModel):
    name: str = Field(min_length=1)
    location: str = Field(min_length=1)
    role: str = Field(min_length=1)

# --- Simple JSON persistence ---
DATA_FILE = os.path.join(os.path.dirname(__file__), "items.json")

def _load_items() -> List[Item]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            return [Item(**it) for it in raw]
    # return empty if no file
    return []

def _save_items(items: List[Item]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([it.dict() for it in items], f, indent=2, ensure_ascii=False)

# --- Load initial items ---
items: List[Item] = _load_items()
_next_id = max([it.id for it in items], default=0) + 1

# --- Generate dummy data up to 10000 ---
while len(items) < 10000:
    items.append(
        Item(
            id=_next_id,
            name=f"User{_next_id}",
            location=["Bangalore", "Chennai", "Hyderabad", "Delhi", "Pune", "Mumbai"][_next_id % 6],
            role=["Developer", "Designer", "Manager", "Tester", "Lead", "Analyst"][_next_id % 6],
        )
    )
    _next_id += 1

# --- Endpoints ---
@app.get("/")
def root():
    return {"status": "ok", "message": "pyapi-serv running"}

@app.get("/items", response_model=List[Item])
def list_items(limit: int = 1000, q: Optional[str] = None):
    """
    Returns up to `limit` items. If `q` provided, filters by id/name/location/role (contains, case-insensitive).
    """
    data = items
    if q:
        ql = q.lower()
        data = [
            it for it in items
            if ql in str(it.id).lower()
            or ql in it.name.lower()
            or ql in it.location.lower()
            or ql in it.role.lower()
        ]
    return data[:limit]

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for it in items:
        if it.id == item_id:
            return it
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

@app.post("/items", response_model=Item, status_code=201)
def create_item(payload: ItemCreate):
    global _next_id
    new_item = Item(id=_next_id, **payload.dict())
    items.append(new_item)
    _next_id += 1
    _save_items(items)
    return new_item

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)