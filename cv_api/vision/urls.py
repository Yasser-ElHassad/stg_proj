from django.urls import path
from .views import (
    home_view, api_upload_and_predict, api_ocr, api_model2d, api_model3d,
    api_gui2code, api_health_check, api_interest_point
)

urlpatterns = [
    # API URLs
    path(" ", home_view, name="home"),
    path("health/", api_health_check, name="api_health"),
    path("predict/", api_upload_and_predict, name="api_predict"),
    path("ocr/", api_ocr, name="api_ocr"),
    path("2d/", api_model2d, name="api_2d"),
    path("3d/", api_model3d, name="api_3d"),
    path("gui2code/", api_gui2code, name="api_gui2code"),
    path("interest-point/", api_interest_point, name="api_interest_point"),
]
