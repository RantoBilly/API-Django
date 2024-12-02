from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Article, ArticleFile, Comment
from .serializers import ArticleSerializer, ArticleFileSerializer, CommentSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class ArticleListCreateView(APIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        articles = Article.objects.all()
        serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleDetailView(APIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk):
        try:
            return Article.objects.get(pk=pk)
        except Article.DoesNotExists:
            return None

    def get(self, request, pk):
        article = self.get_objects(pk)
        if article is None:
            return Response({"error": "article not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(article)
        return Response(serializer.data)

    def delete(self, request, pk):
        article = self.get_objects(pk)
        if article is None:
            return Response({"error": "article not found"}, status=status.HTTP_404_NOT_FOUND)
        if article.user != request.user:
            return Response({"error": "You can only delete your own articles"}, status=status.HTTP_403_FORBIDDEN)
        article.delete()
        return Response({"message": "article deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        article = self.get_objects(pk)
        if article is None:
            return Response({"error": "article not found"}, status=status.HTTP_404_NOT_FOUND)
        if article.user != request.user:
            return Response({"error": "you can only edit your own articles."}, status=status.HTTP_403_FORBIDDEN)
        serializer =self.serializer_class(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleFileUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "article not found"}, status=404)
        if article.user != request.user:
            return Response({"error": "You can only upload files to your own articles."}, status=status.HTTP_403_FORBIDDEN)

        files = request.FILES.getlist('file')

        if 'file' not in request.FILES:
            return Response({"error": "no provided files"}, status=400)

        uploaded_file_data = []
        for file in files:
            article_file = ArticleFile.objects.create(article=article, file=file)
            uploaded_file_data.append({
                "id":article_file.id,
                "file": article_file.file.url,
            })

        return Response({
            "message": "files uploaded successfully",
            "files":uploaded_file_data
        }, status=201)


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        article = Article.objects.get(id=article_id)
        if article.user == request.user:
            return Response({"error": "You cannot comment your own article."}, status=status.HTTP_403_FORBIDDEN)
        comment_serializer = CommentSerializer(data=request.data)
        if comment_serializer.is_valid():
            comment_serializer.save(user=request.user, article=article)
            return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
        return Response(comment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleFileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, article_id):
        # check if the article exists
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "article not found"}, status=status.HTTP_404_NOT_FOUND)

        if article.user != request.user:
            return Response({"error": "You can only delete images from your articles"}, status=status.HTTP_403_FORBIDDEN)

        # get the list of  file IDs to delete
        files_id = request.data.get('file_ids', [])
        if not files_id:
            return Response({"error": "No file Ids provided"}, status=status.HTTP_400_BAD_REQUEST)

        # filter the files by the provided IDs and ensure they belong to the articles
        files_to_delete = ArticleFile.objects.filter(id__in=files_id, article=article)

        if not files_to_delete.exists():
            return Response({"error": "No valid files found for deletion"}, status=status.HTTP_404_NOT_FOUND)

        # deleting the files
        deleted_count = files_to_delete.count()
        files_to_delete.delete()

        return Response({
            "message": f"{deleted_count} file(s) deleted successfully !"
        }, status=status.HTTP_200_OK)


class CommentDeleteEditView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "article not found"})

        if article.user == request.user:
            return Response({"error": "No comments from you in your own article"}, status=status.HTTP_404_NOT_FOUND)

        comment_id = request.data.get('comment_id')
        comment_to_delete = Comment.objects.filter(article=article, user=request.user, id=comment_id)

        if not comment_to_delete.exists():
            return Response({"error": "invalid comment or it is not yours"}, status=status.HTTP_403_FORBIDDEN)

        comment_to_delete.delete()
        return Response({"message": "comment deleted successfully"}, status=status.HTTP_200_OK)

    def put(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "article not found"})

        if article.user == request.user:
            return Response({"error": "No comments from you in your own article"}, status=status.HTTP_404_NOT_FOUND)

        comment_id = request.data.get('comment_id')
        new_content = request.data.get('content')

        if not new_content:
            return Response({"error": "New content is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            comment_to_edit = Comment.objects.get(article=article, user=request.user, id=comment_id)
        except Comment.DoesNotExist:
            return Response({"error": "invalid comment or it is not yours"}, status=status.HTTP_403_FORBIDDEN)

        comment_to_edit.content = new_content
        comment_to_edit.save()

        return Response({"message": "comment edited successfully !"}, status=status.HTTP_200_OK)

