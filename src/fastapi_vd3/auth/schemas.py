from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    username: str
    role: str
    user_id: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True