# utils.py
import json

from PIL import Image, ImageOps, TiffImagePlugin
from moviepy.editor import VideoFileClip

# import moviepy
# print('moviepy:', moviepy.__version__)
# print('ffmpeg :', moviepy.config.FFMPEG_BINARY)

def resize_image(image_path, max_size=(500, 500), overwrite=False):
    # False -> create new image; True - overwrite source image
    if not overwrite:
        out_file = image_path + f'-{max_size[0]}.jpg'
    else:
        out_file = image_path

    """
    Resize an image while maintaining its aspect ratio.
    """
    try:
        # Open the original image using Pillow
        pil_image = Image.open(image_path)
        #   TODO make copy without convert if file smaller then convert dimensions
        if pil_image.height < max_size[1] or pil_image.width < max_size[0]:
            max_size = (pil_image.width, pil_image.height)
        # convert to RGB
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Resize the image to fit within the specified dimensions while maintaining the aspect ratio
        pil_image.thumbnail(max_size)

        # Rotate according exif information
        img = ImageOps.exif_transpose(pil_image)

        # Save the resized image to the original path
        img.save(out_file, format='JPEG', quality=85, optimize=True, progressive=True)

    except Exception as e:
        # Handle any exceptions (e.g., invalid image file)
        print(f"Error resizing image: {e}")


def create_video_thumbs(video_path):
    clip = VideoFileClip(video_path)
    duration = clip.duration
    start = '--start.jpg'
    mid = '--mid.jpg'
    end = '--end.jpg'

    clip.save_frame(video_path + start, t=1.00)
    resize_image(video_path + start, overwrite=True)
    clip.save_frame(video_path + mid, t=duration / 2)
    resize_image(video_path + mid, overwrite=True)
    clip.save_frame(video_path + end, t=duration - 5)
    resize_image(video_path + end, overwrite=True)


def get_exif(image_path):
    import PIL.ExifTags
    dct = {}
    img = Image.open(image_path)

    def cast(v):
        if isinstance(v, TiffImagePlugin.IFDRational):
            return float(v)
        elif isinstance(v, tuple):
            return tuple(cast(t) for t in v)
        elif isinstance(v, bytes):
            return v.decode(errors="replace")
        elif isinstance(v, dict):
            for kk, vv in v.items():
                v[kk] = cast(vv)
            return v
        else:
            return v

    for k, v in img.getexif().items():
        if k in PIL.ExifTags.TAGS:
            v = cast(v)
            dct[PIL.ExifTags.TAGS[k]] = v
    return json.dumps(dct)

# def generate_video_thumbnail(video_path, thumbnail_path, time_seconds=2):
#     try:
#         # Open the video using OpenCV
#         cap = cv2.VideoCapture(video_path)
#
#         # Get the frames per second and calculate the frame to capture
#         fps = cap.get(cv2.CAP_PROP_FPS)
#         frame_to_capture = int(fps * time_seconds)
#
#         # Set the frame position
#         cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_capture)
#
#         # Read the frame
#         ret, frame = cap.read()
#
#         # Convert the frame to an RGB image
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#
#         # Convert the frame to an Image object using Pillow
#         img = Image.fromarray(rgb_frame)
#
#         # Save the image as a thumbnail
#         img.save(thumbnail_path)
#
#         # Release the video capture object
#         cap.release()
#
#     except Exception as e:
#         # Handle any exceptions (e.g., invalid video file)
#         print(f"Error generating video thumbnail: {e}")

# def generate_video_thumbnail(video_path, thumbnail_path, time_seconds=2):
#     try:
#         # Load the video clip
#         clip = VideoFileClip(video_path)
#
#         # Get a frame at the specified time (in seconds)
#         frame = clip.get_frame(time_seconds)
#
#         # Convert the frame to an Image object using Pillow
#         img = Image.fromarray(frame)
#
#         # Save the image as a thumbnail
#         img.save(thumbnail_path)
#
#         # Close the video clip
#         clip.close()
#
#     except Exception as e:
#         # Handle any exceptions (e.g., invalid video file)
#         print(f"Error generating video thumbnail: {e}")
