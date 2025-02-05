from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class BaseModel(models.Model):
    """
    Base model for all models which includes all the required date fields
    for CRUD operations
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    is_deleted = models.BooleanField(
        default=False,
    )
    deleted_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_%(class)s",
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        force = kwargs.pop("force", False)

        # Actual Delete
        if force:
            return super().delete(*args, **kwargs)

        # Soft Delete
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save()
