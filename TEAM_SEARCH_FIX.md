# Team Search Query Fix ✅

## Issue Fixed
**Error**: `unsupported operand type(s) for |: 'QuerySet' and 'QuerySet'`

**Route**: `GET /api/public/team?search=A`

## Problem
The team controller was using the `|` operator to combine QuerySets for OR conditions:
```python
# ❌ WRONG - This doesn't work in Tortoise ORM
query = query.filter(name__icontains=search) | query.filter(email__icontains=search)
```

## Solution Applied
Used `Q` objects for proper OR conditions in Tortoise ORM:
```python
# ✅ CORRECT - Using Q objects
from tortoise.expressions import Q

query = query.filter(Q(name__icontains=search) | Q(email__icontains=search))
```

## What Was Changed
1. **Added Import**: `from tortoise.expressions import Q`
2. **Fixed Query**: Used `Q()` objects for OR condition in search filter

## Route Now Works Correctly
```bash
GET /api/public/team?limit=20&offset=0&search=A
```

### Search Functionality:
- **Search by Name**: Finds team members with names containing the search term
- **Search by Email**: Finds team members with emails containing the search term  
- **OR Logic**: Returns results that match EITHER name OR email
- **Case Insensitive**: Uses `icontains` for case-insensitive search

### Other Filters Still Work:
- **Position Filter**: `?position=Manager`
- **Pagination**: `?limit=10&offset=0`
- **Combined**: `?search=A&position=Developer&limit=5`

## Response Format
```json
{
    "success": true,
    "data": {
        "team_members": [
            {
                "id": "uuid",
                "name": "Team Member Name",
                "email": "email@example.com",
                "position_name": "Developer",
                "description": "...",
                "phone": "...",
                "photo": "...",
                "age": 25,
                "created_at": "...",
                "updated_at": "..."
            }
        ],
        "pagination": {
            "total": 10,
            "limit": 20,
            "offset": 0,
            "has_next": false,
            "has_prev": false
        }
    }
}
```

**Search is now working! 🔍✅**