import base64
import uuid
import mimetypes
from fastapi import UploadFile, HTTPException
from typing import List, Optional
from io import BytesIO
from PIL import Image


# Supported image formats
SUPPORTED_IMAGE_FORMATS = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
SUPPORTED_VIDEO_FORMATS = ['video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv']

# Maximum file sizes (in bytes)


MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_VIDEO_SIZE = 200 * 1024 * 1024  # 200MB



def validate_file_type(file_content: bytes, expected_types: List[str]) -> bool:
    """Validate file type using mimetypes (simplified for Windows compatibility)"""
    try:
        # Try to detect from file signature for images
        if file_content.startswith(b'\xff\xd8\xff'):
            file_type = 'image/jpeg'
        elif file_content.startswith(b'\x89PNG'):
            file_type = 'image/png'
        elif file_content.startswith(b'GIF87a') or file_content.startswith(b'GIF89a'):
            file_type = 'image/gif'
        elif file_content.startswith(b'RIFF') and b'WEBP' in file_content[:12]:
            file_type = 'image/webp'
        else:
            # Fallback to basic detection
            file_type = 'application/octet-stream'
        
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
        print(f"📷 Processing image: {file.filename}")
        
        # Read file content with timeout protection
        content = await file.read()
        print(f"📷 File read complete, size: {len(content)} bytes")
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Validate file size
        if len(content) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024):.1f}MB"
            )
        
        print("📷 Validating file type...")
        # Validate file type
        if not validate_file_type(content, SUPPORTED_IMAGE_FORMATS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported image format. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
            )
        
        print("📷 File validation passed")
        
        # Compress image if requested
        if compress:
            print("📷 Compressing image...")
            content = compress_image(content, quality, max_width, max_height)
            print("📷 Image compression complete")
        
        print("📷 Converting to base64...")
        # Convert to base64
        base64_string = base64.b64encode(content).decode('utf-8')
        
        # Add data URL prefix for web compatibility
        # Simple MIME type detection based on file signature
        if content.startswith(b'\xff\xd8\xff'):
            mime_type = 'image/jpeg'
        elif content.startswith(b'\x89PNG'):
            mime_type = 'image/png'
        elif content.startswith(b'GIF87a') or content.startswith(b'GIF89a'):
            mime_type = 'image/gif'
        elif content.startswith(b'RIFF') and b'WEBP' in content[:12]:
            mime_type = 'image/webp'
        else:
            mime_type = 'image/jpeg'  # Default fallback
            
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
        # Simple video MIME type detection
        mime_type = 'video/mp4'  # Default to mp4
        data_url = f"data:{mime_type};base64,{base64_string}"
        
        return data_url
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")


async def process_profile_photo(file: UploadFile) -> str:
    """
    Process profile photo with specific compression settings and timeout
    """
    try:
        print(f"📷 Starting profile photo processing for: {file.filename}")
        print(f"📷 Content type: {file.content_type}")
        
        # Check file size before reading
        if hasattr(file, 'size') and file.size and file.size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"Image file too large. Maximum size: {MAX_IMAGE_SIZE / (1024*1024):.1f}MB"
            )
        
        result = await process_image_to_base64(
            file=file,
            compress=True,
            quality=75,  # Reduced quality for smaller size
            max_width=300,  # Smaller dimensions
            max_height=300
        )
        
        # Check final base64 size (typical base64 adds ~37% overhead)
        result_size_mb = len(result) / (1024 * 1024)
        print(f"✅ Profile photo processed successfully")
        print(f"📊 Base64 size: {len(result)} chars ({result_size_mb:.2f}MB)")
        
        # Warn if still large (most TEXT fields can handle this, but warn anyway)
        if len(result) > 16_777_215:  # MySQL MEDIUMTEXT limit
            print(f"⚠️  Large image warning: {result_size_mb:.2f}MB base64 string")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Profile photo processing failed: {e}")
        raise HTTPException(status_code=400, detail=f"Profile photo processing failed: {str(e)}")


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


