import base64
import uuid
import magic
from fastapi import UploadFile, HTTPException
from typing import List, Optional
from io import BytesIO
from PIL import Image


# Supported image formats
SUPPORTED_IMAGE_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
SUPPORTED_VIDEO_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv']

# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB


def validate_file_type(file_content: bytes, expected_types: List[str]) -> bool:
    """Validate file type using python-magic"""
    try:
        file_type = magic.from_buffer(file_content, mime=True)
        return file_type in expected_types
    except Exception:
        return False


def compress_image(image_data: bytes, quality: int = 85, max_width: int = 1920, max_height: int = 1080) -> bytes:
    """Compress and resize image while maintaining aspect ratio"""
    try:
        img = Image.open(BytesIO(image_data))
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        
        # Resize if image is larger than max dimensions
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save compressed image
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image processing failed: {str(e)}")


async def process_image_to_base64(
    file: UploadFile, 
    compress: bool = True,
    quality: int = 85,
    max_width: int = 1920,
    max_height: int = 1080
) -> str:
    """
    Process uploaded image file and return base64 string
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Validate file type
        if not validate_file_type(content, SUPPORTED_IMAGE_FORMATS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            )
        
        # Compress image if requested
        if compress:
            content = compress_image(content, quality, max_width, max_height)
        
        # Convert to base64
        base64_string = base64.b64encode(content).decode('utf-8')
        
        # Add data URL prefix for web compatibility
        mime_type = magic.from_buffer(content, mime=True)
        data_url = f"data:{mime_type};base64,{base64_string}"
        
        return data_url
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")


async def process_video_to_base64(file: UploadFile) -> str:
    """
    Process uploaded video file and return base64 string
    """
    try:
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Video file too large. Maximum size: {MAX_VIDEO_SIZE / (1024*1024):.1f}MB"
            )
        
        # Validate file type
        if not validate_file_type(content, SUPPORTED_VIDEO_FORMATS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video format. Supported: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
            )
        
        # Convert to base64
        base64_string = base64.b64encode(content).decode('utf-8')
        
        # Add data URL prefix for web compatibility
        mime_type = magic.from_buffer(content, mime=True)
        data_url = f"data:{mime_type};base64,{base64_string}"
        
        return data_url
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")


async def process_profile_photo(file: UploadFile) -> str:
    """
    Process profile photo with specific compression settings
    """
    return await process_image_to_base64(
        file=file,
        compress=True,
        quality=90,
        max_width=500,
        max_height=500
    )


async def process_property_media(file: UploadFile, media_type: str = "image") -> str:
    """
    Process property media (images or videos)
    """
    if media_type.lower() == "image":
        return await process_image_to_base64(
            file=file,
            compress=True,
            quality=85,
            max_width=1920,
            max_height=1080
        )
    elif media_type.lower() == "video":
        return await process_video_to_base64(file)
    else:
        raise HTTPException(status_code=400, detail="Invalid media type. Use 'image' or 'video'")


def get_file_info_from_base64(base64_data: str) -> dict:
    """
    Extract file information from base64 data URL
    """
    try:
        if base64_data.startswith('data:'):
            header, data = base64_data.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
            
            # Decode to get size
            decoded_data = base64.b64decode(data)
            size = len(decoded_data)
            
            return {
                "mime_type": mime_type,
                "size": size,
                "size_mb": round(size / (1024 * 1024), 2)
            }
        else:
            return {"error": "Invalid base64 data format"}
    except Exception as e:
        return {"error": f"Failed to parse base64 data: {str(e)}"}


async def validate_and_process_multiple_files(
    files: List[UploadFile], 
    media_type: str = "image",
    max_files: int = 10
) -> List[str]:
    """
    Process multiple files and return list of base64 strings
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum allowed: {max_files}"
        )
    
    processed_files = []
    for file in files:
        processed_data = await process_property_media(file, media_type)
        processed_files.append(processed_data)
    
    return processed_files
