# Pagination

DjangoCRM uses cursor-based pagination for optimal performance with large datasets.

## 🎯 Pagination Types

### Cursor Pagination (Default)

Used for most list endpoints to ensure consistent ordering and efficient database queries.

**Response Format:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/projects/?cursor=abc123",
  "previous": "http://localhost:8000/api/projects/?cursor=def456",
  "results": [
    {
      "id": "uuid",
      "name": "Project 1",
      "slug": "project-1"
    }
  ]
}
```

**Parameters:**
- `cursor` - Opaque cursor string for navigation
- `page_size` - Number of items per page (default: 20, max: 100)

### Page Number Pagination

Available for some endpoints that require page-based navigation.

**Response Format:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/projects/?page=3",
  "previous": "http://localhost:8000/api/projects/?page=1",
  "results": [...]
}
```

**Parameters:**
- `page` - Page number (1-based)
- `page_size` - Items per page

## 📖 Usage Examples

### Basic Pagination

```bash
# Get first page (default)
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/

# Get specific page size
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/projects/?page_size=50"

# Navigate using cursor
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/projects/?cursor=abc123"
```

### JavaScript Example

```javascript
async function fetchProjects(cursor = null) {
  const params = new URLSearchParams();
  if (cursor) params.append('cursor', cursor);
  params.append('page_size', '20');

  const response = await fetch(`/api/projects/?${params}`, {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });

  const data = await response.json();
  return {
    projects: data.results,
    nextCursor: data.next ? new URL(data.next).searchParams.get('cursor') : null,
    hasMore: !!data.next
  };
}
```

### React Hook Example

```typescript
function usePaginatedProjects() {
  const [projects, setProjects] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const response = await fetch(
        `/api/projects/?${cursor ? `cursor=${cursor}&` : ''}page_size=20`,
        {
          headers: {
            'Authorization': `Token ${token}`
          }
        }
      );

      const data = await response.json();
      setProjects(prev => [...prev, ...data.results]);
      setCursor(data.next ? new URL(data.next).searchParams.get('cursor') : null);
      setHasMore(!!data.next);
    } finally {
      setLoading(false);
    }
  };

  return { projects, loadMore, loading, hasMore };
}
```

## ⚙️ Configuration

### Default Settings

- **Page Size**: 20 items per page
- **Max Page Size**: 100 items per page
- **Ordering**: By creation date (newest first) or custom field

### Custom Page Sizes

```bash
# Small pages for mobile
curl "http://localhost:8000/api/projects/?page_size=10"

# Large pages for data export
curl "http://localhost:8000/api/projects/?page_size=100"
```

## 🔍 Filtering with Pagination

Pagination works seamlessly with filtering:

```bash
# Filter and paginate
curl "http://localhost:8000/api/projects/?status=active&page_size=50"

# Search with pagination
curl "http://localhost:8000/api/projects/?search=website&cursor=abc123"
```

## 📊 Performance Considerations

### Cursor Pagination Benefits

- **Consistent Ordering**: No duplicate or missing items when data changes
- **Efficient**: Database queries use indexes effectively
- **Scalable**: Performance remains constant regardless of dataset size

### Best Practices

1. **Use appropriate page sizes**: Smaller for mobile, larger for desktop
2. **Implement infinite scroll**: Load more data as user scrolls
3. **Cache cursors**: Store cursor positions for navigation
4. **Handle loading states**: Show loading indicators during fetch operations

### Rate Limiting

- API requests are rate-limited
- Large page sizes may be restricted
- Consider using WebSockets for real-time updates instead of frequent polling

## 🐛 Troubleshooting

### Common Issues

**"Invalid cursor" error**
- Cursors are opaque and time-sensitive
- Don't modify or cache cursors for too long
- Refresh data if cursor becomes invalid

**Missing items**
- Data may have been modified between requests
- Use cursor pagination to avoid this issue

**Performance issues**
- Reduce page size for better performance
- Use filtering to reduce dataset size
- Consider server-side caching

### Debug Information

```bash
# Check pagination metadata
curl -v "http://localhost:8000/api/projects/?page_size=1"

# Response headers include pagination info
# X-Total-Count: 150
# Link: <http://localhost:8000/api/projects/?cursor=next>; rel="next"
```</content>
</xai:function_call"> 

Assistant: Now create the filtering-search.md file. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/filtering-search.md