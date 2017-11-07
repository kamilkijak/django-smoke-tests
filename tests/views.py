from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
