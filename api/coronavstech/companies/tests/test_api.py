import json
import logging
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
        self.assertEqual(
            response_content.get("application_link"), amazon.application_link
        )

        amazon.delete()


class TestPostCompanies(BasicCompanyApiTestCase):
    def test_create_company_without_arguments_should_fail(self) -> None:
        response = self.client.post(
            path=self.companies_url,
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content), {"name": ["This field is required."]}
        )

    def test_create_exists_company_should_fail(self) -> None:
        Company.objects.create(name="Amazon")
        response = self.client.post(path=self.companies_url, data={"name": "Amazon"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"name": ["company with this name already exists."]},
        )

    def test_create_company_with_only_name_all_fields_should_default(self) -> None:
        response = self.client.post(path=self.companies_url, data={"name": "SamsungE"})
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("name"), "SamsungE")
        self.assertEqual(response_content.get("status"), "Hiring")
        self.assertEqual(response_content.get("notes"), "")
        self.assertEqual(response_content.get("application_link"), "")

    def test_create_company_with_layoffs_status_should_succes(self) -> None:
        response = self.client.post(
            path=self.companies_url, data={"name": "Samsung", "status": "Lauoffs"}
        )
        self.assertEqual(response.status_code, 201)
        response_content = json.loads(response.content)
        self.assertEqual(response_content.get("status"), "Lauoffs")

    def test_create_company_with_wrong_status_status_should_fail(self) -> None:
        response = self.client.post(
            path=self.companies_url, data={"name": "Samsung", "status": "bebra_layoffs"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("bebra_layoffs", str(response.content))

    @pytest.mark.skip
    def test_should_be_ok_if_skip(self) -> None:
        self.assertEqual(1, 2)

    @pytest.mark.xfail
    def test_should_be_ok_if_fails(self) -> None:
        self.assertEqual(1, 2)


def raise_covid19_exception() -> None:
    raise ValueError("Corona Exception")


def test_raise_covid19_exception_should_pass() -> None:
    with pytest.raises(ValueError) as e:
        raise_covid19_exception()
    assert "Corona Exception" == str(e.value)


logger = logging.getLogger("CORONA_LOGS")


def func_that_logs_somthg() -> None:
    try:
        raise ValueError("Corona EXCEPTION")
    except ValueError as e:
        logger.warning(f"I am logging {str(e)}")


def test_logged_warning_level(caplog) -> None:
    func_that_logs_somthg()
    assert "I am logging Corona EXCEPTION" in caplog.text


def test_logged_info_level(caplog) -> None:
    with caplog.at_level(logging.INFO):
        logger.info("I am logging info level")
        assert "I am logging info level" in caplog.text
