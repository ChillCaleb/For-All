# For-All

Connecting Communities to Resources

## Resources API

The For-All application includes a RESTful API for accessing community resources in Baltimore. The API provides access to real organizations offering housing, food, and clothing assistance.

For detailed API documentation, see [API_RESOURCES.md](API_RESOURCES.md).

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python -m app.app
```

The API will be available at `http://127.0.0.1:5000/api/resources`

### Example Usage

```javascript
// Fetch housing resources
fetch('/api/resources?category=housing&city=Baltimore')
  .then(response => response.json())
  .then(resources => console.log(resources));
```