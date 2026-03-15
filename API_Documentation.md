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
   ```{
    "market_status": {
        "status": "OPEN",
        "is_open": true,
        "is_halted": false,
        "is_closed": false,
        "trading_allowed": true,
        "message": "Market is OPEN for trading",
        "raw_status": "OPEN",
        "current_time": "2026-03-15T14:23:48.154807",
        "market_hours": "Sunday-Thursday, 11:00 AM - 3:00 PM NPT"
    },
    "stocks": [
        {
            "id": 650,
            "symbol": "NHPC",
            "name": "National Hydro Power Company Limited",
            "sector": "Hydro Power",
            "current_price": 284.6,
            "change": -1.9,
            "high": 295.0,
            "low": 277.0,
            "volume": 1785000,
            "price_source": "live"
        },
        {
            "id": 692,
            "symbol": "BNL",
            "name": "Bottlers Nepal (Balaju) Limited",
            "sector": "Manufacturing And Processing",
            "current_price": 15355.0,
            "change": 0,
            "high": 15355.0,
            "low": 15355.0,
            "volume": 10,
            "price_source": "live"
        },
        {
            "id": 630,
            "symbol": "NIMB",
            "name": "Nepal Investment Mega Bank Limited",
            "sector": "Commercial Banks",
            "current_price": 215.5,
            "change": 0.19,
            "high": 219.4,
            "low": 212.6,
            "volume": 303409,
            "price_source": "live"
        },
        {
            "id": 685,
            "symbol": "NLIC",
            "name": "Nepal Life Insurance Co. Ltd.",
            "sector": "Life Insurance",
            "current_price": 808.4,
            "change": -0.44,
            "high": 820.0,
            "low": 805.0,
            "volume": 37390,
            "price_source": "live"
        }
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

1. ### /market-data/status/ : Get live market status

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

2. ### /market-data/prices/ : Get live prices

   **Success Response (200 OK)**
   ```
   [
    {
        "symbol": "NABIL",
        "lastTradedPrice": 1850.5,
        "percentageChange": 1.25,
        "companyName": "NABIL Company",
        "source": "mock"
    },
    {
        "symbol": "NIC",
        "lastTradedPrice": 420.75,
        "percentageChange": -0.5,
        "companyName": "NIC Company",
        "source": "mock"
    }
   ]
   ```

3. ### /market-data/price/<symbol>/ : get price for a single stock
   
   **Success Response(200 OK)**
   ```
   {
    "price": 210.3,
    "change": 0.75,
    "source": "mock (market closed/halted)",
    "market_status": {
        "is_open": false,
        "message": "Market is CLOSED"
    },
    "nepal_time": "2026-03-15T22:25:15.711418+05:45",
    "last_updated": "2026-03-15T16:40:15.711446"
    }
    ```

4. ### /market-data/intraday/ : intraday chart
   
   **Success Response (200 OK)**
   ```
   {
    "symbol": "NABIL",
    "market_status": {
        "status": "CLOSE",
        "is_open": false,
        "is_halted": false,
        "is_closed": true,
        "trading_allowed": false,
        "message": "Market is CLOSED",
        "raw_status": "CLOSE",
        "current_time": "2026-03-15T15:00:00",
        "market_hours": "Sunday-Thursday, 11:00 AM - 3:00 PM NPT"
    },
    "data": [
        {
            "time": "18:25",
            "timestamp": "2026-03-15T18:25:55+05:45",
            "open": 1855.26,
            "high": 1863.81,
            "low": 1853.89,
            "close": 1861.46,
            "volume": 6585
        },
        {
            "time": "19:25",
            "timestamp": "2026-03-15T19:25:55+05:45",
            "open": 1865.1,
            "high": 1871.09,
            "low": 1862.59,
            "close": 1868.15,
            "volume": 4876
        },
        {
            "time": "20:25",
            "timestamp": "2026-03-15T20:25:55+05:45",
            "open": 1865.32,
            "high": 1868.4,
            "low": 1864.57,
            "close": 1867.74,
            "volume": 1549
        },
        {
            "time": "21:25",
            "timestamp": "2026-03-15T21:25:55+05:45",
            "open": 1868.6,
            "high": 1869.12,
            "low": 1862.12,
            "close": 1864.19,
            "volume": 1600
        },
        {
            "time": "22:25",
            "timestamp": "2026-03-15T22:25:55+05:45",
            "open": 1859.61,
            "high": 1862.4,
            "low": 1855.29,
            "close": 1855.89,
            "volume": 6164
        }
    ],
    "data_points": 5,
    "timezone": "Asia/Kathmandu (NPT)"
   }
   ```

5. ### /market-data/search/ : search stocks
   
   **Success Response (200 OK)**
   ```
   [
    {
        "id": 131,
        "companyName": "Nabil Bank Limited",
        "symbol": "NABIL",
        "securityName": "Nabil Bank Limited",
        "status": "A",
        "companyEmail": "company.affairs@nabilbank.com",
        "website": "www.nabilbank.com",
        "sectorName": "Commercial Banks",
        "regulatoryBody": "Nepal Rastra Bank",
        "instrumentType": "Equity"
    },
    {
        "id": 132,
        "companyName": "Nepal Investment Mega Bank Limited",
        "symbol": "NIMB",
        "securityName": "Nepal Investment Mega Bank Limited",
        "status": "A",
        "companyEmail": "info@nimb.com.np",
        "website": "http://www.nimb.com.np",
        "sectorName": "Commercial Banks",
        "regulatoryBody": "Nepal Rastra Bank",
        "instrumentType": "Equity"
    }
   ]
   ```

6. ### /market-data/summary : get market summary
   
   **Success Response (200 OK)**
   ```
   {
    "summary": {
        "Total Turnover Rs:": 14329604315.9,
        "Total Traded Shares": 39549033.0,
        "Total Transactions": 124490.0,
        "Total Scrips Traded": 350.0,
        "Total Market Capitalization Rs:": 4787469974229.3,
        "Total Float Market Capitalization Rs:": 1631040274256.9
    },
    "nepse_index": {
        "Sensitive Index": {
            "id": 57,
            "auditId": null,
            "exchangeIndexId": null,
            "generatedTime": "2026-03-15T15:23:36.417",
            "index": "Sensitive Index",
            "close": 486.39,
            "high": 490.3112,
            "low": 484.5843,
            "previousClose": 486.8041,
            "change": 0.41,
            "perChange": 0.08,
            "fiftyTwoWeekHigh": 518.6,
            "fiftyTwoWeekLow": 434.98,
            "currentValue": 486.8
        },
        "NEPSE Index": {
            "id": 58,
            "auditId": null,
            "exchangeIndexId": null,
            "generatedTime": "2026-03-15T15:23:36.417",
            "index": "NEPSE Index",
            "close": 2820.45,
            "high": 2839.3544,
            "low": 2808.5736,
            "previousClose": 2824.9052,
            "change": 4.45,
            "perChange": 0.15,
            "fiftyTwoWeekHigh": 3002.08,
            "fiftyTwoWeekLow": 2487.18,
            "currentValue": 2824.9
        },
        "Float Index": {
            "id": 62,
            "auditId": null,
            "exchangeIndexId": null,
            "generatedTime": "2026-03-15T15:23:36.417",
            "index": "Float Index",
            "close": 195.07,
            "high": 196.4734,
            "low": 194.2649,
            "previousClose": 195.2224,
            "change": 0.14,
            "perChange": 0.07,
            "fiftyTwoWeekHigh": 206.26,
            "fiftyTwoWeekLow": 170.58,
            "currentValue": 195.22
        },
        "Sensitive Float Index": {
            "id": 63,
            "auditId": null,
            "exchangeIndexId": null,
            "generatedTime": "2026-03-15T15:23:36.417",
            "index": "Sensitive Float Index",
            "close": 165.83,
            "high": 167.2632,
            "low": 165.2371,
            "previousClose": 166.0159,
            "change": 0.18,
            "perChange": 0.11,
            "fiftyTwoWeekHigh": 177.31,
            "fiftyTwoWeekLow": 145.59,
            "currentValue": 166.01
        }
    },
    "top_gainers": [
        {
            "symbol": "NABIL",
            "companyName": "NABIL",
            "lastTradedPrice": 1850.5,
            "percentageChange": 1.25,
            "volume": 0
        },
        {
            "symbol": "NMB",
            "companyName": "NMB",
            "lastTradedPrice": 210.3,
            "percentageChange": 0.75,
            "volume": 0
        },
        {
            "symbol": "PCBL",
            "companyName": "PCBL",
            "lastTradedPrice": 180.25,
            "percentageChange": 0.5,
            "volume": 0
        },
        {
            "symbol": "ADBL",
            "companyName": "ADBL",
            "lastTradedPrice": 320.0,
            "percentageChange": 0.4,
            "volume": 0
        },
        {
            "symbol": "PRVU",
            "companyName": "PRVU",
            "lastTradedPrice": 300.5,
            "percentageChange": 0.3,
            "volume": 0
        }
    ],
    "top_losers": [
        {
            "symbol": "HDL",
            "companyName": "HDL",
            "lastTradedPrice": 1500.5,
            "percentageChange": -1.2,
            "volume": 0
        },
        {
            "symbol": "NIC",
            "companyName": "NIC",
            "lastTradedPrice": 420.75,
            "percentageChange": -0.5,
            "volume": 0
        },
        {
            "symbol": "SBI",
            "companyName": "SBI",
            "lastTradedPrice": 450.0,
            "percentageChange": -0.25,
            "volume": 0
        },
        {
            "symbol": "CZBIL",
            "companyName": "CZBIL",
            "lastTradedPrice": 400.25,
            "percentageChange": -0.1,
            "volume": 0
        }
    ],
    "last_updated": "2026-03-15T22:27:42.936019+05:45"
    }
    ```