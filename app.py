import requests
import json
import re
from Token import headers

# Define the URLs

# Define the headers for API

# Function to save JSON data to a file
def save_json_to_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Processed data saved to {filename}")

# Function to process Loot.farm data
def process_loot_data(loot_data):
    processed_data = []
    for item in loot_data:
        name = item["name"]
        
        # Extract condition inside parentheses
        match = re.search(r"\((.*?)\)", name)
        condition = match.group(1) if match else ""
        
        # Remove the parentheses from the name
        clean_name = re.sub(r"\s*\(.*?\)", "", name)
        
        # Create a new dictionary with modified structure
        new_item = {
            "Name": clean_name,
            "Condition": condition,
            "Price": item["price"],
            "Have": item["have"],
            "Max": item["max"],
        }
        
        processed_data.append(new_item)
    
    return processed_data

# Function to process Swap.gg data
def process_swap_data(swap_data):
    items = swap_data.get("result", [])
    processed_data = []
    
    for item in items:
        name = item.get("n", "Unknown")  # Use "Unknown" if "n" is missing
        
        # Extract condition inside parentheses
        match = re.search(r"\((.*?)\)", name)
        condition = match.group(1) if match else ""
        
        # Remove the parentheses from the name
        clean_name = re.sub(r"\s*\(.*?\)", "", name)
        
        # Extract price
        price = item.get("p", 0)  # Default price to 0 if missing
        
        # Handle missing "s" key
        stock_info = item.get("s", {})
        have = stock_info.get("have", 0)  # Default to 0 if missing
        max_stock = stock_info.get("max", 0)  # Default to 0 if missing
        
        # Create a new dictionary with modified structure
        new_item = {
            "Name": clean_name,
            "Condition": condition,
            "Price": price,
            "Have": have,
            "Max": max_stock
        }
        
        processed_data.append(new_item)
    
    return processed_data

# Function to load JSON data from a file
def load_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to find top 10 profitable items
def find_top_10_profit(loot_data, swap_data, min_price_diff=50):
    # Create a dictionary for quick lookup of Swap.gg items by name and condition
    swap_lookup = {}
    for item in swap_data:
        key = (item["Name"], item["Condition"])  # Use "Name" and "Condition"
        swap_lookup[key] = item
    
    # List to store profitable items
    profitable_items = []
    
    # Iterate through Loot.farm items
    for loot_item in loot_data:
        key = (loot_item["Name"], loot_item["Condition"])  # Use "Name" and "Condition"
        
        # Check if the item exists in Swap.gg data
        if key in swap_lookup:
            swap_item = swap_lookup[key]
            
            # Edge case: Skip items where `have == max` or prices are zero
            if loot_item["Have"] == loot_item["Max"] or swap_item["Have"] == swap_item["Max"]:
                continue
            if loot_item["Price"] == 0 or swap_item["Price"] == 0:
                continue
            
            # Calculate the price difference
            price_diff = loot_item["Price"] - swap_item["Price"]
            
            # Check if the price difference is at least `min_price_diff`
            if abs(price_diff) >= min_price_diff:
                profit = {
                    "name": loot_item["Name"],
                    "Condition": loot_item["Condition"],
                    "loot_price": loot_item["Price"],
                    "swap_price": swap_item["Price"],
                    "profit": price_diff,
                    "loot_have": loot_item["Have"],
                    "swap_have": swap_item["Have"],
                    "loot_max": loot_item["Max"],
                    "swap_max": swap_item["Max"]
                }
                profitable_items.append(profit)
    
    # Sort the profitable items by profit in descending order
    profitable_items.sort(key=lambda x: x["profit"], reverse=True)
    
    # Return the top 10 items
    return profitable_items[:10]

# Main function to execute
def main():
    # Fetch Lootfarm data
    loot_response = requests.get(loot_url)
    if loot_response.status_code == 200:
        loot_data = loot_response.json()
        processed_loot_data = process_loot_data(loot_data)
        save_json_to_file('processed_loot_farm.json', processed_loot_data)
    else:
        print(f"Failed to fetch Loot.farm data. Status Code: {loot_response.status_code}")
        return
    
    # Fetch Swapgg data
    swap_response = requests.get(swap_url, headers=headers)
    if swap_response.status_code == 200:
        swap_data = swap_response.json()
        processed_swap_data = process_swap_data(swap_data)
        save_json_to_file('processed_swapgg.json', processed_swap_data)
    else:
        print(f"Failed to fetch Swapgg data. Status Code: {swap_response.status_code}")
        return
    
    # Load processed JSON files
    loot_data = load_json_file("processed_loot_farm.json")
    swap_data = load_json_file("processed_swapgg.json")
    
    # Find top 10 profitable items
    top_10_profit = find_top_10_profit(loot_data, swap_data)
    
    # Print the results
    print("Top 10 Profitable Items:")
    for idx, item in enumerate(top_10_profit, start=1):
        print(f"{idx}. Name: {item['name']} | Condition: {item['Condition']}")
        print(f"   Lootfarm Price: {item['loot_price']} | Swapgg Price: {item['swap_price']}")
        print(f"   Profit: {item['profit']}")
        print(f"   Lootfarm Stock: {item['loot_have']}/{item['loot_max']}")
        print(f"   Swapgg Stock: {item['swap_have']}/{item['swap_max']}")
        print()

if __name__ == "__main__":
    main()
