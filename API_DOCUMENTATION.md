# API Documentation - Handwriting Recognition System

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently, the API does not require authentication. For production, implement JWT or API key authentication.

---

## Endpoints

### 1. Health Check

Check API and system health status.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T10:30:00",
  "model_loaded": true,
  "database_connected": true
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### 2. Recognize Text

Upload an image and get recognized text.

**Endpoint:** `POST /api/recognize`

**Content-Type:** `multipart/form-data`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| image | file | Yes | Image file (JPG, PNG, BMP) |

**Response:**
```json
{
  "success": true,
  "text": "Hello World",
  "confidence": 0.95,
  "num_characters": 10,
  "processing_time": 2.34,
  "timestamp": "2025-11-18T10:30:00",
  "record_id": 123,
  "details": {
    "raw_text": "He11o Wor1d",
    "corrected_text": "Hello World"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "No text detected in image",
  "processing_time": 1.23
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:5000/api/recognize \
  -F "image=@handwriting.jpg"
```

**Example (Python):**
```python
import requests

url = "http://localhost:5000/api/recognize"
files = {"image": open("handwriting.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://localhost:5000/api/recognize', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

### 3. Get Recognition History

Retrieve past recognition results.

**Endpoint:** `GET /api/history`

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 50 | Number of records (1-100) |
| offset | integer | No | 0 | Pagination offset |

**Response:**
```json
{
  "success": true,
  "count": 10,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "id": 123,
      "original_filename": "handwriting.jpg",
      "recognized_text": "Hello World",
      "confidence_score": 0.95,
      "num_characters": 10,
      "processing_time": 2.34,
      "timestamp": "2025-11-18T10:30:00",
      "metadata": {}
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/history?limit=10&offset=0"
```

---

### 4. Search Recognition Results

Search for specific text in past recognitions.

**Endpoint:** `GET /api/search`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Search query |
| limit | integer | No | Max results (default: 50) |

**Response:**
```json
{
  "success": true,
  "query": "hello",
  "count": 5,
  "results": [
    {
      "id": 123,
      "original_filename": "test.jpg",
      "recognized_text": "Hello World",
      "confidence_score": 0.95,
      "timestamp": "2025-11-18T10:30:00"
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:5000/api/search?q=hello&limit=10"
```

---

### 5. Get Statistics

Get system statistics and performance metrics.

**Endpoint:** `GET /api/statistics`

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_recognitions": 1234,
    "total_characters": 45678,
    "average_confidence": 0.92,
    "average_processing_time": 2.5
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/statistics
```

---

### 6. Get Specific Record

Retrieve a specific recognition result by ID.

**Endpoint:** `GET /api/record/<record_id>`

**Parameters:**
| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| record_id | integer | Path | Record ID |

**Response:**
```json
{
  "success": true,
  "record": {
    "id": 123,
    "image_path": "/path/to/processed/image.jpg",
    "original_filename": "handwriting.jpg",
    "recognized_text": "Hello World",
    "confidence_score": 0.95,
    "num_characters": 10,
    "processing_time": 2.34,
    "timestamp": "2025-11-18T10:30:00",
    "metadata": {
      "raw_text": "He11o Wor1d",
      "preprocessing_method": "bilateral"
    }
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Record not found"
}
```

**Example:**
```bash
curl http://localhost:5000/api/record/123
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found |
| 413 | Payload Too Large (file > 16MB) |
| 500 | Internal Server Error |

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:
- Implement rate limiting (e.g., 100 requests/hour per IP)
- Use Redis for distributed rate limiting
- Consider API keys for higher limits

---

## Best Practices

### 1. Image Quality
- **Resolution:** 300 DPI or higher
- **Format:** PNG for best quality, JPG for smaller size
- **Lighting:** Even, no shadows
- **Background:** Plain white or light color
- **Contrast:** High contrast between text and background

### 2. Error Handling
Always check the `success` field:
```javascript
if (response.success) {
  // Handle success
} else {
  // Handle error
  console.error(response.error);
}
```

### 3. File Size
- Keep images under 16MB
- Compress large images before upload
- Remove unnecessary metadata

### 4. Batch Processing
For multiple images, send requests sequentially or implement queue:
```python
for image in images:
    response = recognize_text(image)
    time.sleep(0.5)  # Avoid overwhelming server
```

---

## Performance Tips

### 1. Image Preprocessing
Preprocess images client-side when possible:
- Crop to text area
- Convert to grayscale
- Compress to reasonable size

### 2. Caching
Cache results for identical images:
```python
import hashlib

def get_image_hash(image_data):
    return hashlib.md5(image_data).hexdigest()
```

### 3. Async Requests
Use async/await for better performance:
```javascript
async function recognizeImages(images) {
  const promises = images.map(img => 
    fetch('/api/recognize', {
      method: 'POST',
      body: createFormData(img)
    })
  );
  return await Promise.all(promises);
}
```

---

## Webhooks (Future Enhancement)

For long-running processes, webhooks will be added:

**Endpoint:** `POST /api/recognize/async`

**Response:**
```json
{
  "success": true,
  "job_id": "abc123",
  "status": "processing",
  "webhook_url": "https://your-server.com/webhook"
}
```

The system will POST results to your webhook URL when complete.

---

## SDK Examples

### Python SDK (Example)
```python
class HandwritingRecognitionClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def recognize(self, image_path):
        url = f"{self.base_url}/api/recognize"
        files = {"image": open(image_path, "rb")}
        response = requests.post(url, files=files)
        return response.json()
    
    def get_history(self, limit=50, offset=0):
        url = f"{self.base_url}/api/history"
        params = {"limit": limit, "offset": offset}
        response = requests.get(url, params=params)
        return response.json()

# Usage
client = HandwritingRecognitionClient("http://localhost:5000")
result = client.recognize("handwriting.jpg")
print(result['text'])
```

---

## Testing

Use the provided test script:
```bash
python tests/test_api.py
```

Or test manually:
```bash
# Health check
curl http://localhost:5000/api/health

# Upload test image
curl -X POST http://localhost:5000/api/recognize \
  -F "image=@test_images/sample.jpg"
```

---

## Support

For issues or questions:
- Check logs: `app.log`
- Review documentation: `README.md`
- Test API health: `GET /api/health`

---

**Last Updated:** November 18, 2025
**Version:** 1.0
