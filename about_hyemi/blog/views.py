from .models import Post, Category, Tag, Comment

from django.http import HttpResponse, JsonResponse

from .serializers import PostSerializer, CategorySerializer, TagSerializer, CommentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status

# Mixins
from rest_framework import generics
from rest_framework import mixins

#ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

'''
API View 클래스 사용(CBV)
'''
class PostList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PostSerializer(Post.objects.all().order_by('-pk'), context={'request': request}, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PostDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        post.delete()

        return Response(status = status.HTTP_204_NO_CONTENT)

'''
generics APIView
'''
class CategoryList(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request)

    def post(self, request, *args, **kwargs):
        return self.create(request)

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


'''
@api_view (FBV) 
'''
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_postsCategory(request, category):
    queryset = Post.objects.filter(category=category)
    serializer = PostSerializer(queryset, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_postsTag(request, tag):
    queryset = Post.objects.filter(tags=tag)
    serializer = PostSerializer(queryset, many=True)
    return Response(serializer.data)

'''
ViewSet
'''
class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


'''
Mixin
'''
class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

