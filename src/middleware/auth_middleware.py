from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = os.getenv("ALGORITHM")
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify JWT token"""
        try:
            payload = jwt.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_current_user(self, request: Request):
        """Get current authenticated user"""
        # TODO: Implement user extraction from token
        return {"user_id": 1, "email": "user@example.com"} 