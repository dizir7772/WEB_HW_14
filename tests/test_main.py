import unittest

# from fastapi.testclient import TestClient
# import main
#
# client = TestClient(main.app)


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200


if __name__ == '__main__':
    unittest.main()
