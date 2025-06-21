# 🗑️ Deletion Endpoints Documentation

## Overview
This document provides comprehensive information about the deletion endpoints available for your frontend application.

---

## 🔐 Authentication Required
All deletion endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {your_jwt_token}
```

---

## 👤 User Account Deletion

### 1. Delete My Account (Recommended)
**Endpoint:** `DELETE /auth/account/delete`  
**Description:** Delete the current user's account and associated mall  
**Authentication:** Required (Bearer token)

#### Request
```javascript
const response = await fetch('/auth/account/delete', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

#### Response
```json
{
  "success": true,
  "message": "Your account and associated mall have been deleted successfully",
  "user_id": 123
}
```

#### Error Responses
```json
// 404 - User not found
{
  "detail": "User account not found"
}

// 500 - Server error
{
  "detail": "Failed to delete your account"
}
```

### 2. Delete Specific User Account
**Endpoint:** `DELETE /auth/user/{user_id}`  
**Description:** Delete a specific user account (only own account allowed)  
**Authentication:** Required (Bearer token)

#### Request
```javascript
const userId = 123;
const response = await fetch(`/auth/user/${userId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

#### Response
```json
{
  "success": true,
  "message": "Account and associated mall deleted successfully",
  "user_id": 123
}
```

#### Error Responses
```json
// 403 - Forbidden (trying to delete another user's account)
{
  "detail": "You can only delete your own account"
}

// 404 - User not found
{
  "detail": "User not found"
}
```

---

## 🏢 Mall Deletion

### 1. Delete My Mall (Recommended)
**Endpoint:** `DELETE /mall/delete-my-mall`  
**Description:** Delete the current user's mall  
**Authentication:** Required (Bearer token)

#### Request
```javascript
const response = await fetch('/mall/delete-my-mall', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

#### Response
```json
{
  "success": true,
  "message": "Your mall has been deleted successfully",
  "mall_id": 456
}
```

#### Error Responses
```json
// 404 - No mall to delete
{
  "detail": "You don't have a mall to delete"
}

// 404 - Mall not found
{
  "detail": "Mall not found"
}
```

### 2. Delete Specific Mall
**Endpoint:** `DELETE /mall/{mall_id}`  
**Description:** Delete a specific mall (only own mall allowed)  
**Authentication:** Required (Bearer token)

#### Request
```javascript
const mallId = 456;
const response = await fetch(`/mall/${mallId}`, {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

#### Response
```json
{
  "success": true,
  "message": "Mall deleted successfully",
  "mall_id": 456
}
```

#### Error Responses
```json
// 403 - Forbidden (trying to delete another user's mall)
{
  "detail": "You can only delete your own mall"
}

// 404 - Mall not found
{
  "detail": "Mall not found"
}
```

---

## 🚀 Frontend Implementation Examples

### React/TypeScript Implementation

#### 1. Account Deletion Hook
```typescript
import { useState } from 'react';
import { useAuth } from './useAuth';

export const useAccountDeletion = () => {
  const [isDeleting, setIsDeleting] = useState(false);
  const { token, logout } = useAuth();

  const deleteAccount = async () => {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch('/auth/account/delete', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        logout(); // Redirect to login page
        return true;
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return false;
      }
    } catch (error) {
      console.error('Account deletion failed:', error);
      alert('Failed to delete account. Please try again.');
      return false;
    } finally {
      setIsDeleting(false);
    }
  };

  return { deleteAccount, isDeleting };
};
```

#### 2. Mall Deletion Hook
```typescript
import { useState } from 'react';
import { useAuth } from './useAuth';

export const useMallDeletion = () => {
  const [isDeleting, setIsDeleting] = useState(false);
  const { token } = useAuth();

  const deleteMall = async () => {
    if (!confirm('Are you sure you want to delete your mall? This will also delete all associated cameras and data.')) {
      return;
    }

    setIsDeleting(true);
    try {
             const response = await fetch('/mall/delete-my-mall', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        // Refresh user data or redirect to mall creation page
        return true;
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return false;
      }
    } catch (error) {
      console.error('Mall deletion failed:', error);
      alert('Failed to delete mall. Please try again.');
      return false;
    } finally {
      setIsDeleting(false);
    }
  };

  return { deleteMall, isDeleting };
};
```

#### 3. Account Settings Component
```tsx
import React from 'react';
import { useAccountDeletion } from './hooks/useAccountDeletion';
import { useMallDeletion } from './hooks/useMallDeletion';

export const AccountSettings: React.FC = () => {
  const { deleteAccount, isDeleting: isDeletingAccount } = useAccountDeletion();
  const { deleteMall, isDeleting: isDeletingMall } = useMallDeletion();

  return (
    <div className="account-settings">
      <h2>Account Settings</h2>
      
      <div className="danger-zone">
        <h3>Danger Zone</h3>
        
        <div className="delete-section">
          <h4>Delete Mall</h4>
          <p>This will permanently delete your mall and all associated data.</p>
          <button 
            onClick={deleteMall}
            disabled={isDeletingMall}
            className="btn-danger"
          >
            {isDeletingMall ? 'Deleting...' : 'Delete Mall'}
          </button>
        </div>

        <div className="delete-section">
          <h4>Delete Account</h4>
          <p>This will permanently delete your account, mall, and all associated data.</p>
          <button 
            onClick={deleteAccount}
            disabled={isDeletingAccount}
            className="btn-danger"
          >
            {isDeletingAccount ? 'Deleting...' : 'Delete Account'}
          </button>
        </div>
      </div>
    </div>
  );
};
```

---

## ⚠️ Important Notes

### 1. Cascade Deletion
- **Deleting a user account** will automatically delete:
  - Associated mall
  - All cameras in the mall
  - All customer data
  - All analytics data

- **Deleting a mall** will automatically delete:
  - All cameras in the mall
  - All customer data
  - All analytics data
  - User's mall_id will be set to NULL

### 2. Security Features
- Users can only delete their own accounts
- Users can only delete their own malls
- All deletions require valid authentication
- No admin privileges are currently implemented

### 3. ID Management Integration
- Deleted user IDs and mall IDs will be reused for new records (gap filling)
- This maintains clean, sequential numbering
- Statistics available at `/id-management/statistics`

### 4. Error Handling
- Always check response status codes
- Handle network errors gracefully
- Provide user feedback for all operations
- Implement confirmation dialogs for destructive actions

---

## 🧪 Testing the Endpoints

### Using curl
```bash
# Get auth token first
TOKEN="your_jwt_token_here"

# Delete current user's mall
curl -X DELETE "http://localhost:8000/mall/delete-my-mall" \
  -H "Authorization: Bearer $TOKEN"

# Delete current user's account
curl -X DELETE "http://localhost:8000/auth/account/delete" \
  -H "Authorization: Bearer $TOKEN"
```

### Using your test scripts
```bash
# Test the deletion functionality
python test_account_deletion.py
```

---

## 📊 Available Endpoints Summary

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/auth/account/delete` | DELETE | Delete current user's account | Required |
| `/auth/user/{user_id}` | DELETE | Delete specific user account | Required |
| `/mall/delete-my-mall` | DELETE | Delete current user's mall | Required |
| `/mall/{mall_id}` | DELETE | Delete specific mall | Required |

All endpoints return JSON responses with success/error information. 