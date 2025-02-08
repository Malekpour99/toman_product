from django.db import transaction

from rest_framework.response import Response
from rest_framework import viewsets, status, serializers
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product, ProductImage
from .serializers import ProductSerializer
from common.const import PRODUCT_IMAGE_MAX_COUNT


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle new images
        current_images_count = instance.images.count()
        if current_images_count + len(uploaded_images) > PRODUCT_IMAGE_MAX_COUNT:
            raise serializers.ValidationError(
                f"Total number of images cannot exceed {str(PRODUCT_IMAGE_MAX_COUNT)}"
            )

        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)

        return instance

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        # Delete associated images from storage
        for image in product.images.all():
            image.delete(user=request.user if request.user.is_authenticated else None)
        product.delete(user=request.user if request.user.is_authenticated else None)
        return Response(status=status.HTTP_204_NO_CONTENT)
