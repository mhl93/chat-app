# chat-app

## Functional Requirements

1. Direct Message Between Two Users
2. Group Message Between Multiple Users
3. Read Receipts of Message
4. Notification Services

## System Architecture

The chat-app architecture is designed to be modular, consisting of three primary applications: User, Chat, and Notification.
The high level system architecture can be assessed [here](https://drive.google.com/file/d/1JD5qYY9sKX5Qhis-tKO6fOFTzKBu5Vy7/view?usp=drive_link)

###
Framework: Django 5
Language: Python 3.10
Database: RDB, Redis

###Applications
#### User Application

The User Application is responsible for managing user-related functionalities, including:

User Authentication: Manages user login and ensures secure access through token-based authentication. Utilizes Django's built-in authentication system enhanced with Django Rest Framework's token authentication to secure API endpoints.
User Profile Management: Allows users to view and edit their profile information. Profile data includes username, email, and notification preferences

#### Chat Application

The core of the chat functionality, the Chat Application handles message exchanges and chat room management:

Message Retrieval and Posting: Supports fetching historical messages from a specific channel (direct or group) and posting new messages to it. Utilizes Django Channels to handle WebSockets for real-time bi-directional communication.
Broadcast Mechanism: Ensures that new messages are promptly broadcasted to all relevant users within a channel, leveraging Django Channels' group layer functionality for efficient message distribution.
Read Receipts: Tracks the read status of messages to provide read receipts, allowing users to see when their messages have been seen by the recipient(s).

#### Notification Application

Email Notifications: Sends email notifications for important events like new messages or mentions within chats. Built on Django's email backend, it allows for easy integration with SMTP services for email delivery.
Push Notifications (Work In Progress): Aimed at extending the notification system to include real-time push notifications to user devices for immediate alerts. Planned implementation using services like Firebase Cloud Messaging (FCM) for broad compatibility with Android and iOS devices.

### High-Level Data Flow

User Registration and Authentication: Users receives a token for subsequent API requests.
Message Exchange: Authenticated users send and receive messages through the Chat Application. Messages are stored in a relational database and distributed in real-time via WebSockets.
Notifications: Upon receiving a new message, the Notification Application triggers an email alert to the user(s) if they're not currently online. Push notifications are planned for immediate alerts regardless of the user's current state.

### DB Models
(WIP)
