import os
import uuid
from datetime import datetime
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from core.authentication import JWTAuthentication
from core.permissions import IsAuthenticated
from core.exceptions import CustomAppException

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def upload_file_view(request):
    if 'file' not in request.FILES:
        raise CustomAppException(message="Fayl tanlanmagan", status_code=400)

    uploaded_file = request.FILES['file']
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise CustomAppException(
            message=f"Fayl formati qo'llab-quvvatlanmaydi. Ruxsat etilgan: {', '.join(settings.ALLOWED_EXTENSIONS)}",
            status_code=400
        )

    if uploaded_file.size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise CustomAppException(
            message=f"Fayl hajmi {settings.MAX_FILE_SIZE_MB}MB dan oshmasligi kerak",
            status_code=400
        )

    now = datetime.now()
    year_str = now.strftime("%Y")
    month_str = now.strftime("%m")

    upload_path = os.path.join(settings.UPLOAD_DIR, year_str, month_str)
    os.makedirs(upload_path, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}{ext}"
    full_filepath = os.path.join(upload_path, unique_filename)

    with open(full_filepath, "wb") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    url_path = f"/uploads/{year_str}/{month_str}/{unique_filename}"

    return Response({
        "success": True,
        "data": {
            "filename": uploaded_file.name,
            "url": url_path,
            "size_bytes": uploaded_file.size,
            "mime_type": uploaded_file.content_type
        }
    })
