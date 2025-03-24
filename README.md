# Meme Coin Platform

## Overview
Meme Coin is a web-based platform for owning, buying, and selling meme coins. Users can manage their digital wallets, send and receive transactions, and communicate through an internal messaging system.

## Features
- **User Authentication**: Register, login, and manage user accounts.
- **Wallet Management**: Each user has a unique wallet with a balance.
- **Transactions**: Users can send and receive meme coins.
- **Messaging System**: Users can send messages to each other.
- **Dashboard**: Displays transaction statistics and user activity.

## Technologies Used
- **Backend**: Django & Django REST Framework (DRF)
- **Database**: SQLite
- **Authentication**: JWT (Django Simple JWT)
- **Others**: Celery (for async tasks), WebSockets (for live messaging)

## Installation

### 1. Clone the repository
```sh
git clone https://github.com/your-username/meme-coin.git
cd meme-coin
```

### 2.Create a virtual environment and activate it
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3.Install dependencies
```sh
pip install -r requirements.txt
```

### 4.Apply migrations
```sh
python manage.py migrate
```

### 5.Create a superuser (optional)
```sh
python manage.py createsuperuser
```

### 6.Run the development server
```sh
python manage.py runserver
```

## API Endpoints

| Endpoint           | Method | Description                  | Auth Required |
|-------------------|--------|------------------------------|--------------|
| `/users/register/`  | `POST` | Register a new user         | ❌ No       |
| `/users/login/`     | `POST` | User authentication         | ❌ No       |
| `/getwalletaddress/`    | `GET`  | Get user wallet details     | ✅ Yes      |
| `/transactions/` | `POST` | Send meme coin             | ✅ Yes      |
| `/transactionlist/` | `GET` | View transaction history   | ✅ Yes      |
| `/messenger/sendmessage/`   | `POST` | Send a message             | ✅ Yes      |
| `/messenger/readmessages/`  | `GET`  | View received messages     | ✅ Yes      |


## Future Enhancements
- **Integration with a payment gateway**
- **Two-factor authentication (2FA)**
- **WebSocket-based real-time chat system**

> **Developer:** Mohamadreza Heydarnia
> **Date:** March 2025