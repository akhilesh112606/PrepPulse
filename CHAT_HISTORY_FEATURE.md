# 💬 Chat History Feature

## Overview
Users can now see their previous chat conversations when they log back into their account. All chat messages are stored in the database and automatically loaded when the user visits the dashboard.

## Features Implemented

### 1. **Database Schema**
- New `chat_history` table with the following columns:
  - `id` - Primary key (auto-increment)
  - `email` - User email for association
  - `user_message` - The message sent by the user
  - `assistant_response` - The AI response
  - `context` - Additional context (resume analysis, etc.)
  - `created_at` - Timestamp of the message

### 2. **Database Functions** (`app/db.py`)

#### `save_chat_message(db_path, email, user_message, assistant_response, context="")`
- Saves a user message and AI response to chat history
- Called automatically after each chat interaction
- Stores the timestamp automatically

#### `get_chat_history(db_path, email, limit=50)`
- Retrieves the most recent chat messages for a user
- Returns up to `limit` messages (default 50)
- Returns messages in reverse chronological order (newest first)

#### `get_chat_history_paginated(db_path, email, offset=0, limit=20)`
- Retrieves paginated chat history
- Returns `limit` messages starting from `offset`
- Useful for infinite scroll or pagination UI

#### `delete_chat_history(db_path, email)`
- Deletes all chat history for a user
- Returns count of deleted messages

#### `delete_chat_message(db_path, message_id)`
- Deletes a specific chat message by ID
- Returns count of deleted messages (0 or 1)

### 3. **Backend Routes** (`app/routes.py`)

#### **POST /chat**
Updated to automatically save chat messages:
```python
# When user sends a message, it's saved to database
save_chat_message(
    database_path,
    email,
    user_message,
    reply,
    context_text
)
```

#### **GET /api/chat-history**
Retrieves chat history for logged-in user
- **Query Parameters:**
  - `limit` (default: 50) - Maximum messages to retrieve
  - `offset` (default: 0) - Pagination offset

- **Response:**
  ```json
  {
    "success": true,
    "history": [
      {
        "id": 1,
        "user_message": "What courses are available?",
        "assistant_response": "We offer the following courses...",
        "context": "...",
        "created_at": "2026-02-28T10:30:00"
      },
      ...
    ],
    "count": 50,
    "offset": 0,
    "limit": 50
  }
  ```

#### **DELETE /api/chat-history**
Deletes all chat history for the user
- **Response:**
  ```json
  {
    "success": true,
    "deleted": 50,
    "message": "Deleted 50 chat messages"
  }
  ```

#### **DELETE /api/chat-history/<int:message_id>**
Deletes a specific chat message
- **Response:**
  ```json
  {
    "success": true,
    "message": "Message deleted successfully"
  }
  ```

### 4. **Frontend Integration** (`app/static/js/dashboard-chatbot.js`)

#### Automatic Chat History Loading
- When user opens the dashboard, the page automatically loads their previous chat messages
- Messages are displayed in chronological order (oldest to newest)
- Max 50 most recent messages are loaded

#### How It Works:
1. Page loads → `loadChatHistory()` function executes
2. Fetches `/api/chat-history?limit=50`
3. Returns messages in newest-first order
4. JavaScript reverses the order for display
5. All messages are rendered in the chat panel
6. User can continue chatting from where they left off

### 5. **User Experience Flow**

```
┌─ User Logs In ──────────────────────┐
│                                      │
│  Dashboard Loads                     │
│    ↓                                 │
│  loadChatHistory() Executes          │
│    ↓                                 │
│  Fetch /api/chat-history             │
│    ↓                                 │
│  Display Previous Messages in Chat   │
│    ↓                                 │
│  User Can Send New Messages          │
│    ↓                                 │
│  New Message Saved to chat_history   │
│    ↓                                 │
│  Next Login → See All Messages       │
│                                      │
└──────────────────────────────────────┘
```

## Code Changes Summary

