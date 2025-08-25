from rest_framework import serializers


class ImageUploadSerializer(serializers.Serializer):
    """Serializer for image upload requests"""
    image = serializers.ImageField(
        help_text="Upload an image file (JPEG, PNG, etc.)",
        max_length=255,
        allow_empty_file=False
    )
    
    def validate_image(self, value):
        """Validate the uploaded image"""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("Image file too large. Maximum size is 10MB.")
        return value


class PredictionResponseSerializer(serializers.Serializer):
    """Serializer for prediction responses"""
    prediction = serializers.CharField(help_text="The predicted class or result")
    confidence = serializers.FloatField(help_text="Confidence score (0.0 to 1.0)")
    image_url = serializers.URLField(help_text="URL to the uploaded image")
    processing_time = serializers.FloatField(help_text="Time taken for prediction in seconds")


class OCRRequestSerializer(serializers.Serializer):
    """Serializer for OCR requests"""
    image = serializers.ImageField(
        help_text="Upload an image containing text to extract",
        max_length=255,
        allow_empty_file=False
    )
    language = serializers.CharField(
        max_length=10,
        default="eng",
        help_text="Language code for OCR (e.g., 'eng' for English)"
    )


class OCRResponseSerializer(serializers.Serializer):
    """Serializer for OCR responses"""
    extracted_text = serializers.CharField(help_text="Extracted text from the image")
    confidence = serializers.FloatField(help_text="Overall confidence score")
    image_url = serializers.URLField(help_text="URL to the uploaded image")
    processing_time = serializers.FloatField(help_text="Time taken for OCR in seconds")


class Model2DRequestSerializer(serializers.Serializer):
    """Serializer for 2D model requests"""
    image = serializers.ImageField(
        help_text="Upload an image for 2D object detection",
        max_length=255,
        allow_empty_file=False
    )


class Model2DResponseSerializer(serializers.Serializer):
    """Serializer for 2D model responses"""
    objects = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of detected objects with bounding boxes and classes"
    )
    image_url = serializers.URLField(help_text="URL to the uploaded image")
    processing_time = serializers.FloatField(help_text="Time taken for detection in seconds")


class Model3DRequestSerializer(serializers.Serializer):
    """Serializer for 3D model requests"""
    image = serializers.ImageField(
        help_text="Upload an image for 3D object detection",
        max_length=255,
        allow_empty_file=False
    )


class Model3DResponseSerializer(serializers.Serializer):
    """Serializer for 3D model responses"""
    objects_3d = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of detected 3D objects with depth information"
    )
    image_url = serializers.URLField(help_text="URL to the uploaded image")
    processing_time = serializers.FloatField(help_text="Time taken for 3D detection in seconds")


class GUI2CodeRequestSerializer(serializers.Serializer):
    """Serializer for GUI to code conversion requests"""
    image = serializers.ImageField(
        help_text="Upload a screenshot of a GUI to convert to code",
        max_length=255,
        allow_empty_file=False
    )
    target_framework = serializers.ChoiceField(
        choices=[
            ('html', 'HTML/CSS'),
            ('react', 'React'),
            ('vue', 'Vue.js'),
            ('flutter', 'Flutter'),
            ('swift', 'Swift UI'),
        ],
        default='html',
        help_text="Target framework for code generation"
    )


class GUI2CodeResponseSerializer(serializers.Serializer):
    """Serializer for GUI to code conversion responses"""
    generated_code = serializers.CharField(help_text="Generated code for the GUI")
    framework = serializers.CharField(help_text="Target framework used")
    image_url = serializers.URLField(help_text="URL to the uploaded image")
    processing_time = serializers.FloatField(help_text="Time taken for code generation in seconds")
