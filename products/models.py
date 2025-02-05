from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from common.models import BaseModel
from common.utils import normalize_size
from common.const import PRODUCT_IMAGE_MAX_SIZE


def validate_file_size(value):
    filesize = value.size
    if filesize > PRODUCT_IMAGE_MAX_SIZE:
        raise ValidationError(
            f"Maximum file size is {normalize_size(PRODUCT_IMAGE_MAX_SIZE)}"
        )


class Product(BaseModel):
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to="products/",
        validators=[
            validate_file_size,
            FileExtensionValidator(
                [
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                ]
            ),
        ],
    )

    def clean(self):
        super().clean()
        if self.product.images.filter(is_deleted=False).count() > 5:
            raise ValidationError("A product can have at most 5 images.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
