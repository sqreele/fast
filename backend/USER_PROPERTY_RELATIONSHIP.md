# User-Property Many-to-Many Relationship

This document explains the many-to-many relationship between Users and Properties in the PM System.

## Overview

The system implements a many-to-many relationship between Users and Properties through the `UserPropertyAccess` model. This allows:
- Multiple users to have access to the same property
- Users to have access to multiple properties
- Different access levels for each user-property combination

## Database Model

### UserPropertyAccess Table
```sql
CREATE TABLE user_property_access (
    user_id INTEGER PRIMARY KEY,
    property_id INTEGER PRIMARY KEY,
    access_level VARCHAR(20) NOT NULL,
    granted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NULL
);
```

### Access Levels
- `READ_ONLY`: User can only view property data
- `FULL_ACCESS`: User can view and modify property data
- `SUPERVISOR`: User has supervisory access
- `ADMIN`: User has administrative access

## API Endpoints

### User Property Access

#### Get User's Properties
```http
GET /api/v1/users/{user_id}/properties
```
Returns all properties a user has access to.

#### Add Property Access for User
```http
POST /api/v1/users/{user_id}/properties
```
```json
{
    "property_id": 1,
    "access_level": "FULL_ACCESS",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Remove Property Access for User
```http
DELETE /api/v1/users/{user_id}/properties/{property_id}
```

#### Get User with Properties
```http
GET /api/v1/users/{user_id}/with-properties
```
Returns user details with all property access information.

### Property User Access

#### Get Property's Users
```http
GET /api/v1/properties/{property_id}/users
```
Returns all users who have access to a property.

#### Add User Access to Property
```http
POST /api/v1/properties/{property_id}/users
```
```json
{
    "user_id": 1,
    "access_level": "FULL_ACCESS",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

#### Remove User Access from Property
```http
DELETE /api/v1/properties/{property_id}/users/{user_id}
```

#### Get Property with Users
```http
GET /api/v1/properties/{property_id}/with-users
```
Returns property details with all user access information.

## Admin Interface

The `UserPropertyAccess` model is available in the SQLAlchemy Admin interface at `/admin/` with the following features:
- View all user-property access relationships
- Create new access relationships
- Edit existing access levels and expiration dates
- Delete access relationships

## Usage Examples

### Python/SQLAlchemy
```python
from models.models import User, Property, UserPropertyAccess, AccessLevel

# Get user with their properties
user = db.query(User).filter(User.id == 1).first()
for access in user.property_access:
    print(f"Property: {access.property.name}, Level: {access.access_level}")

# Get property with its users
property = db.query(Property).filter(Property.id == 1).first()
for access in property.user_access:
    print(f"User: {access.user.username}, Level: {access.access_level}")

# Create new access
new_access = UserPropertyAccess(
    user_id=1,
    property_id=1,
    access_level=AccessLevel.FULL_ACCESS
)
db.add(new_access)
db.commit()
```

### Frontend/JavaScript
```javascript
// Get user's properties
const userProperties = await fetch('/api/v1/users/1/properties').then(r => r.json());

// Add property access
await fetch('/api/v1/users/1/properties', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        property_id: 1,
        access_level: 'FULL_ACCESS'
    })
});

// Get property's users
const propertyUsers = await fetch('/api/v1/properties/1/users').then(r => r.json());
```

## Security Considerations

1. **Access Control**: All endpoints require authentication
2. **Authorization**: Users can only access properties they have permission for
3. **Audit Trail**: All access changes are logged with timestamps
4. **Expiration**: Access can be set to expire automatically
5. **Validation**: Duplicate access relationships are prevented

## Migration Notes

The `UserPropertyAccess` table is created automatically when the database is initialized. No manual migration is required for new installations.

For existing installations, the table will be created when running database migrations. 