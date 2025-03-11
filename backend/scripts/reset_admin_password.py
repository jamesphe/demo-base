from app.db.session import SessionLocal
from app.core.security import reset_admin_password

def reset_password():
    db = SessionLocal()
    try:
        new_hash = reset_admin_password()
        db.execute(
            "UPDATE users SET hashed_password = :hash "
            "WHERE email = 'admin@admin.com'",
            {"hash": new_hash}
        )
        db.commit()
        print("Admin password reset successfully")
    except Exception as e:
        print(f"Error resetting password: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_password() 