"""
EXAMPLE tests — demonstrates testing patterns for CRUD endpoints.
DELETE this file when you remove the example entities.

To remove:
1. Delete this file
2. Delete the example service, router, models, and schemas
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_create_item(
    client: AsyncClient, auth_headers: dict, test_user: User
) -> None:
    """Test creating a new item."""
    response = await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={
            "title": "Test Item",
            "description": "A test item description",
            "tag_names": ["test", "example"],
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "A test item description"
    assert data["user_id"] == str(test_user.id)
    assert len(data["tags"]) == 2
    tag_names = {t["name"] for t in data["tags"]}
    assert "test" in tag_names
    assert "example" in tag_names


@pytest.mark.asyncio
async def test_create_item_unauthenticated(client: AsyncClient) -> None:
    """Test creating an item without auth returns 403."""
    response = await client.post(
        "/api/v1/items",
        json={"title": "Unauthorized Item"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_items(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test listing items returns paginated results."""
    # Create a couple of items first
    for i in range(3):
        await client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={"title": f"Item {i}", "description": f"Description {i}"},
        )

    response = await client.get("/api/v1/items", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_list_items_with_search(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test searching items by title."""
    await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"title": "Unique Searchable Title", "description": "Some desc"},
    )
    await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"title": "Other Item", "description": "Other desc"},
    )

    response = await client.get(
        "/api/v1/items",
        headers=auth_headers,
        params={"search": "Unique Searchable"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any("Unique Searchable" in item["title"] for item in data["items"])


@pytest.mark.asyncio
async def test_get_item(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test getting a single item by ID."""
    create_response = await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"title": "Detail Item", "description": "Detail description"},
    )
    item_id = create_response.json()["id"]

    response = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["title"] == "Detail Item"


@pytest.mark.asyncio
async def test_get_item_not_found(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test getting a non-existent item returns 404."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/items/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_item(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test updating an item."""
    create_response = await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"title": "Original Title", "description": "Original desc"},
    )
    item_id = create_response.json()["id"]

    response = await client.put(
        f"/api/v1/items/{item_id}",
        headers=auth_headers,
        json={"title": "Updated Title", "description": "Updated desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated desc"


@pytest.mark.asyncio
async def test_delete_item(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test deleting an item."""
    create_response = await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={"title": "To Delete", "description": "Will be deleted"},
    )
    item_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_list_tags_empty(client: AsyncClient) -> None:
    """Test listing tags when none exist."""
    response = await client.get("/api/v1/tags")
    assert response.status_code == 200
    data = response.json()
    assert "tags" in data
    assert isinstance(data["tags"], list)


@pytest.mark.asyncio
async def test_create_tag(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test creating a new tag."""
    response = await client.post(
        "/api/v1/tags",
        headers=auth_headers,
        json={"name": "newtag"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "newtag"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_duplicate_tag(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test creating a duplicate tag returns 409."""
    await client.post(
        "/api/v1/tags",
        headers=auth_headers,
        json={"name": "duplicate"},
    )
    response = await client.post(
        "/api/v1/tags",
        headers=auth_headers,
        json={"name": "duplicate"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_item_with_tags_then_list_tags(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test that tags created via item creation appear in the tags list."""
    await client.post(
        "/api/v1/items",
        headers=auth_headers,
        json={
            "title": "Tagged Item",
            "description": "Has tags",
            "tag_names": ["alpha", "beta"],
        },
    )

    response = await client.get("/api/v1/tags")
    assert response.status_code == 200
    tag_names = {t["name"] for t in response.json()["tags"]}
    assert "alpha" in tag_names
    assert "beta" in tag_names


@pytest.mark.asyncio
async def test_list_items_pagination(
    client: AsyncClient, auth_headers: dict
) -> None:
    """Test pagination parameters work correctly."""
    for i in range(5):
        await client.post(
            "/api/v1/items",
            headers=auth_headers,
            json={"title": f"Paginated Item {i}"},
        )

    response = await client.get(
        "/api/v1/items",
        headers=auth_headers,
        params={"page": 1, "page_size": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] >= 5
    assert data["total_pages"] >= 3