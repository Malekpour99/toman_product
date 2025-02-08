from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from common.models import BaseModel
from common.utils import normalize_size
from common.const import PRODUCT_IMAGE_MAX_SIZE, PRODUCT_IMAGE_MAX_COUNT


def validate_file_size(value):
    """
    Validates product image file size based on the specified limit
    """
    filesize = value.size
    if filesize > PRODUCT_IMAGE_MAX_SIZE:
        raise ValidationError(
            f"Maximum file size is {normalize_size(PRODUCT_IMAGE_MAX_SIZE)}"
        )


class Product(BaseModel):
    """
    simple model for products:
        title: Product's title 
        price: Product's price
        description: Product's description
    """
    title = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return self.title


class ProductImage(BaseModel):
    """
    Holds associated image file records for each product object
    """
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
        if (
            self.product.images.filter(is_deleted=False).count()
            > PRODUCT_IMAGE_MAX_COUNT
        ):
            raise ValidationError(
                f"A product can have at most {str(PRODUCT_IMAGE_MAX_COUNT)} images."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
