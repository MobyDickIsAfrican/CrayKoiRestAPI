from django.test import TestCase
from rest_framework.test import APIClient as Client
from .models import Project, Page, Component
from django.contrib.auth.models import User
from django.urls import reverse

# Create your tests here.

class ProjectViewTest(TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username="sibonelo", password="hashThis2")
        user_1.save()
        Project.objects.create(name="First Project", user=user_1)
    def test_invalid_project_type_yields_error(self):
        c = Client()
        user = User.objects.get(username="sibonelo")
        c.force_authenticate(user=user)
        response = c.post(reverse("projects-new"), {"name": True}, format='json')
        self.assertEqual(response.status_code, 406)
    def test_project_already_exists(self):
        c = Client()
        user = User.objects.get(username="sibonelo")
        c.force_authenticate(user=user)
        response = c.post(reverse("projects-new"), {"name": "First Project"}, format='json')
        self.assertEqual(response.status_code, 406)
    def test_successfully_created(self):
        c = Client()
        user = User.objects.get(username="sibonelo")
        c.force_authenticate(user=user)
        response = c.post(reverse("projects-new"), {"name": "2nd Project"}, format='json')
        self.assertEqual(response.status_code, 200)
    def test_unauthenticated_user_cannot_create_project(self):
        c = Client()
        response = c.post(reverse("projects-new"), {"name": "2nd Project"}, format=None)
        self.assertEqual(response.status_code, 401)

class ProjectListViewTest(TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username="luna", password="hashThis3")
        user_2 = User.objects.create_user(username="lesedi", password="hashThis4")
        User.objects.create_user(username="jongenkamnikamini", password="hashThis4")
        Project.objects.create(name="First Project1", user=user_1)
        Project.objects.create(name="2nd Project", user=user_1)
        Project.objects.create(name="3rd Project", user=user_2)
    def test_no_unauthorized_access(self):
        c = Client()
        response = c.get(reverse("projects-list"))
        self.assertEqual(response.status_code, 401)
    def test_no_projects_found(self):
        user = User.objects.get(username="jongenkamnikamini")
        c = Client()
        c.force_authenticate(user=user)
        response = c.get(reverse("projects-list"))
        self.assertEqual(response.status_code, 200)
        # response should return empty list
        self.assertListEqual(response.data, [])
    #user must only be able to see own projects, not others
    def test_user_gets_own_projects_only(self):
        user = User.objects.get(username="luna")
        c = Client()
        c.force_authenticate(user=user)
        response = c.get(reverse("projects-list"))
        is_true = True
        #view must return an array of project entries {"title": "whatever", id: "pk"}
        for entry in response.data:
            try:
                user.projects.get(pk=entry["id"])
                print(entry['id'])
            except Project.DoesNotExist:
                is_true = False
            finally:
                self.assertEqual(is_true, True)
    def test_user_successful(self):
        c = Client()
        user = User.objects.get(username="luna")
        c.force_authenticate(user=user)
        response = c.get(reverse("projects-list"))
        self.assertEqual(response.status_code, 200)

class PagePostTest(TestCase):
    def setUp(self):
        def url_wrapper(proj_id):
            return reverse("page-post", kwargs={"project_id": proj_id})
        self.reverseWrapper = url_wrapper
        perfect_user = User.objects.create_user(username="leona", password="hashThis4")
        perfect_user_project = Project.objects.create(user=perfect_user, name="Keep Going")
        User.objects.create_user(username="fear", password="hashThis5")
    def test_unauthenticated(self):
        c = Client()
        proj = Project.objects.get(name="Keep Going")
        response = c.post(self.reverseWrapper(proj.id), {"title": "Love"}, format="json")
        self.assertEqual(response.status_code, 401)
    def test_project_does_not_belong_to_user(self):
        user = User.objects.get(username="fear")
        c = Client()
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="Keep Going")
        response = c.post(self.reverseWrapper(proj.id), {"title": "Hardness"}, format="json")
        # view returns 404 if project does not belong to user
        self.assertEqual(response.status_code, 404)
    #if project belongs to user, create page
    def test_successful_page_created(self):
        c = Client()
        user = User.objects.get(username="leona")
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="Keep Going")
        response = c.post(self.reverseWrapper(proj.id), {"title": "Love"}, format="json")
        self.assertEqual(response.status_code, 200)

