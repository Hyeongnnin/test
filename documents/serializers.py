from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument


class DocumentTemplateSerializer(serializers.ModelSerializer):
	class Meta:
		model = DocumentTemplate
		fields = "__all__"


class GeneratedDocumentSerializer(serializers.ModelSerializer):
	# optional upload field handled in the view
	file = serializers.FileField(write_only=True, required=False)

	template = serializers.PrimaryKeyRelatedField(queryset=DocumentTemplate.objects.all(), allow_null=True, required=False)

	class Meta:
		model = GeneratedDocument
		fields = (
			"id",
			"template",
			"user",
			"employee",
			"consultation",
			"filled_data_json",
			"file_url",
			"file",
			"status",
			"created_at",
		)
		read_only_fields = ("user", "created_at", "file_url")
