from django.core.paginator import Paginator
from django.db.models import Count, Avg, Q, F
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from djangoProject import settings
from vacancies.models import Vacancy, Skill
from vacancies.permissions import VacancyCreatePermission
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
        vacancy_text = request.GET.get('text', None)  # Search request eg.: /vacancy/?text=new
        if vacancy_text:
            self.queryset = self.queryset.filter(
                text__icontains=vacancy_text
            )

        """ 
        Множественный поиск пример на вакансиях
        делаем Q класс и заворачиваем все условия для фильтра в класс Q
        """
        skills = request.GET.getlist('skill', None)  # Search request eg.: /vacancy/?skill=java&skill=python
        skills_q = None
        for skill in skills:
            if skills_q is None:
                skills_q = Q(skills__name__icontains=skill)  # специальный Q класс для сбора фильтраций
            else:
                skills_q |= Q(
                    skills__name__icontains=skill)  # otherwise if we already have something we add another 'Q' class

        if skills_q:
            self.queryset = self.queryset.filter(skills_q)

        return super().get(request, *args, **kwargs)


class VacancyDetailView(RetrieveAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer
    permission_classes = [IsAuthenticated]  # Список с доступами


class VacancyCreateView(CreateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyCreateSerializer
    permission_classes = [IsAuthenticated, VacancyCreatePermission]


class VacancyUpdateView(UpdateAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyUpdateSerializer


class VacancyDeleteView(DestroyAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDestroySerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_vacancies(request):
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
        Vacancy.objects.filter(pk__in=request.data).update(
            likes=F('likes') + 1)  # класс F представляет текущий класс записи

        return JsonResponse(
            VacancyDetailSerializer(Vacancy.objects.filter(pk__in=request.data), many=True).data, safe=False
        )
