from rest_framework import serializers

from common.utils import normalize_size
from .models import Product, ProductImage
from common.const import PRODUCT_IMAGE_MAX_SIZE, PRODUCT_IMAGE_MAX_COUNT


class ProductImageSerializer(serializers.ModelSerializer):
    """
    ProductImage model srializer
    """
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "created_at",
        ]


class EmptyValidatingImageField(serializers.ImageField):
    """
    Customized image filed which prevent getting errors when
    submitting empty lists which should contain images
    """
    def to_internal_value(self, data):
        # If data is None or empty, return None
        if not data:
            return None
        return super().to_internal_value(data)


class ProductSerializer(serializers.ModelSerializer):
    """
    Product model serializer with customized created and update methods
    """
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=EmptyValidatingImageField(
            required=False, allow_empty_file=False, use_url=True
        ),
        required=False,
        write_only=True,
        allow_empty=True,
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "price",
            "description",
            "images",
            "uploaded_images",
            "created_at",
            "updated_at",
        ]

    def validate_uploaded_images(self, value):
        """
        Validates uploaded images
        - data-type: list
        - length < PRODUCT_IMAGE_MAX_SIZE
        - sanitize its values by removing None values
        """
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Invalid format. Expected a list of images."
            )

        if len(value) > PRODUCT_IMAGE_MAX_COUNT:
            raise serializers.ValidationError(
                {"uploaded_images": "You can upload a maximum of 5 images"}
            )

        for image in value:
            if image and image.size > PRODUCT_IMAGE_MAX_SIZE:
                raise serializers.ValidationError(
                    f"Image {image.name} is too large. "
                    f"Maximum size is {normalize_size(PRODUCT_IMAGE_MAX_SIZE)}"
                )

        return [image for image in value if image is not None]

    def create(self, validated_data):
        """
        Creating products and their associated images
        """
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = Product.objects.create(**validated_data)

        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        """
        Updating products and their associated images considering image count limit
        for each product
        """
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
