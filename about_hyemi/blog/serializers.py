from rest_framework import serializers
from .models import Post, Category

class PostSerializer(serializers.ModelSerializer):

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

