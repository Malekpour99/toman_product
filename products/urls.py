from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

app_name = "products"

router = DefaultRouter()
router.register("", ProductViewSet, basename="products")
urlpatterns = router.urls