### Database (`app/db.py`)
- ✅ Added `chat_history` table creation in `init_db()`
- ✅ Added 5 new functions for chat history management

### Routes (`app/routes.py`)
- ✅ Imported chat history functions
- ✅ Updated `/chat` endpoint to save messages
- ✅ Added `GET /api/chat-history` endpoint
- ✅ Added `DELETE /api/chat-history` endpoint
- ✅ Added `DELETE /api/chat-history/<id>` endpoint

### Frontend (`app/static/js/dashboard-chatbot.js`)
- ✅ Added `loadChatHistory()` function
- ✅ Auto-load chat history on page load
- ✅ Display previous messages before greeting

## Example Usage

### JavaScript - Retrieve Chat History
```javascript
// Fetch chat history
fetch('/api/chat-history?limit=50&offset=0')
  .then(res => res.json())
  .then(data => {
    console.log(`Loaded ${data.count} messages`);
    console.log(data.history);
  });
```

### JavaScript - Delete All Chat History
```javascript
// Delete all messages
fetch('/api/chat-history', { method: 'DELETE' })
  .then(res => res.json())
  .then(data => console.log(`${data.deleted} messages deleted`));
```

### Python - Save a Chat Message
```python
from app.db import save_chat_message

save_chat_message(
    database_path="data/preppulse.db",
    email="user@example.com",
    user_message="What's the best way to prepare?",
    assistant_response="I recommend focusing on these areas...",
    context="resume_analysis"
)
```

### Python - Retrieve Chat History
```python
from app.db import get_chat_history

history = get_chat_history(
    database_path="data/preppulse.db",
    email="user@example.com",
    limit=20
)

for msg in history:
    print(f"User: {msg['user_message']}")
    print(f"AI: {msg['assistant_response']}")
    print(f"Time: {msg['created_at']}")
```

## Data Persistence
- ✅ Chat messages are persisted across user sessions
- ✅ History is user-specific (linked to email)
- ✅ Messages include timestamps for reference
- ✅ Context data is stored for reference

## Logging
The system includes detailed logging:
- `✅ [CHATBOT] Chat message saved to history for user@example.com`
- `✅ [CHATBOT] Retrieved 20 chat history messages for user@example.com`
- `✅ [CHATBOT] Deleted 50 chat messages for user@example.com`
- `⚠️  [CHATBOT] Warning: Could not save chat history: [error]`

## Benefits
1. **Continuity** - Users see their entire conversation history
2. **Reference** - Easy to look back at previous advice
3. **Context** - LLM can better understand ongoing discussions
4. **Analytics** - Track user interactions and popular topics
5. **Recovery** - Can revisit solutions to previous questions

## Future Enhancements
- [ ] Search through chat history
- [ ] Export chat history as PDF/TXT
- [ ] Categorize chats by topic
- [ ] Summarize chat sessions
- [ ] Share chat conversations
- [ ] Star/bookmark important messages
- [ ] Advanced analytics dashboard

## Testing

### Test 1: Save and Retrieve
1. Log in as a user
2. Send a chat message
3. Check database: `SELECT * FROM chat_history WHERE email = 'user@example.com';`
4. Verify message is saved with timestamp

### Test 2: Load on Dashboard
1. Log in and send a message
2. Log out
3. Log back in
4. Previous message should appear in chat panel
5. Open browser console: `fetch('/api/chat-history').then(r => r.json()).then(console.log)`
6. Verify messages are returned

### Test 3: Delete History
1. Open browser console
2. Run: `fetch('/api/chat-history', {method: 'DELETE'}).then(r => r.json()).then(console.log)`
3. Refresh page
4. Chat history should be gone
5. Check database - no records for user

## Schema Details
```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    context TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```

## Performance Notes
- Loads max 50 messages on dashboard load (configurable)
- Database queries use simple indexed lookups
- No N+1 queries
- Pagination support for large histories
- Consider archiving old messages if table grows >100k rows