class PageViewTest(TestCase):
    def setUp(self):
        def url_wrapper(proj_id, page_id):
            return reverse("page-view", kwargs={"project_id": proj_id, "page_id": page_id})
        self.reverseWrapper = url_wrapper
        perfect_user = User.objects.create_user(username="musa", password="hashThis6")
        perfect_user_project = Project.objects.create(user=perfect_user, name="Discipline")
        perfect_page = Page.objects.create(project=perfect_user_project, title="Alright")
        #user that will try to modify other user's project
        User.objects.create_user(username="baduser", password="hashThis5")
    def test_project_does_not_belong_to_user(self):
        user = User.objects.get(username="baduser")
        c = Client()
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="Discipline")
        response = c.delete(self.reverseWrapper(proj.id, 93), {"title": "Hardness"}, format="json")
        # view returns 404 if project does not belong to user
        self.assertEqual(response.status_code, 400)
    def test_unauthenticated(self):
        c = Client()
        proj = Project.objects.get(name="Discipline")
        response = c.delete(self.reverseWrapper(proj.id, 90), {"title": "Love"}, format="json")
        self.assertEqual(response.status_code, 401)
    #if project belongs to user, but user has no page and tries to delete, return "Not Allowed"
    def test_page_does_not_exist(self):
        user = User.objects.get(username="musa")
        c = Client()
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="Discipline")
        response = c.delete(self.reverseWrapper(proj.id, 90), {"title": "Love"}, format="json")
        self.assertEqual(response.status_code, 400)
    #if project belongs to user, page exists, user tries to delete check if successful
    def test_page_delete_successful(self):
        user = User.objects.get(username="musa")
        c = Client()
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="Discipline")
        page_id = Page.objects.get(project=proj).id
        response = c.delete(self.reverseWrapper(proj.id, page_id), {"title": "Love"}, format="json")
        self.assertEqual(response.status_code, 200)

class ComponentViewTest(TestCase):
    def setUp(self):
        def url_func(proj_id, page_id, comp_id):
            return reverse("component-view", kwargs={"project_id": proj_id, "comp_id": comp_id, "page_id": page_id})
        self.urlReverse = url_func
        good_user = User.objects.create_user(username="Thobz", password="hashThis1")
        project_1 = Project.objects.create(user=good_user, name="top secret")
        page = Page.objects.create(project=project_1, title="We here")
        obj = {"backgroundColor": 'blue', "borderRadius": "9px"}
        Component.objects.create(page=page, secondary_state=obj, left=55, top=80, height=60, width=50, comp_id="some-id", parent=None)
        Component.objects.create(page=page, secondary_state=obj, left=55, top=80, height=60, width=50, comp_id="another-id", parent=None)
        #create bad user
        User.objects.create_user(username="Xobz", password="hashThis2")
    def test_unauthenticated(self):
        c = Client()
        get_response = c.get(self.urlReverse(1, 2, 3))
        delete_response = c.delete(self.urlReverse(1, 2, 3))
        self.assertEqual(get_response.status_code, 401)
        self.assertEqual(delete_response.status_code, 401)
    def test_not_your_project(self):
        c = Client()
        user = User.objects.get(username="Xobz")
        c.force_authenticate(user=user)
        proj_id = Project.objects.get(name="top secret").id
        get_response = c.get(self.urlReverse(proj_id, 100, 88))
        delete_response = c.delete(self.urlReverse(proj_id, 100, 88))
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
    def test_page_not_found(self):
        c = Client()
        user = User.objects.get(username="Thobz")
        c.force_authenticate(user=user)
        proj= Project.objects.get(name="top secret")
        get_response = c.get(self.urlReverse(proj.id, 55, 71))
        delete_response = c.delete(self.urlReverse(proj.id, 55, 71))
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
    def test_component_not_found(self):
        c = Client()
        user = User.objects.get(username="Thobz")
        c.force_authenticate(user=user)
        proj= Project.objects.get(name="top secret")
        page = Page.objects.get(project=proj)
        get_response = c.get(self.urlReverse(proj.id, page.id, 71))
        delete_response = c.delete(self.urlReverse(proj.id, page.id, 71))
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
    def test_succesful_request(self):
        c = Client()
        user = User.objects.get(username="Thobz")
        c.force_authenticate(user=user)
        proj = Project.objects.get(name="top secret")
        page = Page.objects.get(project=proj)
        comp_id_1 = Component.objects.get(comp_id="some-id").id
        comp_id_2 = Component.objects.get(comp_id="another-id").id
        get_response = c.get(self.urlReverse(proj.id, page.id, comp_id_1))
        delete_response = c.delete(self.urlReverse(proj.id, page.id, comp_id_2))
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 200)

