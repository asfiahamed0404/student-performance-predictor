import unittest

from application import application


class CloudFrontRedirectTests(unittest.TestCase):
    def setUp(self):
        self.client = application.test_client()

    def test_direct_root_redirects(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://d16l6hogcgmcvh.cloudfront.net/")

    def test_direct_get_preserves_path_and_query(self):
        response = self.client.get("/predictdata?x=1&x=2")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.location,
            "https://d16l6hogcgmcvh.cloudfront.net/predictdata?x=1&x=2",
        )

    def test_direct_head_redirects(self):
        response = self.client.head("/predictdata")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "https://d16l6hogcgmcvh.cloudfront.net/predictdata")

    def test_only_exact_cloudfront_header_bypasses_redirect(self):
        response = self.client.get("/", headers={"X-From-CloudFront": "Yes"})
        self.assertEqual(response.status_code, 302)

        response = self.client.get("/", headers={"X-From-CloudFront": "yes"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<!DOCTYPE html>", response.data)

    def test_health_remains_available_directly(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_prediction_form_works_through_cloudfront(self):
        response = self.client.get("/predictdata", headers={"X-From-CloudFront": "yes"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"predict-form", response.data)

    def test_prediction_post_is_not_redirected(self):
        response = self.client.post(
            "/predictdata",
            data={
                "gender": "female",
                "race_ethnicity": "group C",
                "parental_level_of_education": "some college",
                "lunch": "standard",
                "test_preparation_course": "completed",
                "reading_score": "72",
                "writing_score": "74",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your predicted maths score", response.data)


if __name__ == "__main__":
    unittest.main()
