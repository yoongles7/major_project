# Major Project - API Documentation

## Table of Contents
1. [Base Information](#base-information)
2. [Authentication Endpoints](#authentication-endpoints)
3. [Stock Data Endpints](#stock-data-endpoints)
4. [Trading Endpoints](#trading-endpoints)
5. [Portfolio Endpoints](#portfolio-endpoints)
6. [Market Data Endpoints](#market-data-endpoints)

---

## Base Information

| Property | Value |
|----------|-------|
| **Base URL** | `http://localhost:8000` |
| **Content Type** | `application/json` |
| **Authentication** | JWT (JSON Web Tokens) |

---

## Authentication

### How to Authenticate
1. **Login** → Get `access` and `refresh` tokens
2. **Store** → tokens in localStorage/sessionStorage
3. **Include** → token in all requests:

Authorization: Bearer <your_access_token>

## Authentication Endpoints

1. ### /users_authentication/register/ : Create new account
   
   **Request**
   ```
   {
    "username": "your_username",
    "email": "example@example.com",
    "password": "your_password",
    "password_confirmation": "your_password"
   }
   ```
   **Success Response (201 Created)**
   ```
   {
    "user": {
        "email": "pritikas@gmail.com",
        "username": "yoongles",
        "password": "Katsuki0420",
        "password_confirmation": "Katsuki0420"
    },
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
    ```
    **Error Response (400 Bad Request)**
    ```
    {
    "username": [
        "A user with that username already exists."
    ],
    "email": [
        "user with this email already exists."
    ]
    }
    ```

2. ### /users_authentication/login/ : login to existing account
   
   **Request**
   ```
   {
    "username": "your_username", 
    "password": "your_password"
   }
   ```
   **Success Response (200 OK)**
   ```
   {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   ```

   **Error Response (401 Unauthorized)**
   ```
   {
    "detail": "No active account found with the given credentials"
   }
   ```

3. ### /users_authentication/refresh/ : Refresh token when expired
    
   **Request**
   ```
   {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."  
   }
   ```
   **Success Response (200 OK)**
   ```
   {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   }
   ```
   **Error Response (401 Unauthorized)**
   ```
   {
    "detail": "Token is invalid",
    "code": "token_not_valid"
   }
   ```

## Stock Data Endpoints

1. ### /trading/stocks/ : List of stocks
   
   **Success Response (200 OK)**
   ```
   {
    "count": 150,
    "next": "http://localhost:8000/api/trading/stocks/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "symbol": "NIC",
            "name": "NIC Asia Bank",
            "current_price": 425.50,
            "sector": "Banking",
            "change_percent": 2.5,
            "day_high": 430.00,
            "day_low": 420.00,
            "volume": 125000,
            "last_updated": "2024-01-15T14:30:00Z"
        },
        {
            "id": 2,
            "symbol": "NMB",
            "name": "NMB Bank",
            "current_price": 215.75,
            "sector": "Banking",
            "change_percent": -0.8,
            "day_high": 218.00,
            "day_low": 214.50,
            "volume": 98000,
            "last_updated": "2024-01-15T14:30:00Z"
        }
    ]
    }
    ```

2. ### /trading/stocks/{symbol}/ : Single stock details
   
   **Sucess Response (200 OK)**
   ```
   {
    {
    "symbol": "BNL",
    "price": 15657.0,
    "change": 0.0
    }
   }
   ```


## Trading Endpoints

1. ### /trading/buy/ : to buy stocks
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Request** 
   ```
   {
    "symbol": "NIC",
    "quantity": 10
   }
   ```
   **Success Response (201 Created)**
   ```
   {
    "trade_id": 101,
    "message": "Successfully bought 10 shares of NIC",
    "stock": {
        "symbol": "NIC",
        "name": "NIC Asia Bank",
        "price_per_share": 425.50
    },
    "quantity": 10,
    "total_amount": 4255.00,
    "timestamp": "2024-01-15T14:35:22Z",
    "remaining_balance": 95745.00,
    "new_holding": {
        "symbol": "NIC",
        "quantity": 10,
        "average_price": 425.50,
        "current_value": 4255.00,
        "profit_loss": 0
    }
    }
    ```
    **Error Response**
    1. Insufficient Balance (400 Bad Request)
    ```
    {
    "error": "Insufficient balance",
    "available": 95745.00,
    "required": 100000.00,
    "code": "insufficient_funds"
    }
    ```
    2. Market Closed (400 Bad Request)
    ```
    {
    "warning": "Market is currently closed. Order will be processed when market opens.",
    "market_hours": "NEPSE: Sunday-Thursday, 11:00 AM - 3:00 PM NPT"
    }
    ```
    3. Invalid Quantity (400 Bad Request)
    ```
    {
    "error": "Quantity must be greater than 0"
    }
    ```

2. ### /trading/sell/ : sell your holdings/stocks
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Request**
   ```
   {
    "symbol": "NIC",
    "quantity": 5
   }
   ```
   **Success Response (201 Created)**
   ```
   {
    "trade_id": 102,
    "message": "Successfully sold 5 shares of NIC",
    "stock": {
        "symbol": "NIC",
        "name": "NIC Asia Bank",
        "price_per_share": 430.25
    },
    "quantity": 5,
    "total_amount": 2151.25,
    "timestamp": "2024-01-15T14:40:15Z",
    "updated_balance": 97872.50,
    "updated_holding": {
        "symbol": "NIC",
        "quantity": 5,
        "average_price": 425.50,
        "current_value": 2151.25,
        "profit_loss": 12.75
    }
    }
    ```
    **Error Response**
    1. No Holdings (400 Bad Request)
    ```
    {
    "error": "You don't own any shares of NIC"
    }
    ```
    2. Insufficient Shares (400 Bad Request)
    ```
    {
    "error": "Insufficient shares",
    "available": 5,
    "requested": 10,
    "code": "insufficient_shares"
    }
    ```

3. ### /trading/holdings/ : Get user's holdings
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```
   {
    "holdings": [],
    "summary": {
        "cash_balance": 95087.5,
        "stock_value": 0.0,
        "total_portfolio_value": 95087.5,
        "total_invested": 0.0,
        "total_profit_loss": 0.0,
        "total_profit_loss_percentage": 0,
        "number_of_holdings": 0,
        "last_updated": "2026-03-02T12:47:30.475277+00:00"
    }
    }
    ```

4. ### /trading/holdings/{symbol}/ : Get golding details
   
   Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```

5. ### /trading/history/ : get trades history

   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```
   {
    "count": 25,
    "next": "http://localhost:8000/api/trading/trades/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 102,
            "symbol": "NIC",
            "company_name": "NIC Asia Bank",
            "order_type": "SELL",
            "quantity": 5,
            "price_per_share": 430.25,
            "total_amount": 2151.25,
            "timestamp": "2024-01-15T14:40:15Z",
            "status": "EXECUTED"
        },
        {
            "id": 101,
            "symbol": "NIC",
            "company_name": "NIC Asia Bank",
            "order_type": "BUY",
            "quantity": 10,
            "price_per_share": 425.50,
            "total_amount": 4255.00,
            "timestamp": "2024-01-15T14:35:22Z",
            "status": "EXECUTED"
        }
    ]
    }
    ```


## Portfolio Endpoints        

1. ### /trading/portfolio/ : Get portfolio
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```
   {
    "portfolio": {
        "id": 1,
        "cash_balance": "95087.50",
        "total_value": 95087.5,
        "total_profit_loss": 0.0,
        "holdings_count": 0,
        "holdings": [],
        "updated_at": "2026-02-15T17:25:11.315663Z",
        "created_at": "2026-02-14T15:28:18.023392Z"
    },
    "stats": {
        "total_trades": 0,
        "total_buys": 0,
        "total_sells": 0
    },
    "recent_trades": []
    }
    ```

2. ### /trading/portfolio/performance/ : get portfolio performance metrics
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```
   {
    "timeline": [
        {
            "date": "2026-01-31T12:41:52.235883",
            "value": 95087.5
        },
        {
            "date": "2026-03-01T12:41:52.235883",
            "value": 95087.5
        }
    ],
    "period": "30_days"
    }
    ```

3. ### /trading/portfolio/dashboard/ : get portfolio summary
   
   **Headers**
   ```
   Authorization: Bearer <access_token>
   ```
   **Success Response (200 OK)**
   ```
   {
    "summary": {
        "cash_balance": 95087.5,
        "total_invested": 0.0,
        "total_stock_value": 0.0,
        "total_portfolio_value": 95087.5,
        "total_profit_loss": 0.0,
        "profit_loss_percentage": 0,
        "holdings_count": 0,
        "total_trades": 0,
        "diversification_score": 0
    },
    "holdings": [],
    "recent_trades": [],
    "top_performers": [],
    "worst_performers": [],
    "sector_breakdown": [],
    "charts": {
        "portfolio_growth": [],
        "sector_allocation": []
    }
    }
    ```


## Market Data Endpoints

1. ### /trading/market-status/ : Get live market status

   **Success Response (200 OK)**
   ```
   {
    "status": "OPEN",
    "badge": {
        "color": "green",
        "text": "OPEN"
    },
    "is_open": true,
    "is_halted": false,
    "is_closed": false,
    "trading_allowed": true,
    "message": "Market is OPEN (estimated)",
    "current_time": "2026-03-10T13:34:26.382193+05:45",
    "market_hours": "Sunday-Thursday, 11:00 AM - 3:00 PM NPT",
    "source": "local calculation (API unavailable)"
    }
   ```