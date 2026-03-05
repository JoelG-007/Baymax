from database.db_init import SessionLocal
from database.models import User
from auth.security import hash_password, verify_password
from database.crud import log_login_attempt


# -----------------------------
# REGISTER USER
# -----------------------------
def register(username, email, password):
    db = SessionLocal()
    username = username.strip().lower()
    email = email.strip().lower()

    if db.query(User).filter(User.email == email).first():
        db.close()
        return "Email already registered"

    if db.query(User).filter(User.username == username).first():
        db.close()
        return "Username already taken"

    db.add(User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    ))
    db.commit()
    db.close()
    return "User created successfully"


# -----------------------------
# AUTHENTICATE USER
# -----------------------------
def authenticate(identifier, password):
    db = SessionLocal()
    identifier = identifier.strip().lower()

    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    # User not found
    if not user:
        db.close()
        log_login_attempt(identifier, success=False)
        return None

    # Wrong password
    if not verify_password(password, user.hashed_password):
        db.close()
        log_login_attempt(identifier, success=False)
        return None

    # Suspended
    if not user.is_active:
        db.close()
        log_login_attempt(identifier, success=False)
        return None

    db.close()
    log_login_attempt(identifier, success=True)
    return user