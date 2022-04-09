import json
from unittest import TestCase

import pytest
from django.test import Client
from django.urls import reverse

from companies.models import Company

@pytest.mark.django_db
class BasicCompanyApiTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.companies_url = reverse("companies-list")

    def tearDown(self) -> None:
        pass

class TestGetCompanies(BasicCompanyApiTestCase):
    def test_zero_companies_should_return_empty_list(self) -> None:
        response = self.client.get(self.companies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_one_company_exists_should_succed(self) -> None:
        amazon = Company.objects.create(name="Amazon")
        response = self.client.get(self.companies_url)
        response_content = json.loads(response.content)[0]
        self.assertEqual(response_content.get("name"), amazon.name)
        self.assertEqual(response_content.get("status"), amazon.status)
        self.assertEqual(response_content.get("notes"), amazon.notes)
        self.assertEqual(response_content.get("application_link"), amazon.application_link)

        amazon.delete()

class TestPostCompanies(BasicCompanyApiTestCase):
    def test_create_company_without_arguments_should_fail(self) -> None:
        response = self.client.post(path=self.companies_url, )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {"name": ["This field is required."]})



