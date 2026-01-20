"""
Helper script to update SECRET_KEY in .env file
This is used by start-backend.bat to generate and set the SECRET_KEY
"""
import secrets
import re
import sys

def update_secret_key(env_file='.env'):
    try:
        # Read the .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Generate a new SECRET_KEY
        secret_key = secrets.token_hex(32)
        
        # Replace the SECRET_KEY line using regex
        # Matches lines starting with SECRET_KEY= (with optional whitespace)
        new_content = re.sub(
            r'^(\s*)SECRET_KEY=.*$',
            rf'\1SECRET_KEY={secret_key}',
            content,
            flags=re.MULTILINE
        )
        
        # Write back to the file
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print(f"✅ SECRET_KEY generated and saved to {env_file}")
        return 0
    except Exception as e:
        print(f"❌ Error updating SECRET_KEY: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(update_secret_key())
