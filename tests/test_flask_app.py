from unittest import TestCase

from flask import Response

from main import create_app, data_provider


class TestFlaskApp(TestCase):
    def setUp(self) -> None:
        data_provider.clear()
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    def test_root_url(self):
        with self.client.get("/") as rv:
            self.assertIsInstance(rv, Response)
            self.assertEqual(rv.status_code, 404)
            self.assertIn(b"<title>404 Not Found</title>", rv.data)

    def test_movies(self):
        with self.client.get("/movies") as rv:
            self.assertIsInstance(rv, Response)
            self.assertIn(b"films  req time", rv.data)
            self.assertIn(b"people req time", rv.data)
            self.assertEqual(rv.status_code, 200)

