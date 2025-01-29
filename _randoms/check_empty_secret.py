import jwt
import sys

def is_signed_with_empty_secret(token):
    try:
        header = jwt.get_unverified_header(token)
        algo = header.get("alg", "")

        if algo not in ["HS256", "HS384", "HS512"]:
            print("[!] Not an HMAC-signed token or unsupported algorithm.")
            return False

        # Decode without validating claims (only signature check)
        jwt.decode(token, key="", algorithms=[algo], options={"verify_signature": True, "verify_exp": False})

        print("[+] Token is signed using an empty secret!")
        return True
    except jwt.InvalidSignatureError:
        print("[-] Token signature verification failed.")
    except jwt.DecodeError:
        print("[-] Token is invalid.")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <jwt_token>")
        sys.exit(1)

    token = sys.argv[1]
    is_signed_with_empty_secret(token)
