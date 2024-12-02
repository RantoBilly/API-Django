from rest_framework import serializers
from .models import Article, ArticleFile, Comment


class ArticleFileSerializer(serializers.ModelSerializer):
    # file = serializers.SerializerMethodField()  # ensuring that it returns the full file URL

    class Meta:
        model = ArticleFile
        fields = ['id', 'file']

    def create(self, validated_data):
        file = validated_data.get('file')
        if not file:
            raise serializers.ValidationError({"file": "no file uploaded"})
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_email', 'content', 'created_at']


class ArticleSerializer(serializers.ModelSerializer):
    files = ArticleFileSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'user_email', 'title', 'comment', 'files', 'comments', 'created_at']