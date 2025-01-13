import os
import logging
from PIL import Image
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import MarineSpecies
from .serializers import MarineSpeciesSerializer
from .ai_handler import AIHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Initialize logger for debugging
logger = logging.getLogger(__name__)

# Directory to save uploaded images
UPLOAD_DIR = 'uploads/'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize AIHandler
model_path = "model/resnet50_model_finetuned.pth"
class_to_idx_path = "model/class_to_idx.json"
try:
    ai_handler = AIHandler(model_path, class_to_idx_path)
    logger.info("AIHandler initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize AIHandler: {e}")

@api_view(['POST'])
def upload_image(request):
    """
    Upload an image and classify the fish species.
    """
    try:
        # Retrieve the uploaded image
        image_file = request.FILES.get('image')
        if not image_file:
            logger.error("No image provided in the request.")
            return JsonResponse({'error': 'No image provided'}, status=400)

        # Generate a sequential ID for the image
        last_entry = MarineSpecies.objects.last()
        image_id = str(int(last_entry.image_id) + 1) if last_entry else "1"
        logger.info(f"Generated Image ID: {image_id}")

        '''# Save the uploaded image to the server
        image_path = os.path.join(UPLOAD_DIR, f"{image_id}.jpg")
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)
        logger.info(f"Image saved at: {image_path}")'''

        # Save the uploaded image to the media/uploads directory
        image_path = os.path.join(MEDIA_ROOT, 'uploads', f"{image_id}.jpg")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)



        # Open the image for classification
        try:
            image = Image.open(image_path)
        except Exception as e:
            logger.error(f"Failed to open image: {e}")
            return JsonResponse({'error': f'Failed to open image: {e}'}, status=400)

        # Classify the image
        classification = ai_handler.classify(image)
        if "error" in classification:
            logger.error(f"Classification error: {classification['error']}")
            return JsonResponse({'error': classification["error"]}, status=500)

        class_name = classification["class_name"]
        confidence = classification["confidence"]
        logger.info(f"Classification Result - Class: {class_name}, Confidence: {confidence}")

        # Retrieve data about the species
        species_data = ai_handler.retrieve_data(class_name)
        logger.info(f"Retrieved species data: {species_data}")

        # Save the classification result to the database
        species_entry = MarineSpecies.objects.create(
            image_id=image_id,
            class_name=class_name,
            image=image_file,  # Save the uploaded image
            summary=species_data.get('summary', 'No summary available'),
            url=species_data.get('url', 'No URL available')
        )
        logger.info(f"Saved entry to database for Image ID: {image_id}")

        return JsonResponse({
            'image_id': species_entry.image_id,
            'class_name': species_entry.class_name,
            'confidence': confidence,
            'summary': species_entry.summary,
            'url': species_entry.url
        }, status=201)

    except Exception as e:
        logger.error(f"Unexpected error in upload_image: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

@api_view(['GET', 'DELETE'])
def history(request):
    """
    View or delete the history of classified images.
    """
    try:
        if request.method == 'GET':
            species_entries = MarineSpecies.objects.all().order_by('-image_id')
            serializer = MarineSpeciesSerializer(species_entries, many=True)
            logger.info(f"Retrieved {len(species_entries)} history entries.")
            return JsonResponse(serializer.data, safe=False, status=200)

        elif request.method == 'DELETE':
            image_id = request.data.get('image_id')
            if not image_id:
                logger.error("No Image ID provided for deletion.")
                return JsonResponse({'error': 'Image ID is required for deletion'}, status=400)

            try:
                species_entry = MarineSpecies.objects.get(image_id=image_id)
                os.remove(species_entry.image.path)  # Delete the associated image file
                species_entry.delete()
                logger.info(f"Deleted entry and file for Image ID: {image_id}")
                return JsonResponse({'message': f'Image {image_id} deleted successfully'}, status=200)
            except MarineSpecies.DoesNotExist:
                logger.error(f"Image ID not found: {image_id}")
                return JsonResponse({'error': 'Image ID not found'}, status=404)

    except Exception as e:
        logger.error(f"Unexpected error in history endpoint: {e}")
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)


def home(request):
    """
    Home endpoint for the API.
    """
    logger.info("Home endpoint accessed.")
    return JsonResponse({'message': 'Welcome to the OceanID API!'}, status=200)
