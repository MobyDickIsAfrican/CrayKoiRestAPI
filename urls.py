from django.urls import path
from .views import ProjectView, PageView, ComponentView, ComponentListView, ComponentPostView, ProjectListView, PagePost, SignUpView
from rest_framework.authtoken import views as tokenView

urlpatterns = [
    path("projects/", ProjectListView.as_view(), name="projects-list"),
    path("projects/new/", ProjectView.as_view(), name="projects-new"),
    path("projects/project/<int:project_id>/new/page/", PagePost.as_view(), name="page-post"),
    path("projects/project/<int:project_id>/page/<int:page_id>/", PageView.as_view(), name="page-view"),
    path("projects/project/<int:project_id>/ui/", ComponentListView.as_view(), name="components-list"),
    path("projects/project/<int:project_id>/page/<int:page_id>/new/component/", ComponentPostView.as_view(), name="new-component"),
    path("projects/project/<int:project_id>/page/<int:page_id>/component/<int:comp_id>/", ComponentView.as_view(), name="component-view"),
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path('auth/', tokenView.obtain_auth_token, name="auth-view")
]