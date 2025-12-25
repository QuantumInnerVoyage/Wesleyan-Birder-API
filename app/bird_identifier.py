import base64
import os
from google import genai
from google.genai import types

WESLEYAN_FIELD_GUIDE_BIRDS = [
    "Northern Cardinal",
    "American Robin",
    "Blue Jay",
    "House Sparrow",
    "European Starling",
    "American Crow",
    "Mourning Dove",
    "Red-tailed Hawk",
    "American Goldfinch",
    "Black-capped Chickadee",
    "White-breasted Nuthatch",
    "Downy Woodpecker",
    "Carolina Wren",
    "Eastern Bluebird",
    "Song Sparrow",
    "Dark-eyed Junco",
]


def get_gemini_client():
    client = genai.Client(
        api_key=os.getenv("AI_INTEGRATIONS_GEMINI_API_KEY"),
        http_options=types.HttpOptions(
            base_url=os.getenv("AI_INTEGRATIONS_GEMINI_BASE_URL")
        ),
    )
    return client


async def identify_bird(image_data: bytes) -> dict:
    client = get_gemini_client()
    
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")
    
    wesleyan_birds_list = ", ".join(WESLEYAN_FIELD_GUIDE_BIRDS)
    
    prompt = f"""You are an expert ornithologist for the Wesleyan Birder app. Analyze this bird image and provide:

1. **Common Name**: The bird's common English name
2. **Scientific Name**: The scientific name in "Genus species" format
3. **Wesleyan Fact**: A fact connecting this bird to Wesleyan University or Connecticut. If this bird is one of the 16 species in the Field Guide to the Birds of Wesleyan ({wesleyan_birds_list}), mention this. The Wesleyan Cardinal is the university mascot, so the Northern Cardinal is especially significant.

Respond in this exact JSON format:
{{
    "common_name": "Bird Common Name",
    "scientific_name": "Genus species",
    "wesleyan_fact": "A Wesleyan-specific fact about this bird",
    "confidence": "high/medium/low",
    "in_wesleyan_field_guide": true/false
}}

If you cannot identify the bird or the image doesn't contain a bird, respond with:
{{
    "common_name": "Unknown",
    "scientific_name": "Unknown",
    "wesleyan_fact": "Unable to identify the bird in this image. Try a clearer photo!",
    "confidence": "none",
    "in_wesleyan_field_guide": false
}}"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
                    types.Part.from_text(text=prompt),
                ],
            )
        ],
    )
    
    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    import json
    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        result = {
            "common_name": "Unknown",
            "scientific_name": "Unknown",
            "wesleyan_fact": "Could not parse the identification result. Please try again.",
            "confidence": "none",
            "in_wesleyan_field_guide": False,
        }
    
    return result
