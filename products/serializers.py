from rest_framework import serializers

from common.utils import normalize_size
from .models import Product, ProductImage
from common.const import PRODUCT_IMAGE_MAX_SIZE, PRODUCT_IMAGE_MAX_COUNT


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
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
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Invalid format. Expected a list of images."
            )

        if len(value) > PRODUCT_IMAGE_MAX_COUNT:
            raise serializers.ValidationError(
                {"uploaded_images": "You can upload a maximum of 5 images"}
            )

        for image in value:
            if image.size > PRODUCT_IMAGE_MAX_SIZE:
                raise serializers.ValidationError(
                    f"Image {image.name} is too large. "
                    f"Maximum size is {normalize_size(PRODUCT_IMAGE_MAX_SIZE)}"
                )
        return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])
        product = Product.objects.create(**validated_data)

        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images", [])

        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle new images
        current_images_count = instance.images.count()
        if current_images_count + len(uploaded_images) > 5:
            raise serializers.ValidationError("Total number of images cannot exceed 5")

        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)

        return instance
