# Notice File Download Testing Documentation

## File Download Endpoints

### Public Download Endpoint
```
GET /api/notices/{notice_id}/download
```
- **Access**: Public (no authentication required)
- **Purpose**: Allow users to download notice files
- **Response**: Binary file data with proper headers

### Admin Download Endpoint
```
GET /api/admin/notices/{notice_id}/download
```
- **Access**: Admin only (authentication + admin role required)
- **Purpose**: Admin access to download any notice file
- **Response**: Binary file data with proper headers

## Supported File Types

The download endpoints support the following file types with proper MIME types:
- **PDF**: `application/pdf`
- **DOCX**: `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **DOC**: `application/msword`
- **Images**: 
  - JPG/JPEG: `image/jpeg`
  - PNG: `image/png`
  - GIF: `image/gif`
- **Text**: `text/plain`
- **Default**: `application/octet-stream` (for unknown types)

## Download Process

1. **Request**: Client sends GET request to download endpoint with notice ID
2. **Validation**: System validates notice ID and checks if file exists
3. **Decoding**: Base64 encoded file data is decoded to binary
4. **Headers**: Proper HTTP headers are set including:
   - `Content-Disposition: attachment; filename="original_filename.ext"`
   - `Content-Length: file_size_in_bytes`
   - `Cache-Control: no-cache`
5. **Response**: Binary file data is returned with correct MIME type

## Error Handling

### Common Error Responses

#### Notice Not Found (404)
```json
{
  "detail": "Notice not found"
}
```

#### Invalid Notice ID (400)
```json
{
  "detail": "Invalid notice ID format"
}
```

#### No File Attached (404)
```json
{
  "detail": "No file attached to this notice"
}
```

#### File Corruption (500)
```json
{
  "detail": "Failed to decode file data. File may be corrupted."
}
```

## Testing Examples

### Using cURL

#### Download Public Notice File
```bash
curl -X GET "http://127.0.0.1:8001/api/notices/{notice-uuid}/download" \
  -H "Accept: */*" \
  --output "downloaded_notice_file.pdf"
```

#### Download Admin Notice File (with authentication)
```bash
curl -X GET "http://127.0.0.1:8001/api/admin/notices/{notice-uuid}/download" \
  -H "Accept: */*" \
  -H "Cookie: auth_token=your-admin-token" \
  --output "downloaded_notice_file.pdf"
```

### Using JavaScript (Frontend)

#### Public Download
```javascript
async function downloadNoticeFile(noticeId) {
  try {
    const response = await fetch(`/api/notices/${noticeId}/download`);
    
    if (!response.ok) {
      throw new Error('Download failed');
    }
    
    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition');
    const filename = contentDisposition 
      ? contentDisposition.split('filename=')[1].replace(/"/g, '')
      : `notice_${noticeId}.pdf`;
    
    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
  } catch (error) {
    console.error('Download failed:', error);
    alert('Failed to download file');
  }
}
```

#### Admin Download (with authentication)
```javascript
async function downloadNoticeFileAdmin(noticeId) {
  try {
    const response = await fetch(`/api/admin/notices/${noticeId}/download`, {
      credentials: 'include' // Include cookies for authentication
    });
    
    if (!response.ok) {
      throw new Error('Download failed');
    }
    
    const contentDisposition = response.headers.get('Content-Disposition');
    const filename = contentDisposition 
      ? contentDisposition.split('filename=')[1].replace(/"/g, '')
      : `notice_${noticeId}.pdf`;
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
  } catch (error) {
    console.error('Admin download failed:', error);
    alert('Failed to download file');
  }
}
```

## Integration with Frontend

### Notice List Component
```javascript
// Add download button to each notice with file
const NoticeListItem = ({ notice }) => {
  const hasFile = notice.notice_file && notice.original_filename;
  
  return (
    <div className="notice-item">
      <h3>{notice.title}</h3>
      <p>{notice.description}</p>
      
      {hasFile && (
        <button 
          onClick={() => downloadNoticeFile(notice.id)}
          className="download-btn"
        >
          📁 Download {notice.original_filename}
        </button>
      )}
    </div>
  );
};
```

### Admin Notice Management
```javascript
// Admin can download any notice file
const AdminNoticeItem = ({ notice }) => {
  const hasFile = notice.notice_file && notice.original_filename;
  
  return (
    <div className="admin-notice-item">
      <h3>{notice.title}</h3>
      <p>{notice.description}</p>
      
      {hasFile && (
        <div className="file-actions">
          <span>📎 {notice.original_filename}</span>
          <button 
            onClick={() => downloadNoticeFileAdmin(notice.id)}
            className="admin-download-btn"
          >
            Download File
          </button>
        </div>
      )}
    </div>
  );
};
```

## Fixed Issues

1. **Base64 Decoding**: Proper base64 decoding with error handling
2. **MIME Type Detection**: Automatic content type detection based on file extension
3. **Filename Handling**: Uses original filename or generates fallback
4. **Binary Response**: Returns proper binary data with correct headers
5. **Error Handling**: Comprehensive error handling for all failure scenarios
6. **Access Control**: Both public and admin endpoints available

The notice file download functionality is now fully working and handles all encoding/decoding issues properly!