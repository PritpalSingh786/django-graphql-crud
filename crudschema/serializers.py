from rest_framework import serializers
from .models import Upload
from django.core.files.storage import default_storage
from django.conf import settings
import os
import shutil

class UploadSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Upload
        fields = ['id', 'title', 'description', 'images', 'uploaded_images', 'created_at']
        read_only_fields = ['images', 'created_at']

    def validate_uploaded_images(self, images):
        allowed_extensions = ['.jpg', '.jpeg', '.png']
        for image in images:
            if image.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Each image must be ≤ 5MB.")
            if not image.content_type.startswith("image/"):
                raise serializers.ValidationError("Only image files are allowed.")
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"Invalid file extension: {ext}. Allowed: .jpg, .jpeg, .png")
        return images

    def save_images(self, uploaded_images, upload_id):
        image_paths = []
        folder_path = os.path.join('uploads', str(upload_id))

        # Ensure the folder exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, folder_path), exist_ok=True)

        for image in uploaded_images:
            filename = default_storage.save(os.path.join(folder_path, image.name), image)
            image_paths.append(filename)
        return image_paths

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Temporarily save the instance to get the ID
        upload = Upload.objects.create(**validated_data)

        # Save images to the specific folder
        if uploaded_images:
            image_paths = self.save_images(uploaded_images, upload.id)
            upload.images = image_paths
            upload.save()

        return upload

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])

        if uploaded_images:
            # Clear old images from folder
            folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', str(instance.id))
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            # Save new images
            image_paths = self.save_images(uploaded_images, instance.id)
            instance.images = image_paths

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance