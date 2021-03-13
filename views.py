from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Page, Component
from .serializers import ProjectSerializer, PageSerializer, ComponentSerializer, UserSerializer
from rest_framework.parsers import JSONParser
import itertools
from .styleHelpers import getStyle, getComp
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate, login

# Create your views here.
def get_key(comp):
    return comp["page"]

class ProjectView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        user = request.user
        project_serializer = ProjectSerializer(data = request.data)
        if project_serializer.is_valid():
            project_serializer.save(user=user)
            return Response(data=project_serializer.errors, status=status.HTTP_200_OK)
        return Response(data=project_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

class ProjectListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        #get list of projects
        user = request.user
        user_projects = user.projects.all()
        if(user_projects.count() > 0):
            data = []
            for project in user_projects:
                proj_obj = {}
                proj_obj["name"] = project.name
                proj_obj["id"] = project.id
                data.append(proj_obj)
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(data=[], status=status.HTTP_200_OK)

class PagePost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #create new page
    def post(self, request, project_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            page_serializer = PageSerializer(data=request.data)
            if page_serializer.is_valid():
                page_serializer.save(project=project)
                return Response(status=status.HTTP_200_OK)
            return Response(data=page_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class PageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def delete(self, request, project_id, page_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            try:
                page = project.pages.get(id=page_id)
                page.delete()
                return Response(status=status.HTTP_200_OK)
            except Page.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ComponentView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #retreive component styles
    def get(self, request, project_id, page_id, comp_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            try:
                page = project.pages.get(id=page_id)
                try:
                    component = page.components.get(id=comp_id)
                    data = component.getStyles()
                    return Response(data=data, status=status.HTTP_200_OK)
                except Component.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            except Page.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
           return Response(status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, project_id, page_id, comp_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            try:
                page = project.pages.get(id=page_id)
                try:
                    component = page.components.get(id=comp_id)
                    component.delete()
                    return Response(status=status.HTTP_200_OK)
                except Component.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            except Page.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
           return Response(status=status.HTTP_404_NOT_FOUND)

class ComponentPostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #create new component
    def post(self, request, project_id, page_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            try:
                page = project.pages.get(id=page_id)
                secondary = getStyle(request.data)
                primary = getComp(request.data)
                serializer_data = {}
                serializer_data.update(primary)
                serializer_data.update({"secondary_state": secondary})
                comp_serializer = ComponentSerializer(data=serializer_data)
                if comp_serializer.is_valid():
                    comp_serializer.save(page=page)
                    return Response(status=status.HTTP_200_OK)
                print(comp_serializer.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except Page.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
           return Response(status=status.HTTP_400_BAD_REQUEST)
def sortFunc(entry):
    return entry["page"]

#retrieves all components of a project
class ComponentListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    #get all components of a project
    def get(self, request, project_id, format=None):
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            pages = project.pages.all()
            data = []
            for page in pages:
                components = page.components.all()
                for comp in components:
                    data.append(comp.getData())
            return Response(data=data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
           return Response(status=status.HTTP_404_NOT_FOUND)
    def put(self, request, project_id, format=None):
        #update all components of a project
        user = request.user
        try:
            project = user.projects.get(id=project_id)
            sortedData = sorted(request.data, key=sortFunc)
            groupedPages = itertools.groupby(sortedData, get_key)
            for page_title, group in groupedPages:
                try:
                    page = project.pages.get(title=page_title)
                    for compData in group:
                        try:
                            component = page.components.get(comp_id=compData["id"])
                            component_data = getComp(compData)
                            component_data["secondary_state"] = getStyle(compData)
                            comp_serializer = ComponentSerializer(component, data=component_data)
                            if comp_serializer.is_valid():
                                comp_serializer.save()
                            else:
                                return Response(status=status.HTTP_400_BAD_REQUEST)
                        except Component.DoesNotExist:
                            return Response(status=status.HTTP_400_BAD_REQUEST)
                except Page.DoesNotExist:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        except Project.DoesNotExist:
           return Response(status=status.HTTP_400_BAD_REQUEST)

class SignUpView(APIView):
    def post(self, request, format=None):
        if request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if data["firstPassword"] != data["secondPassword"]:
            return Response(data={"passwordMatch": False}, status=status.HTTP_400_BAD_REQUEST)
        user_data = {"username": data["email"], "email": data["email"], "password": data["firstPassword"]}
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(data=user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)