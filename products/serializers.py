from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Product, ProductImage


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
            max_length=100000,
            allow_empty_file=False,
            use_url=False
        ), 
        write_only=True, 
        required=False
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

        def validate(self, data):
            # Validate uploaded images
            uploaded_images = data.get('uploaded_images', [])
            
            if uploaded_images and len(uploaded_images) > 5:
                raise serializers.ValidationError({
                    "uploaded_images": "You can upload a maximum of 5 images"
                })
            
            return data

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
