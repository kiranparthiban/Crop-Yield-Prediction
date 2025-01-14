import torch
import json
import os
import wikipediaapi
from torchvision import transforms, models
from PIL import Image


class AIHandler:
    def __init__(self, base_model_dir):
        """
        Initialize the AIHandler by dynamically loading model files and class-to-index mappings.

        Args:
            base_model_dir (str): Base directory where model files and class-to-index JSON files are located.
        """
        self.base_model_dir = base_model_dir
        self.model_name_mapping = {
            "resnet": "ResNet50",
            "mobilenet": "MobileNetV3",
            "efficientnet": "EfficientNet"
        }

        # Load models and mappings dynamically
        self.models = {}
        self.class_to_idx = {}
        self.idx_to_class = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._discover_and_load_models()

        # Preprocessing pipeline for input images
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        # Wikipedia API for retrieving data
        self.wiki_api = wikipediaapi.Wikipedia(
            language='en',
            user_agent="FishClassifier/1.0 (https://github.com/username/fishclassifier)"
        )

    def _discover_and_load_models(self):
        """
        Discover model and class-to-index files in the base directory and load them.
        """
        for short_name, full_name in self.model_name_mapping.items():
            model_file = None
            class_idx_file = None

            # Search for model file and class-to-index file
            for root, _, files in os.walk(self.base_model_dir):
                for file in files:
                    if file.lower() == f"{full_name.lower()}_finetuned.pth":
                        model_file = os.path.join(root, file)
                    if file.lower() == f"{full_name.lower()}_cls_idx.json":
                        class_idx_file = os.path.join(root, file)

            # If both files are found, load them
            if model_file and class_idx_file:
                self._load_model(short_name, full_name, model_file, class_idx_file)
            else:
                missing = []
                if not model_file:
                    missing.append(f"model file ({full_name}_finetuned.pth)")
                if not class_idx_file:
                    missing.append(f"class-to-index file ({full_name}_cls_idx.json)")
                print(f"Warning: Missing {', '.join(missing)} for {full_name}")

    def _load_model(self, short_name, full_name, model_path, class_idx_path):
        """
        Load a model and its class-to-index mapping.

        Args:
            short_name (str): Short name of the model (e.g., 'resnet').
            full_name (str): Full name of the model (e.g., 'ResNet50').
            model_path (str): Path to the model file.
            class_idx_path (str): Path to the class-to-index mapping file.
        """
        print(f"Loading {full_name} from {model_path} and {class_idx_path}")
        
        # Load class-to-index mapping
        with open(class_idx_path, "r") as f:
            self.class_to_idx[short_name] = json.load(f)
            self.idx_to_class[short_name] = {v: k for k, v in self.class_to_idx[short_name].items()}

        # Load model
        if short_name == "resnet":
            model = models.resnet50(pretrained=False)
            model.fc = torch.nn.Linear(model.fc.in_features, len(self.class_to_idx[short_name]))
        elif short_name == "efficientnet":
            model = models.efficientnet_b0(pretrained=False)
            model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(self.class_to_idx[short_name]))
        elif short_name == "mobilenet":
            model = models.mobilenet_v3_large(pretrained=False)
            model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(self.class_to_idx[short_name]))
        else:
            raise ValueError(f"Unsupported model architecture: {short_name}")

        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model = model.to(self.device)
        model.eval()

        self.models[short_name] = model

    def classify(self, image: Image.Image, model_name: str):
        """
        Classify an image using the specified model.

        Args:
            image (PIL.Image.Image): Image to classify.
            model_name (str): Simplified model name (e.g., 'resnet', 'mobilenet', 'efficientnet').

        Returns:
            dict: A dictionary containing the predicted class name and confidence score.
        """
        model_name = model_name.lower()
        if model_name not in self.models:
            return {"error": f"Model '{model_name}' not found. Available models: {list(self.models.keys())}"}

        model = self.models[model_name]

        try:
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
        except Exception as e:
            return {"error": f"Error processing image: {e}"}

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, dim=0)

        predicted_class = self.idx_to_class[model_name][predicted_idx.item()]
        confidence_percentage = confidence.item() * 100
        return {"class_name": predicted_class, "confidence": f"{confidence_percentage:.2f}%"}

    def retrieve_data(self, class_name):
        """
        Retrieve data about the given class name (fish name) using Wikipedia API.

        Args:
            class_name (str): Name of the class (fish species).

        Returns:
            dict: A JSON object with key details about the class.
        """
        try:
            page = self.wiki_api.page(class_name)

            if not page.exists():
                return {"error": f"No data found for {class_name}"}

            return {
                "title": page.title,
                "summary": page.summary[:500],
                "url": page.fullurl
            }
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
