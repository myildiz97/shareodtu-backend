from models.user_model.user_model import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_user_from_db(email: str) -> User | None:
    try:
        user = await User.find_one(User.email == email)
        return user
    except Exception as e:
        return {"message": "User not found", "error": str(e)}
    
    
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)