class ComponentPostViewTest(TestCase):
    def setUp(self):
        def url_wrapper(project_id, page_id):
            return reverse("new-component", kwargs={"project_id": project_id, "page_id": page_id})
        self.urlReverse = url_wrapper
        user_1 = User.objects.create_user(username="sethu", password="tomriddle1")
        user_project = Project.objects.create(user=user_1, name="unique 1")
        user_page = Page.objects.create(project=user_project, title="best ever")
    def test_unauthenticated(self):
        c = Client()
        response = c.post(self.urlReverse(101, 102))
        self.assertEqual(response.status_code, 401)
    def test_no_project(self):
        c = Client()
        user = User.objects.get(username="sethu")
        c.force_authenticate(user=user)
        data = {}
        response = c.post(self.urlReverse(101, 102), data, format="json")
        self.assertEqual(response.status_code, 400)
    def test_no_page(self):
        c = Client()
        user = User.objects.get(username="sethu")
        project = Project.objects.get(name="unique 1")
        c.force_authenticate(user=user)
        data = {}
        response = c.post(self.urlReverse(project.id, 102), data, format="json")
        self.assertEqual(response.status_code, 400)
    def test_successful(self):
        c = Client()
        user = User.objects.get(username="sethu")
        project = Project.objects.get(name="unique 1")
        page = Page.objects.get(project=project)
        c.force_authenticate(user=user)
        data_1 = {"left": 1, "top": 3, "width": 30, "height": 30, "id": "jdakie", "parent": None}
        response_1 = c.post(self.urlReverse(project.id, page.id), data_1, format="json")
        self.assertEqual(response_1.status_code, 200)

