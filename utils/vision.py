import time
from groq import Groq
from config import GROQ_API_KEY
from .audio import convert_text_to_speech
from .io_utils import save_to_csv, encode_image

def generate_vision_explanation(image_path: str):
    client = Groq(api_key=GROQ_API_KEY)
    image_base64 = encode_image(image_path)

    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Describe the image as you are explaining to a normal person. "
                                    "Do not use any special characters. Mention obstacles clearly and suggest how to avoid them."
                                )
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=1,
                max_completion_tokens=500,
                top_p=1,
                stream=False
            )
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)
    else:
        print("❌ Failed to generate description.")
        return "Description not available", ""

    description = completion.choices[0].message.content
    final_message = description  # You can enhance this with obstacle parsing logic
    save_to_csv(image_path, description)
    return final_message, description
