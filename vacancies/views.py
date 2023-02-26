import json

from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.viewsets import ModelViewSet

from djangoProject import settings
from vacancies.models import Vacancy, Skill
from vacancies.serializers import VacancyListSerializer, VacancyDetailSerializer, VacancyCreateSerializer, \
    VacancyUpdateSerializer, VacancyDestroySerializer, SkillSerializer


def hello(request):
    return HttpResponse("Hello world")


class SkillsViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class VacancyListView(ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyListSerializer

    def get(self, request, *args, **kwargs):
        vacancy_text = request.GET.get('text', None) # Search request eg.: /vacancy/?text=new
        if vacancy_text:
            self.queryset = self.queryset.filter(
                text__icontains=vacancy_text
            )

        # skill_name = request.GET.get('skill', None) # Search request eg.: /vacancy/?skill=java
        # if skill_name:
        #     self.queryset = self.queryset.filter(
        #         skills__name__icontains=skill_name
        #     )
        #
        # return super().get(request, *args, **kwargs)
        """ 
        Множественный поиск пример на вакансиях
        делаем Q класс и заворачиваем все условия для фильтра в класс Q
        """
        skills = request.GET.getlist('skill', None)  # Search request eg.: /vacancy/?skill=java&skill=python
        skills_q = None
        for skill in skills:
            if skills_q is None:
                skills_q = Q(skills__name__icontains=skill)# специальный Q класс для сбора фильтраций
            else:
                skills_q |= Q(skills__name__icontains=skill)# otherwise if we already have something we add another 'Q' class

        if skills_q:
            self.queryset = self.queryset.filter(skills_q)

        return super().get(request, *args, **kwargs)




    # def get(self, request, *args, **kwargs):
    #     super().get(request, *args, **kwargs)
    #
    #     search_text = request.GET.get("text", None)
    #     if search_text:
    #         self.object_list = self.object_list.filter(text=search_text)
    #
    #     # Sort A-Z
    #     # self.object_list = self.object_list.order_by("text")
    #     self.object_list = self.object_list.select_related("user").prefetch_related("skills").order_by("text")
    #
    #     # Pagination
    #     paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
    #     page_number = request.GET.get("page")
    #     page_obj = paginator.get_page(page_number)
    #
    #     #       all commented because we use Serializers feature
    #     # vacancies = []
    #     # for vacancy in page_obj:
    #     #     vacancies.append({
    #     #         "id": vacancy.id,
    #     #         "slug": vacancy.slug,
    #     #         "text": vacancy.text,
    #     #         "status": vacancy.status,
    #     #         "created": vacancy.created,
    #     #         "username": vacancy.user.username,
    #     #         "skills": list(map(str, vacancy.skills.all()))
    #     #     })
    #
    #     # Func that every page_obj will put 'vacancy.user.username' field.
    #     list(map(lambda x: setattr(x, "username", x.user.username if x.user else None), page_obj))
    #
    #     # for frontend that it can view all pagination
    #     response = {
    #         "items": VacancyListSerializer(page_obj, many=True).data,  # use 'many=True' process list of objects,not just one
    #         "num_pages": paginator.num_pages,
    #         "total": paginator.count
    #     }
    #     return JsonResponse(response, safe=False)


class VacancyDetailView(RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer

    # def get(self, request, *args, **kwargs):
    #     vacancy = self.get_object()
    #     return JsonResponse(VacancyDetailSerializer(vacancy).data)


# @method_decorator(csrf_exempt, name="dispatch")
class VacancyCreateView(CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyCreateSerializer
    # model = Vacancy
    # fields = ["user", "slug", "text", "status", "created", "skills"]  # Нужно для CreateView чтобы сгенерировать форму
    #
    # def post(self, request, *args, **kwargs):
    #     vacancy_data = VacancyCreateSerializer(data=json.loads(request.body))
    #     if vacancy_data.is_valid():
    #         vacancy_data.save()
    #     else:
    #         return JsonResponse(vacancy_data.errors)
    #
    #     # vacancy = Vacancy.objects.create(
    #     #     slug=vacancy_data["slug"],
    #     #     text=vacancy_data["text"],
    #     #     status=vacancy_data["status"]
    #     # )
    #     # # Returns an object or 404 error
    #     # vacancy.user = get_object_or_404(User, pk=vacancy_data["user_id"])
    #     #
    #     # # Сохранение скилов
    #     # for skill in vacancy_data["skills"]:
    #     #     skill_obj, create = Skill.objects.get_or_create(
    #     #         name=skill,
    #     #         defaults={
    #     #             "is_active": True
    #     #         }
    #     #     )
    #     #     vacancy.skills.add(skill_obj)
    #     # vacancy.save()
    #
    #     return JsonResponse(vacancy_data.data)


# @method_decorator(csrf_exempt, name="dispatch")
class VacancyUpdateView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyUpdateSerializer

    #
    # model = Vacancy
    # fields = ["slug", "text", "status", "skills"]
    #
    # def patch(self, request, *args, **kwargs):
    #     super().post(request, *args, **kwargs)
    #
    #     vacancy_data = json.loads(request.body)
    #     self.object.slug = vacancy_data["slug"]
    #     self.object.text = vacancy_data["text"]
    #     self.object.status = vacancy_data["status"]
    #
    #     # Сохранение скилов
    #     for skill in vacancy_data["skills"]:
    #         try:
    #             skill_obj = Skill.objects.get(name=skill)
    #         except Skill.DoesNotExist:
    #             return JsonResponse({"error": "Skill not found"}, status=404)
    #         self.object.skills.add(skill_obj)
    #
    #     self.object.save()
    #
    #     return JsonResponse({
    #         "id": self.object.id,
    #         "slug": self.object.slug,
    #         "text": self.object.text,
    #         "status": self.object.status,
    #         "created": self.object.created,
    #         "user": self.object.user_id,
    #         "skills": list(self.object.skills.all().values_list("name", flat=True)),
    #     })


# @method_decorator(csrf_exempt, name="dispatch")
class VacancyDeleteView(DestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDestroySerializer
    # model = Vacancy
    # success_url = "/"  # URL На который надо направить пользователя после того как удалили запись
    #
    # def delete(self, request, *args, **kwargs):
    #     super().delete(request, *args, **kwargs)
    #
    #     return JsonResponse({"status": "ok"}, status=200)


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

# Запросы лайков по id [1, 2, 3, 4, 5, 6]
class VacancyLikeView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer

    def put(self, request, *args, **kwargs):
        Vacancy.objects.filter(pk__in=request.data).update(likes=F('likes') + 1)# класс F представляет текущий класс записи

        return JsonResponse(
            VacancyDetailSerializer(Vacancy.objects.filter(pk__in=request.data), many=True).data, safe=False
        )
