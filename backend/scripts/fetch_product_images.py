import json
import os
import time
import requests
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PRODUCTS_JSON_PATH = PROJECT_ROOT / "backend" / "seed_data" / "products.json"
CATALOG_DIR = PROJECT_ROOT / "public" / "catalog"

def get_pexels_api_key():
    # Try environment variable first
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        return key
    
    # Try checking .env file if it exists
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    return line.strip().split("=")[1].strip('"\'')
    
    return None

def build_search_query(product):
    name = product.get("name", "")
    colour = product.get("primary_colour", "")
    category = product.get("category", "")
    subcategory = product.get("subcategory", "")
    
    # Base query on colour and subcategory
    query_parts = []
    if colour:
        query_parts.append(colour)
    if subcategory:
        query_parts.append(subcategory.replace("_", " "))
    else:
        query_parts.append(category)
        
    query_parts.append("product photography")
    
    # For clothing, add "flat lay" or "apparel" to get better e-commerce shots
    if category in ["top", "bottom", "dress", "outerwear"]:
        query_parts.append("clothing flat lay")
        
    return " ".join(query_parts)

def fetch_image_from_pexels(api_key, query):
    headers = {
        "Authorization": api_key
    }
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "portrait"
    }
    
    try:
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("photos") and len(data["photos"]) > 0:
            photo = data["photos"][0]
            # Prefer large size for good quality without being massive
            image_url = photo["src"].get("large", photo["src"].get("original"))
            return image_url
    except Exception as e:
        print(f"  Error fetching from Pexels: {e}")
        
    return None

def download_image(url, destination_path):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"  Error downloading image: {e}")
        return False

def main():
    api_key = get_pexels_api_key()
    if not api_key:
        print("ERROR: PEXELS_API_KEY environment variable not set.")
        print("Please add it to your .env file or export it in your shell.")
        print("Example: export PEXELS_API_KEY=your_key_here")
        return

    # Ensure catalog directory exists
    os.makedirs(CATALOG_DIR, exist_ok=True)

    with open(PRODUCTS_JSON_PATH, "r") as f:
        products = json.load(f)

    updated_count = 0
    failures = []
    
    print(f"Checking {len(products)} products...")
    
    for i, product in enumerate(products):
        sku = product["sku"].lower()
        current_image = product.get("image", "")
        
        # Idempotent: only download if it's still using the .svg placeholder
        if not current_image.endswith(".svg"):
            continue
            
        print(f"[{i+1}/{len(products)}] Processing {product['name']} ({sku})...")
        
        query = build_search_query(product)
        print(f"  Query: {query}")
        
        image_url = fetch_image_from_pexels(api_key, query)
        
        if not image_url:
            print(f"  Failed to find a confident match for {sku}.")
            failures.append({
                "sku": sku,
                "name": product["name"],
                "query": query,
                "reason": "No search results or API error"
            })
            # Sleep to respect rate limits even on failure
            time.sleep(1.5)
            continue
            
        print(f"  Found image: {image_url}")
        
        # Determine file extension (pexels usually returns jpg)
        ext = ".jpg"
        if ".png" in image_url.lower():
            ext = ".png"
        
        # Build local filename, e.g., myi-top-0001.jpg
        local_filename = f"{sku}{ext}"
        local_path = CATALOG_DIR / local_filename
        
        print(f"  Downloading to {local_filename}...")
        success = download_image(image_url, local_path)
        
        if success:
            # Update product object
            new_image_path = f"/catalog/{local_filename}"
            product["image"] = new_image_path
            updated_count += 1
            print(f"  Successfully updated image to {new_image_path}")
        else:
            failures.append({
                "sku": sku,
                "name": product["name"],
                "query": query,
                "reason": "Download failed"
            })
            
        # Pexels allows 20,000 requests per month, ~200 per hour limit is common for free tier.
        # Add a sleep to prevent hitting aggressive rate limits
        time.sleep(1.5)

    # Save updated products.json
    if updated_count > 0:
        with open(PRODUCTS_JSON_PATH, "w") as f:
            json.dump(products, f, indent=2)
        print(f"\nSuccessfully updated {updated_count} products.")
    else:
        print("\nNo products were updated.")

    if failures:
        print("\n--- COULD NOT FIND A CONFIDENT MATCH FOR THESE PRODUCTS ---")
        for f in failures:
            print(f"- {f['sku']}: {f['name']} (Query used: '{f['query']}') - {f['reason']}")
        print("These products will continue to use their existing local SVG placeholders.")

if __name__ == "__main__":
    main()
