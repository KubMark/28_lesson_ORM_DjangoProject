import pytest

from tests.factories import VacancyFactory
from vacancies.serializers import VacancyListSerializer


@pytest.mark.django_db
def test_vacancy_list(client):
    vacancies = VacancyFactory.create_batch(10)

    expected_response = {
        "count": 10,
        "next": None,
        "previous": None,
        "results": VacancyListSerializer(vacancies, many=True).data

        #  всё что возвращает VacancyListSerializer
        # "results": [{
        #     "id": vacancy.pk,
        #     "text": "test text",
        #     "slug": "test",
        #     "status": "draft",
        #     "created": date.today().strftime("%Y-%m-%d"),
        #     "username": "test",
        #     "skills": []
        # }]
    }

    response = client.get("/vacancy/")

    assert response.status_code == 200
    assert response.data == expected_response