async def handle_general_media_upload(
    files: List[UploadFile],
    upload_type: str = "property",
    max_files: int = 20,
    compress_images: bool = True,
    quality: int = 85,
    max_width: int = 1920,
    max_height: int = 1080
) -> dict:
    """
    General-purpose media upload function that handles 1 to N files
    
    Args:
        files: List of UploadFile objects (can be 1 or more)
        upload_type: Type of upload ('property', 'profile', 'general')
        max_files: Maximum number of files allowed
        compress_images: Whether to compress images
        quality: Compression quality (1-100)
        max_width: Maximum image width
        max_height: Maximum image height
    
    Returns:
        dict: {
            'success': bool,
            'processed_files': List[str],  # base64 URLs
            'file_count': int,
            'errors': List[str],
            'file_info': List[dict]
        }
    """
    try:
        print(f"🔄 Processing {len(files)} files for {upload_type} upload...")
        
        # Validate file count
        if len(files) > max_files:
            raise HTTPException(
                status_code=400,
                detail=f"Too many files. Maximum allowed: {max_files}"
            )
        
        # If no files, return success with empty results
        if not files or len(files) == 0:
            return {
                'success': True,
                'processed_files': [],
                'file_count': 0,
                'errors': [],
                'file_info': []
            }
        
        processed_files = []
        errors = []
        file_info = []
        
        for i, file in enumerate(files):
            try:
                print(f"📁 Processing file {i+1}/{len(files)}: {file.filename}")
                
                # Check if file is empty
                if not file.filename or file.filename == '':
                    errors.append(f"File {i+1}: Empty filename")
                    continue
                
                # Auto-detect media type based on content type or extension
                content_type = getattr(file, 'content_type', '') or ''
                filename = file.filename.lower()
                
                if (content_type.startswith('image/') or 
                    filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                    media_type = "image"
                elif (content_type.startswith('video/') or 
                      filename.endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv'))):
                    media_type = "video"
                else:
                    # Default to image for unknown types
                    media_type = "image"
                
                print(f"📁 Detected media type: {media_type}")
                
                # Process based on upload type and media type
                if upload_type == "profile" and media_type == "image":
                    # Special handling for profile photos
                    base64_url = await process_profile_photo(file)
                elif media_type == "image":
                    # General image processing
                    base64_url = await process_image_to_base64(
                        file=file,
                        compress=compress_images,
                        quality=quality,
                        max_width=max_width,
                        max_height=max_height
                    )
                else:
                    # Video processing
                    base64_url = await process_video_to_base64(file)
                
                processed_files.append(base64_url)
                
                # Get file info for response
                file_info_dict = get_file_info_from_base64(base64_url)
                file_info_dict.update({
                    'original_filename': file.filename,
                    'media_type': media_type,
                    'processed_successfully': True
                })
                file_info.append(file_info_dict)
                
                print(f"✅ Successfully processed: {file.filename}")
                
            except Exception as e:
                error_msg = f"File {i+1} ({file.filename}): {str(e)}"
                errors.append(error_msg)
                print(f"❌ Error processing file {file.filename}: {e}")
                continue
        
        success = len(processed_files) > 0  # Success if at least one file processed
        
        result = {
            'success': success,
            'processed_files': processed_files,
            'file_count': len(processed_files),
            'errors': errors,
            'file_info': file_info
        }
        
        print(f"📊 Upload summary: {len(processed_files)}/{len(files)} files processed successfully")
        if errors:
            print(f"⚠️ Errors encountered: {len(errors)} files failed")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ General media upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Media upload processing failed: {str(e)}")


async def upload_single_file(
    file: UploadFile,
    upload_type: str = "property",
    compress_images: bool = True,
    quality: int = 85,
    max_width: int = 1920,
    max_height: int = 1080
) -> str:
    """
    Convenience function for uploading a single file
    
    Returns:
        str: Base64 URL of the processed file
    """
    result = await handle_general_media_upload(
        files=[file],
        upload_type=upload_type,
        max_files=1,
        compress_images=compress_images,
        quality=quality,
        max_width=max_width,
        max_height=max_height
    )
    
    if not result['success'] or len(result['processed_files']) == 0:
        errors = result.get('errors', ['Unknown error'])
        raise HTTPException(status_code=400, detail=f"File upload failed: {'; '.join(errors)}")
    
    return result['processed_files'][0]


# Document file support for notices
SUPPORTED_DOCUMENT_FORMATS = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']
MAX_DOCUMENT_SIZE = 100 * 1024 * 1024  # 100MB


async def process_document_to_base64(file: UploadFile) -> str:
    """Process document files (PDF, DOCX, DOC) to base64"""
    try:
        print(f"📄 Processing document: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Check file size
        if file_size > MAX_DOCUMENT_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Document file too large. Maximum size: {MAX_DOCUMENT_SIZE / (1024*1024)}MB"
            )
        
        # Validate document type
        content_type = getattr(file, 'content_type', '') or ''
        filename = file.filename.lower()
        
        # Determine file type
        if (content_type == 'application/pdf' or filename.endswith('.pdf')):
            detected_type = 'application/pdf'
        elif (content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or 
              filename.endswith('.docx')):
            detected_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif (content_type == 'application/msword' or filename.endswith('.doc')):
            detected_type = 'application/msword'
        else:
            # Allow images as well for notices
            if (content_type.startswith('image/') or 
                filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))):
                # Process as image
                await file.seek(0)  # Reset file pointer
                return await process_image_to_base64(file, compress=True, quality=85)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type. Only PDF, DOCX, DOC, and image files are allowed for notices."
                )
        
        # Convert to base64
        base64_content = base64.b64encode(file_content).decode('utf-8')
        base64_url = f"data:{detected_type};base64,{base64_content}"
        
        print(f"✅ Document processed successfully: {file.filename} ({file_size} bytes)")
        return base64_url
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )
