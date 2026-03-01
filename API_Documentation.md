# Major Project - API Documentation

## Table of Contents
1. [Base Information](#base-information)
2. [Authentication Endpoints](#authentication-endpoints)

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
2. **Store** tokens in localStorage/sessionStorage
3. **Include** token in all requests:

Authorization: Bearer <your_access_token>

## Authentication Endpoints

1. **/users_authentication/register/** : Create new user
   
   ### Request 
   {
    "username": "your_username",
    "email": "example@example.com",
    "password": "your_password",
    "password_confirmation": "your_password"
   }

   ### Response