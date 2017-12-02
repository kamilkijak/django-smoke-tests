from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet


def simple_method_view(request, parameter=None):
    return HttpResponse()


@permission_classes((IsAuthenticated,))
def view_with_drf_auth(request):
    return HttpResponse()


class ViewWithDRFAuth(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, *args, **kwargs):
        return Response()


@login_required
def view_with_django_auth(request):
    return HttpResponse()


class SimpleViewSet(ViewSet):

    def list(self, request):
        return Response([])

    def create(self, request):
        return Response(status=HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        return Response()

    def update(self, request, pk=None):
        return Response()

    def destroy(self, request, pk=None):
        Response(status=HTTP_204_NO_CONTENT)


def skipped_view(request):
    return HttpResponse()
