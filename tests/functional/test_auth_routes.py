def test_unauthenticated_redirect_to_login(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_login_success(client, staff_user):
    response = client.post(
        "/auth/login",
        data={"username": "staff_test", "password": "StaffPass123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome back, Staff!" in response.data
    assert b"Dashboard Overview" in response.data


def test_login_invalid_password(client, staff_user):
    response = client.post(
        "/auth/login",
        data={"username": "staff_test", "password": "WrongPassword!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username/email or password." in response.data


def test_rbac_staff_forbidden_from_admin_users(client, staff_user):
    # Log in as staff
    client.post(
        "/auth/login",
        data={"username": "staff_test", "password": "StaffPass123!"},
        follow_redirects=True,
    )

    # Attempt to visit admin-only user management
    response = client.get("/users")
    assert response.status_code == 403
    assert b"Access Denied" in response.data or b"403" in response.data


def test_admin_allowed_access_to_users(client, admin_user):
    # Log in as admin
    client.post(
        "/auth/login",
        data={"username": "admin_test", "password": "AdminPass123!"},
        follow_redirects=True,
    )

    # Visit admin user management
    response = client.get("/users")
    assert response.status_code == 200
    assert b"User Management" in response.data
