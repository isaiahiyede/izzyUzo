import base64
from django.conf import settings
import boto
import requests
from django.core.files.base import ContentFile



def convert_remote_image_to_base64(image_path):
    image_response = requests.get(image_path).content
    return base64.b64encode(image_response)

def decode_image_base64(image_base64):
    return base64.b64decode(image_base64)
            
def convert_base64_to_image(base64_string, filename):
    decoded_base64 = decode_image_base64(base64_string)
    return ContentFile(decoded_base64, filename)
    # image_data = base64.b64decode(base64_string)
    # filename = '%s.jpg' %tracking_number
    # with open(filename, 'wb') as f:
    #     f.write(image_data)
    # return filename
    
def upload_image_To_s3(location, filename, img):
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    b = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME)
    k = b.new_key('%s/%s' %(location, filename))
    k.set_contents_from_string(img.getvalue())
    
    image_path = "%s%s/%s" %(settings.STATIC_URL, location, filename+".png")
    
    return image_path