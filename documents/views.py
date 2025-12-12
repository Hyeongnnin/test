from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.files.storage import default_storage
import os

from .models import DocumentTemplate, GeneratedDocument
from .serializers import DocumentTemplateSerializer, GeneratedDocumentSerializer


class DocumentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
	"""Read-only viewset for available document templates."""
	queryset = DocumentTemplate.objects.filter(is_active=True)
	serializer_class = DocumentTemplateSerializer
	permission_classes = [IsAuthenticated]


class GeneratedDocumentViewSet(viewsets.ModelViewSet):
	"""CRUD for user-generated documents. Users can only access their own documents."""
	serializer_class = GeneratedDocumentSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		user = self.request.user
		return GeneratedDocument.objects.filter(user=user).order_by("-created_at")

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		# extract file if provided
		upload_file = serializer.validated_data.pop("file", None)
		instance = serializer.save(user=request.user)

		if upload_file:
			upload_path = os.path.join("documents", str(request.user.id), upload_file.name)
			saved_path = default_storage.save(upload_path, upload_file)
			# build accessible URL (MEDIA_URL + saved_path)
			file_url = settings.MEDIA_URL.rstrip("/") + "/" + saved_path.replace("\\", "/")
			instance.file_url = file_url
			instance.save()

		out_serializer = self.get_serializer(instance)
		return Response(out_serializer.data, status=status.HTTP_201_CREATED)

	def update(self, request, *args, **kwargs):
		partial = kwargs.pop("partial", False)
		instance = self.get_object()
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		upload_file = serializer.validated_data.pop("file", None)
		instance = serializer.save()

		if upload_file:
			upload_path = os.path.join("documents", str(request.user.id), upload_file.name)
			saved_path = default_storage.save(upload_path, upload_file)
			file_url = settings.MEDIA_URL.rstrip("/") + "/" + saved_path.replace("\\", "/")
			instance.file_url = file_url
			instance.save()

		out_serializer = self.get_serializer(instance)
		return Response(out_serializer.data)
