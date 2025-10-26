# Pagination

DjangoCRM uses cursor-based pagination for optimal performance with large datasets.

## 📄 Pagination Format

**Response Structure:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/projects/?cursor=abc123",
  "previous": null,
  "results": [
    // Array of items
  ]
}
```

## 🔍 Query Parameters

- `page_size`: Number of items per page (default: 10, max: 100)
- `cursor`: Pagination cursor for next/previous pages

**Example:**
```bash
# Get first page with 20 items
GET /api/projects/?page_size=20

# Get next page
GET /api/projects/?cursor=abc123&page_size=20
```

## 📊 Pagination Metadata

- `count`: Total number of items
- `next`: URL for next page (null if no more pages)
- `previous`: URL for previous page (null if first page)
- `results`: Array of items for current page

## 🎯 Usage Examples

### JavaScript/Fetch
```javascript
async function fetchProjects(pageUrl = '/api/projects/') {
  const response = await fetch(pageUrl, {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });

  const data = await response.json();

  // Process current page
  console.log('Projects:', data.results);
  console.log('Total count:', data.count);

  // Fetch next page if available
  if (data.next) {
    fetchProjects(data.next);
  }

  return data;
}
```

### Python/Requests
```python
import requests

def fetch_all_projects(token, url='/api/projects/'):
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    all_projects = []

    while url:
        response = requests.get(url, headers=headers)
        data = response.json()

        all_projects.extend(data['results'])

        # Get next page URL
        url = data.get('next')

    return all_projects
```

## ⚙️ Configuration

Pagination settings in `saasCRM/settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'saasCRM.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
    # ... other settings
}
```

## 🚀 Performance Benefits

- **Cursor-based**: Efficient for large datasets
- **Stable**: Page content doesn't shift with insertions/deletions
- **Memory efficient**: Only loads current page data
- **Scalable**: Performance remains consistent as data grows

## 🔍 Filtering with Pagination

Combine pagination with filtering:

```bash
# Filter and paginate
GET /api/projects/?status=active&page_size=5

# Search and paginate
GET /api/tasks/?search=bug&page_size=10
```

## 📱 Frontend Integration

### React Example
```jsx
import { useState, useEffect } from 'react';

function ProjectsList() {
  const [projects, setProjects] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchProjects = async (url = '/api/projects/') => {
    setLoading(true);
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Token ${token}`
        }
      });
      const data = await response.json();

      setProjects(prev => [...prev, ...data.results]);
      setNextPage(data.next);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMore = () => {
    if (nextPage && !loading) {
      fetchProjects(nextPage);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <div>
      {projects.map(project => (
        <div key={project.id}>{project.name}</div>
      ))}
      {nextPage && (
        <button onClick={loadMore} disabled={loading}>
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

## ⚠️ Important Notes

- Always check for `next` and `previous` URLs
- Handle loading states in your UI
- Consider implementing infinite scroll for better UX
- Cache responses when appropriate
- Use appropriate `page_size` for your use case</content>
</xai:function_call"> 

Assistant: Now create filtering-search.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/filtering-search.md