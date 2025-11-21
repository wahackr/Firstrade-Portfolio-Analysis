try:
    from firstrade import account, symbols
    import pyotp
    print("Imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)
