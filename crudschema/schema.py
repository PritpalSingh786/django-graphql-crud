import os
import shutil
from django.conf import settings
from graphene_file_upload.scalars import Upload as UploadScalar
import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from rest_framework.serializers import ValidationError
from .models import Upload
from .serializers import UploadSerializer


# Reuse Upload model
class UploadType(DjangoObjectType):
    class Meta:
        model = Upload
        fields = ("id", "title", "description", "images", "created_at")


class Query(graphene.ObjectType):
    all_uploads = graphene.List(UploadType)
    upload = graphene.Field(UploadType, id=graphene.Int(required=True))

    def resolve_all_uploads(root, info):
        return Upload.objects.all()

    def resolve_upload(root, info, id):
        return Upload.objects.get(pk=id)


# def save_uploaded_files(uploaded_images, upload_id):
#     folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads', str(upload_id))
#     os.makedirs(folder_path, exist_ok=True)

#     image_paths = []
#     for image in uploaded_images:
#         filepath = os.path.join('uploads', str(upload_id), image.name)
#         full_path = os.path.join(settings.MEDIA_ROOT, filepath)
#         with open(full_path, 'wb+') as f:
#             for chunk in image.chunks():
#                 f.write(chunk)
#         image_paths.append(filepath)
#     return image_paths


class CreateUpload(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=False)
        uploaded_images = graphene.List(UploadScalar, required=False)

    upload = graphene.Field(UploadType)

    def mutate(self, info, title, description="", uploaded_images=None):
        data = {
            "title": title,
            "description": description,
            "uploaded_images": uploaded_images or []
        }

        serializer = UploadSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            upload = serializer.save()
        except ValidationError as e:
            raise GraphQLError(e.detail)

        return CreateUpload(upload=upload)


class UpdateUpload(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String(required=False)
        description = graphene.String(required=False)
        uploaded_images = graphene.List(UploadScalar, required=False)

    upload = graphene.Field(UploadType)

    def mutate(self, info, id, title=None, description=None, uploaded_images=None):
        try:
            instance = Upload.objects.get(pk=id)
        except Upload.DoesNotExist:
            raise GraphQLError("Upload not found.")

        data = {
            "title": title if title is not None else instance.title,
            "description": description if description is not None else instance.description,
        }

        if uploaded_images:
            data["uploaded_images"] = uploaded_images

        serializer = UploadSerializer(instance=instance, data=data)
        try:
            serializer.is_valid(raise_exception=True)
            updated_upload = serializer.save()
        except ValidationError as e:
            raise GraphQLError(e.detail)

        return UpdateUpload(upload=updated_upload)


class DeleteUpload(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    message = graphene.String()

    def mutate(self, info, id):
        try:
            instance = Upload.objects.get(pk=id)
        except Upload.DoesNotExist:
            raise GraphQLError("Upload not found.")

        folder = os.path.join(settings.MEDIA_ROOT, 'uploads', str(instance.id))
        if os.path.exists(folder):
            shutil.rmtree(folder)

        instance.delete()
        return DeleteUpload(message="Upload deleted successfully.")


class Mutation(graphene.ObjectType):
    create_upload = CreateUpload.Field()
    update_upload = UpdateUpload.Field()
    delete_upload = DeleteUpload.Field()

'''
Here is a **complete Postman CRUD setup** for your **GraphQL Django project** using `http://localhost:8000/graphql/` with **form-data for Create** and **raw JSON for Read/Update/Delete**.

---

## 🚀 GRAPHQL CRUD via POSTMAN (localhost:8000/graphql/)

### ✅ BASE URL

```
http://localhost:8000/graphql/
```

---

## 🟢 1. CREATE Upload (POST with form-data)

> Mutation must exist in your GraphQL schema (`createUpload`)

**Postman** → `POST` → `Body` → `raw` → `JSON`

```json
{
  "query": "mutation { createUpload(title: "My First Upload" description: "This is a test upload") {upload {id title description images createdAt } } }"
}
```

**Postman** → `POST` → `Body` → `form-data`

| Key        | Type | Value                                                                                                                                                                                               |
| ---------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| operations | text | `{"query":"mutation($file: Upload!){ createUpload(title:\"My First Upload\", description:\"Test via Postman\", uploadedImages:[$file]){ upload { id title images } } }","variables":{"file":null}}` |
| map        | text | `{"0":["variables.file"]}`                                                                                                                                                                          |
| 0          | file | *(choose an image file from your system)*                                                                                                                                                           |
                                                                                                                                                                                                                                                                                                             | File |

---

## 🔵 2. READ ALL Uploads (GET all)

**Postman** → `POST` → `Body` → `raw` → `JSON`

```json
{
  "query": "query {  allUploads { id title description images createdAt } }"
}
```

---

## 🔵 3. READ Upload by ID

**Postman** → `POST` → `Body` → `raw` → `JSON`

```json
{
  "query": "query {upload(id: 1) {id title description images createdAt}}",

}
```
---

## ✏️ 4. UPDATE Upload by ID (title and description)

> Mutation must exist in your GraphQL schema (`updateUpload`)

**Postman** → `POST` → `Body` → `raw` → `JSON`

```json
{
  "query": "mutation { updateUpload( id: 1 title: "Updated Title" description: "Updated description here") { upload { id title description images createdAt } } }"
}
```
**Postman** → `POST` → `Body` → `form-data`

| Key        | Type | Value                                                                                                                                                                       |
| ---------- | ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| operations | text | `{"query":"mutation($file: Upload!){ updateUpload(id:1, title:\"Updated via Postman\", uploadedImages:[$file]){ upload { id title images } } }","variables":{"file":null}}` |
| map        | text | `{"0":["variables.file"]}`                                                                                                                                                  |
| 0          | file | *(choose an image file from your system)*                                                                                                                                   |


---

## ❌ 5. DELETE Upload by ID

> Mutation must exist in your GraphQL schema (`deleteUpload`)

**Postman** → `POST` → `Body` → `raw` → `JSON`

```json
{
  "query": "mutation deleteUpload($id: ID!) { deleteUpload(id: $id) { success message } }",
  "variables": {
    "id": "1"
  }
}
```




'''
