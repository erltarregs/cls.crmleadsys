# test_schemas.py
from app.schemas import UserCreate

tests = [
    ("Password1",          "should FAIL — dictionary word + number"),
    ("qwerty123",          "should FAIL — keyboard pattern"),
    ("Tr0ub4dor&3",        "should PASS — random but memorable"),
    ("correct-horse-2025", "should PASS — passphrase style"),
    ("abc",                "should FAIL — too short (min_length=8)"),
]

for password, label in tests:
    try:
        u = UserCreate(email="test@crm.com", password=password)
        print(f"  ✓ ACCEPTED  '{password}' — {label}")
    except Exception as e:
        # Just show first line of error to keep output clean
        first_line = str(e).split("\\n")[0][:80]
        print(f"  ✗ REJECTED  '{password}' — {label}")
        print(f"             → {first_line}")
    print()