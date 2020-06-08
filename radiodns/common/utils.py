from io import BytesIO
import uuid

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


def scale_image(image, width, height):
    new_image = Image.open(image)
    new_image.thumbnail((width, height),)
    buffer = BytesIO()
    new_image.save(fp=buffer, format="JPEG")
    pillow_img = ContentFile(buffer.getvalue())
    img_name = f"{uuid.uuid4()}.jpg"
    return InMemoryUploadedFile(
        pillow_img,  # file
        None,  # field_name
        img_name,  # file name
        "image/jpeg",  # content_type
        pillow_img.tell,  # size
        None,
    )
