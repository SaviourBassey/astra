from decouple import config
from imagekitio import ImageKit

# IMAGEKIT_PRIVATE_KEY = config('IMAGEKIT_PRIVATE_KEY')
# IMAGEKIT_PUBLIC_KEY = config('IMAGEKIT_PUBLIC_KEY')
# IMAGEKIT_URL_ENDPOINT = config('IMAGEKIT_URL_ENDPOINT')

IMAGEKIT_PRIVATE_KEY = "private_1riUqU/LHMBQ4bMNCNwRumaw9go="
IMAGEKIT_PUBLIC_KEY = "public_OwGKSGixGV36a+nFww5lchcH85I="
IMAGEKIT_URL_ENDPOINT = "https://ik.imagekit.io/5kilolxt5"

imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY,
    public_key=IMAGEKIT_PUBLIC_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)



url = "https://cfm.ehu.es/ricardo/docs/python/Learning_Python.pdf"
# # ✅ Open the file and read its binary content
# with open("home/Learning_Python.pdf", "rb") as file:
#     upload = imagekit.upload_file(
#         file=file,  # ✅ Pass the file object, NOT the file path
#         file_name="test-url.pdf",
#     )

# # ✅ Retrieve the uploaded file URL
# url = upload.response_metadata.raw["url"]
# print("Uploaded file URL:", url)







































