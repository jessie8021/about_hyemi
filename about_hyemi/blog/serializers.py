from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Post, Category, Tag, Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    post = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = '__all__'

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    postCount = serializers.SerializerMethodField(method_name='get_PostCount')
    post = serializers.HyperlinkedRelatedField(many=True, view_name='blog:post-detail', read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug',  'postCount', 'post']

    def get_PostCount(self, obj):
        return obj.post.model.objects.filter(category=obj.pk).count()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


