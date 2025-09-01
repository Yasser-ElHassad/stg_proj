from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
import os
import time, json, cv2, numpy as np
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.urls import reverse
from .cv_models.pointinteret import InterestPointExtractor

# # Template-based views 
def home_view(request):
    return render(request, "vision/home.html")

def ocr_view(request):
    return render(request, "vision/ocr.html")

def model2d_view(request):
    return render(request, "vision/model2d.html")

def model3d_view(request):
    return render(request, "vision/model3d.html")

def gui2code_view(request):
    return render(request, "vision/gui2code.html")


def upload_and_predict(request):
    prediction = None
    uploaded_image_url = None
    
    if request.method == "POST" and request.FILES.get("image"):
        img_file = request.FILES["image"]
        file_path = default_storage.save(f'uploads/{img_file.name}', img_file)
        prediction = "cat"
        uploaded_image_url = settings.MEDIA_URL + file_path

    return render(request, "vision/upload.html", 
                  {"prediction": prediction,
                  "uploaded_image_url": uploaded_image_url})




def interest_point_view(request):
    context = {}
    
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            
            # Read the file content
            file_bytes = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("Could not read the image file")
            
            # Save original image for reference
            file_path = default_storage.save(f'uploads/interest_points/{image_file.name}', image_file)
            image_file.seek(0)
            
            # Use the InterestPointExtractor model
            extractor = InterestPointExtractor()
            results = extractor.process_image(img)
            
            # Debug the results
            print("Type of results:", type(results))
            print("Results value:", results)
            
            # Check if results is a dictionary
            if not isinstance(results, dict):
                raise ValueError(f"Model returned {type(results)} instead of dictionary: {results}")
            
            context = {
                'points': results.get('points', []),
                'image_url': settings.MEDIA_URL + results.get('output_image_path', ''),
                'processing_time': results.get('processing_time', 0),
                'success': True
            }
            
        except Exception as e:
            print("Error occurred:", str(e))
            import traceback
            print("Traceback:", traceback.format_exc())
            context = {'error': str(e)}
    
    return render(request, 'vision/interest_point.html', context)