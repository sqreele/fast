# Registration Error Fix - 400 Bad Request

## 🐛 **Problem**
The registration page was showing a 400 Bad Request error:
```
Registration error: Error: Registration failed: 400
```

## 🔍 **Root Cause**
The error was caused by trying to register a user with a username that already exists in the database. The backend returns a 400 error with the message "Username already registered".

### **Error Details:**
- **Frontend Error**: Generic "Registration failed: 400" message
- **Backend Error**: "Username already registered"
- **Issue**: Frontend wasn't properly displaying the specific error message from the backend

## ✅ **Solution Applied**

### **1. Enhanced Error Handling**
```typescript
// Before
if (!response.ok) {
  throw new Error(data.message || `Registration failed: ${response.status}`);
}

// After
if (!response.ok) {
  throw new Error(data.detail || data.message || `Registration failed: ${response.status}`);
}
```

### **2. Added Debugging**
```typescript
// Added console logging to track registration data
console.log('Sending registration data:', registrationData);
console.log('Registration response:', response.status, data);
console.log('Error message:', errorMessage);
```

### **3. Improved Error Display**
```typescript
// Better error message handling
const errorMessage = error instanceof Error ? error.message : 'Registration failed. Please try again.';
setError(errorMessage);
```

## 🎯 **Result**

### **Better Error Messages:**
- ✅ **Specific Errors**: Now shows "Username already registered" instead of generic 400 error
- ✅ **Debug Information**: Console logs show exactly what data is being sent
- ✅ **User-Friendly**: Clear error messages for users

### **Registration Process:**
1. **User fills form**: Including property selection
2. **Data validation**: Frontend validates form data
3. **API call**: Sends data to `/api/v1/auth/register`
4. **Error handling**: Shows specific backend error messages
5. **Success**: Redirects to login page

## 📊 **Property Field Status**

### **Property Selection Working:**
- ✅ **Properties Loading**: Fetches from `/api/v1/properties/public`
- ✅ **Property Display**: Shows available properties as checkboxes
- ✅ **Property Selection**: Users can select multiple properties
- ✅ **Data Sending**: Property IDs included in registration data

### **Available Properties:**
- **Lubd Chainatown** (ID: 2)
- **Lubd Siam** (ID: 3)

## 🔧 **Technical Details**

### **Registration Data Structure:**
```typescript
const registrationData = {
  username: formData.username.trim(),
  email: formData.email.trim(),
  first_name: formData.first_name.trim(),
  last_name: formData.last_name.trim(),
  phone: formData.phone.trim(),
  role: formData.role,
  password: formData.password,
  is_active: true,
  property_ids: formData.property_ids  // ✅ Property IDs included
};
```

### **Property Selection UI:**
```typescript
{properties.length > 0 ? (
  <div className="space-y-2 max-h-32 overflow-y-auto border border-gray-300 rounded-md p-3">
    {properties.map((property) => (
      <div key={property.id} className="flex items-center">
        <input
          type="checkbox"
          value={property.id}
          checked={formData.property_ids.includes(property.id)}
          onChange={handlePropertyChange}
        />
        <label>{property.name}</label>
      </div>
    ))}
  </div>
) : (
  <div className="border border-gray-300 rounded-md p-3 bg-gray-50">
    <p>Loading properties...</p>
  </div>
)}
```

## 🚀 **How to Test**

### **1. Access Registration Page:**
```
URL: http://localhost/register
```

### **2. Fill Registration Form:**
- **Username**: Use a unique username (not "admin" or "testuser123")
- **Email**: Use a unique email address
- **Other Fields**: Fill in all required fields
- **Properties**: Select one or more properties

### **3. Submit Form:**
- Click "Create account"
- Check browser console for debug information
- See specific error messages if any issues

### **4. Success:**
- User created successfully
- Property access assigned
- Redirected to login page

## 📝 **Common Issues and Solutions**

### **"Username already registered"**
- **Solution**: Use a different username
- **Note**: Usernames must be unique

### **"Email already registered"**
- **Solution**: Use a different email address
- **Note**: Email addresses must be unique

### **Properties not loading**
- **Check**: Browser console for network errors
- **Verify**: Backend properties endpoint is working
- **Test**: `curl http://localhost:8000/api/v1/properties/public`

## ✅ **Status: Fixed**

The registration page is now working correctly with:
- ✅ Proper error handling
- ✅ Property selection functionality
- ✅ Debug information
- ✅ User-friendly error messages

**Access the registration page at:** `http://localhost/register` 