# Lynx Compare v1.0.0 — REST API Reference

Lynx Compare exposes a REST API via Flask for programmatic access over HTTP.

## Starting the Server

```bash
# Default (production mode, port 5000)
lynx-compare-server

# Custom port and mode
lynx-compare-server --port 8080 -t

# With debug mode
lynx-compare-server --port 8080 -p --debug
```

Or programmatically:

```python
from lynx_compare.server import create_app

app = create_app(run_mode="production")
app.run(port=8080)
```

---

## Endpoints

### `GET /`

Returns API information and available endpoints.

**Response:**
```json
{
  "name": "Lynx Compare",
  "version": "1.0.0",
  "endpoints": ["/about", "/compare", "/export", "/health"]
}
```

---

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### `GET /about`

Returns developer and license information.

**Response:**
```json
{
  "name": "Lynx Compare",
  "version": "0.1.0",
  "developer": "Borja Tarraso",
  "email": "borja.tarraso@member.fsf.org",
  "license": "BSD 3-Clause License",
  "license_text": "..."
}
```

---

### `GET|POST /compare`

Compare two companies.

**Parameters:**

| Parameter          | Type   | Required | Description                     |
| ------------------ | ------ | -------- | ------------------------------- |
| `a`                | string | Yes      | First company identifier        |
| `b`                | string | Yes      | Second company identifier       |
| `refresh`          | bool   | No       | Force fresh data download       |
| `download_reports` | bool   | No       | Fetch SEC filings               |
| `download_news`    | bool   | No       | Fetch news articles             |
| `verbose`          | bool   | No       | Enable verbose analysis output  |

**Example:**
```
GET /compare?a=AAPL&b=MSFT
```

**Response:**
```json
{
  "summary": "MSFT wins 6-1 sections (30-15 metrics) vs AAPL",
  "winner": "MSFT",
  "data": { ... }
}
```

---

### `GET|POST /export`

Export a comparison as HTML, text, or PDF.

**Parameters:**

| Parameter | Type   | Required | Description                        |
| --------- | ------ | -------- | ---------------------------------- |
| `a`       | string | Yes      | First company identifier           |
| `b`       | string | Yes      | Second company identifier          |
| `format`  | string | No       | `html` (default), `text`, or `pdf` |

**Example:**
```
GET /export?a=AAPL&b=MSFT&format=html
```

**Response:** File download with appropriate MIME type.

---

---

## Error Handling

All error responses follow the format:

```json
{
  "error": "Description of what went wrong."
}
```

| Status | Meaning               |
| ------ | --------------------- |
| 200    | Success               |
| 400    | Missing/invalid input |
| 500    | Server error          |
