from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .serializers import PostSerializer
from rest_framework import status


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_PostList(request):
    posts = Post.objects.all().order_by('-pk')
    serializer = PostSerializer(posts, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_Post(request, pk):
    obj = Post.objects.get(pk=pk)

    serializer = PostSerializer(obj)
    return JsonResponse(serializer.data, safe=False)