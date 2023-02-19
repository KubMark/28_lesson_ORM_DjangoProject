import json

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView

from djangoProject import settings
from vacancies.models import Vacancy, Skill


def hello(request):
    return HttpResponse("Hello world")


class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        search_text = request.GET.get("text", None)
        if search_text:
            self.object_list = self.object_list.filter(text=search_text)

        # Sort A-Z
        # self.object_list = self.object_list.order_by("text")
        self.object_list = self.object_list.select_related("user").prefetch_related("skills").order_by("text")

        # Pagination
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        vacancies = []
        for vacancy in page_obj:
            vacancies.append({
                # "id": vacancy.id,
                # "text": vacancy.text
                "id": vacancy.id,
                "slug": vacancy.slug,
                "text": vacancy.text,
                "status": vacancy.status,
                "created": vacancy.created,
                "username": vacancy.user.username,
                "skills": list(map(str, vacancy.skills.all()))
            })
        # for frontend that it can view all pagination
        response = {
            "items": vacancies,
            "num_pages": paginator.num_pages,
            "total": paginator.count
        }
        return JsonResponse(response, safe=False)


class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        vacancy = self.get_object()
        return JsonResponse({
            "id": vacancy.id,
            "slug": vacancy.slug,
            "text": vacancy.text,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
            "skills": list(map(str, vacancy.skills.all())),

        })


@method_decorator(csrf_exempt, name="dispatch")
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ["user", "slug", "text", "status", "created", "skills"]  # Нужно для CreateView чтобы сгенерировать форму

    def post(self, request, *args, **kwargs):
        vacancy_data = json.loads(request.body)

        vacancy = Vacancy.objects.create(
            slug=vacancy_data["slug"],
            text=vacancy_data["text"],
            status=vacancy_data["status"]
        )
        # Returns an object or 404 error
        vacancy.user = get_object_or_404(User, pk=vacancy_data["user_id"])

        # Сохранение скилов
        for skill in vacancy_data["skills"]:
            skill_obj, create = Skill.objects.get_or_create(
                name=skill,
                defaults={
                    "is_active": True
                }
            )
            vacancy.skills.add(skill_obj)
        vacancy.save()


        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
        })


@method_decorator(csrf_exempt, name="dispatch")
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ["slug", "text", "status", "skills"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        vacancy_data = json.loads(request.body)
        self.object.slug = vacancy_data["slug"]
        self.object.text = vacancy_data["text"]
        self.object.status = vacancy_data["status"]

        # Сохранение скилов
        for skill in vacancy_data["skills"]:
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Skill not found"}, status=404)
            self.object.skills.add(skill_obj)

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "slug": self.object.slug,
            "text": self.object.text,
            "status": self.object.status,
            "created": self.object.created,
            "user": self.object.user_id,
            "skills": list(self.object.skills.all().values_list("name", flat=True)),
        })


@method_decorator(csrf_exempt, name="dispatch")
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = "/"  # URL На который надо направить пользователя после того как удалили запись

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


# to see quantity of vacancys from each user
class UserVacancyDetailView(View):
    def get(self, request):
        """method 'annotate' adds 'vacancies' and Counts it"""
        user_qs = User.objects.annotate(vacancies=Count('vacancy'))
        # paginating
        paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        users = []
        for user in page_obj:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies
            })

        response = {
            "items": users,
            "total": paginator.count,
            "num_pages": paginator.num_pages,
            # counting average quantity of vacancies from user
            "avg": user_qs.aggregate(avg=Avg('vacancies'))['avg']
        }
        return JsonResponse(response)
