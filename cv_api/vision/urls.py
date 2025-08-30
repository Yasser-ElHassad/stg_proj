from django.urls import path
from django.shortcuts import render
from .views import (
    upload_and_predict, ocr_view, model2d_view, model3d_view, gui2code_view, home_view, interest_point_view,
    api_upload_and_predict, api_ocr, api_model2d, api_model3d, api_gui2code, api_health_check, api_interest_point
)

urlpatterns = [
    # Template-based URLs (existing)
    path("", home_view, name="home"),
    path("upload/", upload_and_predict, name="upload"),
    path("ocr/", ocr_view, name="ocr"),
    path("2d/", model2d_view, name="model2d"),
    path("3d/", model3d_view, name="model3d"),
    path("gui2code/", gui2code_view, name="gui2code"),
    path("interest-point/", interest_point_view, name="interest_point"),
    path("api-docs/", lambda request: render(request, "vision/api_docs.html"), name="api_docs"),
    
    # API URLs (new)
    path("api/health/", api_health_check, name="api_health"),
    path("api/predict/", api_upload_and_predict, name="api_predict"),
    path("api/ocr/", api_ocr, name="api_ocr"),
    path("api/2d/", api_model2d, name="api_2d"),
    path("api/3d/", api_model3d, name="api_3d"),
    path("api/gui2code/", api_gui2code, name="api_gui2code"),
    path("api/interest-point/", api_interest_point, name="api_interest_point"),
]
