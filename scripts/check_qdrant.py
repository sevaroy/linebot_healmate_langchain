import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from pathlib import Path

# --- Enhanced Debugging --- #
# Construct the path to the .env file in the project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

print(f"DEBUG: Script running from: {Path(__file__).resolve()}")
print(f"DEBUG: Project root detected as: {project_root.resolve()}")
print(f"DEBUG: Checking for .env file at: {env_path.resolve()}")

if env_path.exists():
    print("DEBUG: .env file found!")
    # Load the .env file explicitly
    load_dotenv(dotenv_path=env_path)
else:
    print("ERROR: .env file NOT FOUND at the expected location.")

# --- Qdrant Connection Logic --- #

# Initialize Qdrant client
try:
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    print(f"DEBUG: Value of QDRANT_URL from environment: {qdrant_url}")

    if not qdrant_url:
        print("\n--- RESULT ---")
        print("Error: QDRANT_URL is not set or loaded correctly from the .env file.")
    else:
        print(f"\n--- RESULT ---")
        print(f"Connecting to Qdrant at: {qdrant_url}")
        qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
        )

        # Get the list of collections
        collections = qdrant_client.get_collections()

        print("\nAvailable collections:")
        if collections.collections:
            for collection in collections.collections:
                print(f"- {collection.name}")
        else:
            print("No collections found on this Qdrant instance.")

except Exception as e:
    print(f"\nAn error occurred: {e}")
    print("Please double-check your QDRANT_URL and QDRANT_API_KEY in the .env file.")
