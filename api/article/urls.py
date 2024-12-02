from django.urls import path
from .views import ArticleListCreateView, ArticleDetailView, ArticleFileUploadView, CommentCreateView, ArticleFileDeleteView, CommentDeleteEditView

urlpatterns = [
    path('article/', ArticleListCreateView.as_view(), name="article-list-create"),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name="article-detail"),
    path('article/<int:article_id>/upload-file/', ArticleFileUploadView.as_view(), name="article-file-uppload"),
    path('article/<int:article_id>/comment/', CommentCreateView.as_view(), name='comment-create'),
    path('article/<int:article_id>/delete-files/', ArticleFileDeleteView.as_view(), name='articleFile-delete'),
    path('article/<int:article_id>/delete-edit-comments/', CommentDeleteEditView.as_view(), name='comment-delete-edit')
]