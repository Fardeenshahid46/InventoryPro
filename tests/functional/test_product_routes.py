def test_product_detail_view(client, staff_user, sample_product):
    # Log in as staff
    client.post(
        "/auth/login",
        data={"username": "staff_test", "password": "StaffPass123!"},
        follow_redirects=True,
    )

    # View product details
    response = client.get(f"/products/{sample_product.id}")
    assert response.status_code == 200
    assert sample_product.name.encode() in response.data
    assert sample_product.sku.encode() in response.data
