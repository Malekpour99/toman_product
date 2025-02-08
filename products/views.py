from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        # Delete associated images from storage
        for image in product.images.all():
            image.delete(user=request.user if request.user.is_authenticated else None)
        product.delete(user=request.user if request.user.is_authenticated else None)
        return Response(status=status.HTTP_204_NO_CONTENT)
