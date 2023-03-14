from datetime import date

import pytest

from vacancies.models import Vacancy


@pytest.mark.django_db
def test_vacancy_list(client, vacancy):
    expected_response = {
        "count": 1,
        "next": None,
        "previous": None,
        #  всё что возвращает VacancyListSerializer
        "results": [{
            "id": vacancy.pk,
            "text": "test text",
            "slug": "test",
            "status": "draft",
            "created": date.today().strftime("%Y-%m-%d"),
            "username": "test",
            "skills": []
        }]
    }

    response = client.get("/vacancy/")

    assert response.status_code == 200
    assert response.data == expected_response
