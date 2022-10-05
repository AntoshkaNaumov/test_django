import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from model_bakery import baker
from random import randint


@pytest.fixture  # помечаем фикстуру
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.fixture
def student():
    return baker.make('students.Student')


@pytest.fixture
def course():
    return baker.make('students.Course')


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_get_first_course(client, course):
    """проверка получения 1го курса"""
    # Arrange подгоотовка данных
    # Act вызов метода
    response = client.get(f'/api/v1/courses/{course.id}/')
    # Assert проверка
    assert response.status_code == 200
    assert response.data['id'] == course.id


@pytest.mark.django_db
def test_get_courses_list(client, course_factory):
    """проверка получения списка курсов"""
    courses = course_factory(_quantity=10)
    response = client.get('/api/v1/courses/')
    assert response.status_code == 200
    data = response.json()
    assert len(data) == len(courses)


@pytest.mark.django_db
def test_filter_courses_list_id(client, course_factory):
    """проверка фильтрации списка курсов по id"""
    courses = course_factory(_quantity=10)
    random_id = [course.id for course in courses][randint(0, 9)]
    response = client.get(f'/api/v1/courses/?id={random_id}')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == random_id


@pytest.mark.django_db
def test_filter_courses_list_name(client, course_factory):
    """проверка фильтрации списка курсов по name"""
    courses = course_factory(_quantity=10)
    course_name = [course.name for course in courses][randint(0, 9)]
    response = client.get(f'/api/v1/courses/?name={course_name}')
    assert response.status_code == 200
    data = response.json()
    assert data[0]['name'] == course_name


@pytest.mark.django_db
def test_create_course(client, student):
    """тест успешного создания курса"""
    count = Course.objects.count()
    response = client.post('/api/v1/courses/', data={'name': student.name, 'id': student.id})
    assert response.status_code == 201
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_update_course(client, course):
    """тест успешного обновления курса"""
    response = client.get(f'/api/v1/courses/{course.id}/')
    assert response.status_code == 200
    response_update = client.put(f'/api/v1/courses/{course.id}/',
    data={'name': 'New name'})
    assert response_update.status_code == 200
    response_updated = client.get(f'/api/v1/courses/{course.id}/')
    assert response_updated.data != response.data


@pytest.mark.django_db
def test_delete_course(client, course):
    """тест успешного удаления курса"""
    response = client.get(f'/api/v1/courses/{course.id}/')
    assert response.status_code == 200
    response_delete = client.delete(f'/api/v1/courses/{course.id}/')
    assert response_delete.status_code == 204
    response_deleted = client.get(f'/api/v1/courses/{course.id}/')
    assert response_deleted.status_code == 404
