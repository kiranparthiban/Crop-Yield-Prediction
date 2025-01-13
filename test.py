import torch
import json
import wikipediaapi
from torchvision import transforms
from PIL import Image
from rich.console import Console
from rich.table import Table


class AIHandler:
    def __init__(self, model_path, class_to_idx_path):
        """
        Initialize the AIHandler with the trained model and class-to-index mapping.

        Args:
            model_path (str): Path to the saved model file.
            class_to_idx_path (str): Path to the class-to-index mapping JSON file.
        """
        # Load the class-to-index mapping
        with open(class_to_idx_path, "r") as f:
            self.class_to_idx = json.load(f)

        # Reverse mapping from index to class
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}

        # Initialize and load the model
        self.num_classes = len(self.class_to_idx)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)

        # Preprocessing pipeline for input image
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),  # Resize image to match model input size
            transforms.ToTensor(),         # Convert image to PyTorch tensor
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # Normalize using ImageNet mean and std
        ])

        # Wikipedia API for retrieving data with a proper user agent
        self.wiki_api = wikipediaapi.Wikipedia(
            language='en',
            user_agent="FishClassifier/1.0 (https://github.com/username/fishclassifier)"
        )

    def _load_model(self, model_path):
        """
        Load the trained model.

        Args:
            model_path (str): Path to the saved model file.

        Returns:
            torch.nn.Module: The loaded model.
        """
        class ResNet50Model(torch.nn.Module):
            def __init__(self, num_classes):
                super(ResNet50Model, self).__init__()
                self.model = torch.hub.load("pytorch/vision:v0.10.0", "resnet50", weights=None)
                self.model.fc = torch.nn.Linear(self.model.fc.in_features, num_classes)

            def forward(self, x):
                return self.model(x)

        model = ResNet50Model(self.num_classes).to(self.device)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        return model

    def classify(self, image_path):
        """
        Classify an image and return the predicted class name and confidence score.

        Args:
            image_path (str): Path to the image file.

        Returns:
            dict: A dictionary containing the predicted class name and confidence score.
        """
        try:
            image = Image.open(image_path).convert("RGB")  # Load image and convert to RGB
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)  # Preprocess image
        except Exception as e:
            return {"error": f"Error processing image: {e}"}

        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)  # Apply softmax to get probabilities
            confidence, predicted_idx = torch.max(probabilities, dim=0)

        predicted_class = self.idx_to_class[predicted_idx.item()]
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
                "summary": page.summary[:500],  # Limit summary to 500 characters
                "url": page.fullurl
            }
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}


def main():
    console = Console()

    # Initialize the AIHandler
    model_path = "resnet50_model_finetuned.pth"
    class_to_idx_path = "class_to_idx.json"
    handler = AIHandler(model_path, class_to_idx_path)

    console.print("[bold cyan]Fish Species Classifier[/bold cyan]")
    console.print("[bold green]Type 'exit' to quit the program.[/bold green]\n")

    while True:
        # Get the image path from the user
        image_path = input("Enter the path to the image file: ").strip()

        if image_path.lower() == "exit":
            console.print("[bold red]Exiting the program. Goodbye![/bold red]")
            break

        if not image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            console.print("[bold yellow]Invalid input. Please enter a valid image file path.[/bold yellow]\n")
            continue

        # Classify the image
        console.print(f"[bold cyan]Classifying the image: [green]{image_path}[/green][/bold cyan]")
        classification_result = handler.classify(image_path)
        if "error" in classification_result:
            console.print(f"[bold red]{classification_result['error']}[/bold red]")
            continue

        class_name = classification_result["class_name"]
        confidence = classification_result["confidence"]

        console.print(f"\n[bold yellow]Prediction Result[/bold yellow]")
        console.print(f"[bold green]Predicted Class:[/bold green] {class_name}")
        console.print(f"[bold green]Confidence:[/bold green] {confidence}")

        # Retrieve data about the class
        console.print(f"\n[bold cyan]Fetching data about {class_name} from Wikipedia...[/bold cyan]")
        data = handler.retrieve_data(class_name)

        if "error" in data:
            console.print(f"[bold red]{data['error']}[/bold red]")
        else:
            table = Table(title=f"Information about {class_name}")
            table.add_column("Field", style="bold cyan")
            table.add_column("Details", style="white")

            table.add_row("Title", data["title"])
            table.add_row("Summary", data["summary"])
            table.add_row("More Info", data["url"])
            console.print(table)
        console.print("\n")


if __name__ == "__main__":
    main()