class ComponentListViewTest(TestCase):
    def setUp(self):
        def url_wrapper(project_id):
            return reverse("components-list", kwargs={"project_id": project_id})
        self.urlReverse = url_wrapper
        #project has no components
        user_1 = User.objects.create_user(username="inga", password="tomriddle2")
        user_project = Project.objects.create(user=user_1, name="unique 2")
        user_page = Page.objects.create(project=user_project, title="best ever 2")
        #testing for project that has components
        user_project_2 = Project.objects.create(user=user_1, name="unique 3")
        user_page_2 = Page.objects.create(project=user_project_2, title="best ever 3")
        obj = {"backgroundColor": 'blue', "borderRadius": "9px"}
        Component.objects.create(page=user_page_2, secondary_state=obj, left=55, top=80, height=60, width=50, comp_id="some-id-1", parent=None)
        Component.objects.create(page=user_page_2, secondary_state=obj, left=55, top=80, height=60, width=50, comp_id="another-id-2", parent="some-id-1")
    def test_unauthenticated(self):
        c = Client()
        response = c.get(self.urlReverse(104))
        self.assertEqual(response.status_code, 401)
    def test_no_project(self):
        c = Client()
        user = User.objects.get(username="inga")
        c.force_authenticate(user=user)
        response_1 = c.get(self.urlReverse(105))
        data_1 = {}
        response_2 = c.put(self.urlReverse(105), [data_1], format="json")
        self.assertEqual(response_1.status_code, 404)
        self.assertEqual(response_2.status_code, 400)
    def test_no_components(self):
        c = Client()
        user = User.objects.get(username="inga")
        project = Project.objects.get(name="unique 2")
        c.force_authenticate(user=user)
        data_1 = {"left": 1, "top": 3, "width": 30, "height": 30, "id": "jdakieiyut", "parent": None, "page": "best ever 2"}
        response_1 = c.get(self.urlReverse(project.id))
        response_2 = c.put(self.urlReverse(project.id), [data_1], format="json")
        self.assertEqual(response_1.status_code, 200)
        self.assertEqual(response_2.status_code, 400)
    def test_succesful_get(self):
        c = Client()
        user = User.objects.get(username="inga")
        project = Project.objects.get(name="unique 3")
        c.force_authenticate(user=user)
        response_1 = c.get(self.urlReverse(project.id))
        self.assertEqual(response_1.status_code, 200)
    def test_succesful_put(self):
        c = Client()
        user = User.objects.get(username="inga")
        project = Project.objects.get(name="unique 3")
        c.force_authenticate(user=user)
        data_1 = {"left": 1, "top": 3, "width": 30, "height": 30, "id": "some-id-1", "parent": None, "page": "best ever 3"}
        data_2 = {"left": 1, "top": 3, "width": 30, "height": 30, "id": "another-id-2", "parent": "some-id-1", "page": "best ever 3"}
        response_1 = c.put(self.urlReverse(project.id), data=[data_1, data_2], format="json")
        self.assertEqual(response_1.status_code, 200)

class SignUpTest(TestCase):
    def setUp(self):
        User.objects.create_user(username="mpumi@gmail.com", password="hashmpumi1", email="mpumi@gmail.com")
    def test_validation_errors(self):
        c = Client()
        data = {"email": "mpumi@gmail.com", "firstPassword": "craxykoi1", "secondPassword": "craxykoi1"}
        response = c.post(reverse("sign-up"), data, format="json")
        self.assertEqual(response.status_code, 400)
    def test_user_is_already_logged_in(self):
        c = Client()
        user = User.objects.get(username="mpumi@gmail.com")
        c.force_authenticate(user=user)
        data = {"email": "mpumi@gmail.com", "firstPassword": "craxykoi1", "secondPassword": "craxykoi1"}
        response = c.post(reverse("sign-up"), data, format="json")
        self.assertEqual(response.status_code, 403)
    def test_succesful_user(self):
        c = Client()
        data = {"email": "thea@gmail.com", "firstPassword": "craxykoi1", "secondPassword": "craxykoi1"}
        response = c.post(reverse("sign-up"), data, format="json")
        self.assertEqual(response.status_code, 200)

class LoginTest(TestCase):
    #useless test to help me understand the authToken view
    def setUp(self):
        User.objects.create_user(username="atibia@gmail.com", password="hashatibia1", email="atibia@gmail.com")
    def test_succesful_login(self):
        c = Client()
        response = c.post(reverse("auth-view"), {"username": "atibia@gmail.com", "password": "hashatibia1"}, format="json")
        self.assertEquals(response.status_code, 200)
    def test_failed_login(self):
        c = Client()
        response = c.post(reverse("auth-view"), {"username": "atibia@gmail.com", "password": "hashatibia13"}, format="json")
        self.assertEquals(response.status_code, 400)

