from django.urls import path
from .views import upload_and_predict, ocr_view, model2d_view, model3d_view, gui2code_view, home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("upload/", upload_and_predict, name="upload"),
    path("ocr/", ocr_view, name="ocr"),
    path("2d/", model2d_view, name="model2d"),
    path("3d/", model3d_view, name="model3d"),
    path("gui2code/", gui2code_view, name="gui2code"),
]
