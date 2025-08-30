from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
import os
import time
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ImageUploadSerializer, PredictionResponseSerializer,
    OCRRequestSerializer, OCRResponseSerializer,
    Model2DRequestSerializer, Model2DResponseSerializer,
    Model3DRequestSerializer, Model3DResponseSerializer,
    GUI2CodeRequestSerializer, GUI2CodeResponseSerializer,
    InterestPointRequestSerializer, InterestPointResponseSerializer
)

# Example placeholder model (replace with your real model)
def dummy_model(image):
    # TODO: load your ML model (e.g. PyTorch/TensorFlow)
    return "cat"  # just a dummy return

def dummy_ocr_model(image, language="eng"):
    # TODO: implement actual OCR model
    return "Sample extracted text from image"

def dummy_2d_detection_model(image):
    # TODO: implement actual 2D object detection
    return [
        {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
        {"class": "car", "confidence": 0.87, "bbox": [300, 150, 450, 250]}
    ]

def dummy_3d_detection_model(image):
    # TODO: implement actual 3D object detection
    return [
        {"class": "chair", "confidence": 0.92, "depth": 2.5, "position": [1.2, 0.8, 2.5]},
        {"class": "table", "confidence": 0.88, "depth": 1.8, "position": [0.5, 0.0, 1.8]}
    ]

def dummy_gui2code_model(image, framework="html"):
    # TODO: implement actual GUI to code conversion
    if framework == "html":
        return """<div class="container">
    <h1>Sample Generated Code</h1>
    <p>This is a sample HTML structure generated from the GUI image.</p>
</div>"""
    elif framework == "react":
        return """import React from 'react';

function GeneratedComponent() {
    return (
        <div className="container">
            <h1>Sample Generated Code</h1>
            <p>This is a sample React component generated from the GUI image.</p>
        </div>
    );
}

export default GeneratedComponent;"""
    else:
        return f"Generated code for {framework} framework"

def dummy_interest_point_model(image, detection_type="corners"):
    # TODO: implement actual interest point detection
    if detection_type == "corners":
        return [
            {"x": 100, "y": 150, "confidence": 0.95},
            {"x": 250, "y": 200, "confidence": 0.92},
            {"x": 400, "y": 300, "confidence": 0.88},
            {"x": 150, "y": 400, "confidence": 0.85}
        ]
    elif detection_type == "edges":
        return [
            {"x": 120, "y": 180, "confidence": 0.94},
            {"x": 280, "y": 220, "confidence": 0.91},
            {"x": 420, "y": 320, "confidence": 0.87}
        ]
    elif detection_type == "blobs":
        return [
            {"x": 110, "y": 160, "confidence": 0.93},
            {"x": 260, "y": 210, "confidence": 0.90},
            {"x": 410, "y": 310, "confidence": 0.86},
            {"x": 160, "y": 410, "confidence": 0.83}
        ]
    else:  # keypoints
        return [
            {"x": 105, "y": 155, "confidence": 0.96},
            {"x": 255, "y": 205, "confidence": 0.93},
            {"x": 405, "y": 305, "confidence": 0.89},
            {"x": 155, "y": 405, "confidence": 0.84},
            {"x": 300, "y": 250, "confidence": 0.82}
        ]

# Template-based views (existing)
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

def interest_point_view(request):
    return render(request, "vision/interest_point.html")

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

# API Views (new)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_upload_and_predict(request):
    """API endpoint for image upload and prediction"""
    start_time = time.time()
    
    serializer = ImageUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Get prediction (replace with actual model)
        prediction = dummy_model(image)
        confidence = 0.95  # Dummy confidence
        
        processing_time = time.time() - start_time
        
        response_data = {
            'prediction': prediction,
            'confidence': confidence,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = PredictionResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_ocr(request):
    """API endpoint for OCR text extraction"""
    start_time = time.time()
    
    serializer = OCRRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        language = serializer.validated_data.get('language', 'eng')
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Extract text (replace with actual OCR model)
        extracted_text = dummy_ocr_model(image, language)
        confidence = 0.92  # Dummy confidence
        
        processing_time = time.time() - start_time
        
        response_data = {
            'extracted_text': extracted_text,
            'confidence': confidence,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = OCRResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'OCR processing failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_model2d(request):
    """API endpoint for 2D object detection"""
    start_time = time.time()
    
    serializer = Model2DRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Detect objects (replace with actual 2D detection model)
        objects = dummy_2d_detection_model(image)
        
        processing_time = time.time() - start_time
        
        response_data = {
            'objects': objects,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = Model2DResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'2D detection failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_model3d(request):
    """API endpoint for 3D object detection"""
    start_time = time.time()
    
    serializer = Model3DRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Detect 3D objects (replace with actual 3D detection model)
        objects_3d = dummy_3d_detection_model(image)
        
        processing_time = time.time() - start_time
        
        response_data = {
            'objects_3d': objects_3d,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = Model3DResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'3D detection failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_gui2code(request):
    """API endpoint for GUI to code conversion"""
    start_time = time.time()
    
    serializer = GUI2CodeRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        framework = serializer.validated_data.get('target_framework', 'html')
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Generate code (replace with actual GUI to code model)
        generated_code = dummy_gui2code_model(image, framework)
        
        processing_time = time.time() - start_time
        
        response_data = {
            'generated_code': generated_code,
            'framework': framework,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = GUI2CodeResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Code generation failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def api_interest_point(request):
    """API endpoint for interest point detection"""
    start_time = time.time()
    
    serializer = InterestPointRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        image = serializer.validated_data['image']
        detection_type = serializer.validated_data.get('detection_type', 'corners')
        
        # Save image
        file_path = default_storage.save(f'uploads/{image.name}', image)
        image_url = settings.MEDIA_URL + file_path
        
        # Detect interest points (replace with actual interest point detection model)
        points = dummy_interest_point_model(image, detection_type)
        
        processing_time = time.time() - start_time
        
        response_data = {
            'points': points,
            'detection_type': detection_type,
            'image_url': image_url,
            'processing_time': round(processing_time, 3)
        }
        
        response_serializer = InterestPointResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Interest point detection failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def api_health_check(request):
    """Health check endpoint for API status"""
    return Response({
        'status': 'healthy',
        'message': 'CV API is running',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
