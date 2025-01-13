import random

class Classify:
    def run(self, image_path):
        # Placeholder classification logic
        species = random.choice(['Clownfish', 'Great White Shark', 'Blue Tang'])
        description = f"{species} is a marine species known for its unique appearance."
        return {
            'species_name': species,
            'description': description,
        }
