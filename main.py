from tkinter import Tk, filedialog
from utils.vision import generate_vision_explanation
from utils.io_utils import load_dataset
from utils.classifier import train_text_classifier
from utils.feedback import handle_image_feedback
from config import DATASET_PATH

if __name__ == "__main__":
    print("📸 Please select an image.")
    root = Tk()
    root.attributes('-topmost', True)
    root.withdraw()
    image_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    root.destroy()

    if not image_path:
        print("❌ No image selected.")
        exit()

    print(f"✅ Image selected: {image_path}")
    final_message, description = generate_vision_explanation(image_path)
   # train_text_classifier()
    handle_image_feedback(image_path, description, final_message)
