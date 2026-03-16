import pytest


class TestProductsList:
    async def test_get_products_empty(self, client, auth_header):
        response = await client.get("/api/products", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_products_with_data(self, client, auth_header, sample_product):
        response = await client.get("/api/products", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Product"

    async def test_get_products_filter_by_category(self, client, auth_header, db):
        from app.models.analytics import AffiliateProduct

        product1 = AffiliateProduct(
            name="Product 1", category="electronics", ref_url="http://example.com/1"
        )
        product2 = AffiliateProduct(
            name="Product 2", category="books", ref_url="http://example.com/2"
        )
        db.add_all([product1, product2])
        await db.commit()

        response = await client.get("/api/products?category=electronics", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert all(p["category"] == "electronics" for p in data)

    async def test_get_products_unauthorized(self, client):
        response = await client.get("/api/products")
        assert response.status_code == 403


class TestProductCreate:
    async def test_create_product(self, client, auth_header):
        response = await client.post(
            "/api/products",
            json={
                "name": "New Product",
                "category": "electronics",
                "ref_url": "https://example.com/product/new",
                "description": "A brand new product",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Product"
        assert data["category"] == "electronics"
        assert data["is_active"] is True

    async def test_create_product_with_keywords(self, client, auth_header):
        response = await client.post(
            "/api/products",
            json={
                "name": "Keyword Product",
                "ref_url": "https://example.com/kw",
                "keywords": ["tech", "gadget", "new"],
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["keywords"] == ["tech", "gadget", "new"]

    async def test_create_product_with_price(self, client, auth_header):
        response = await client.post(
            "/api/products",
            json={
                "name": "Priced Product",
                "ref_url": "https://example.com/price",
                "price": "$99.99",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["price"] == "$99.99"

    async def test_create_product_missing_ref_url(self, client, auth_header):
        response = await client.post(
            "/api/products",
            json={"name": "No URL"},
            headers=auth_header,
        )
        assert response.status_code == 422


class TestProductUpdate:
    async def test_update_product_name(self, client, auth_header, sample_product):
        response = await client.patch(
            f"/api/products/{sample_product.id}",
            json={"name": "Updated Product Name"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Product Name"

    async def test_update_product_category(self, client, auth_header, sample_product):
        response = await client.patch(
            f"/api/products/{sample_product.id}",
            json={"category": "software"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["category"] == "software"

    async def test_update_product_not_found(self, client, auth_header):
        response = await client.patch(
            "/api/products/9999",
            json={"name": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert "error" in response.json()


class TestProductDelete:
    async def test_delete_product(self, client, auth_header, sample_product):
        response = await client.delete(f"/api/products/{sample_product.id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

    async def test_delete_product_not_found(self, client, auth_header):
        response = await client.delete("/api/products/9999", headers=auth_header)
        assert response.status_code == 200
        assert "error" in response.json()
