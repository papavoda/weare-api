from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_image_extension(value):
    valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
    ext = str(value).split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(_('Invalid file extension. Allowed extensions are .jpg, .jpeg, .png, .gif'))

def validate_video_extension(value):
    valid_extensions = ['mp4']
    ext = str(value).split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(_('Invalid file extension. Allowed extensions are .mp4'))
