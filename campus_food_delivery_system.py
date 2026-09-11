import json
import os
import time

# ==========================================
# a) Menu Setup (Ugandan Campus Menu in UGX)
# ==========================================
menu = {
    "Main Meals": {
        "Matooke & Groundnut Sauce": 8000,
        "Posho & Beans": 5000,
        "Rice & Beef Stew": 10000,
        "Cassava & Fish": 12000,
        "Rolex (Chapati & Eggs)": 3000,
        "Kikomando (Chapati & Beans)": 3500,
        "Chicken Luwombo": 15000,
        "Sweet Potatoes & Dodo": 6000,
        "Beef Pilau": 8000,
        "Goat Meat Stew": 12000,
    },
    "Drinks": {
        "Mukyalo (Millet Drink)": 2000,
        "Bushera (Sorghum Drink)": 1500,
        "Mubisi (Fresh Juice)": 2500,
        "Kasese (Local Brew)": 3000,
        "Fresh Milk (Cow)": 1500,
        "Soda (300ml)": 1500,
        "Bottled Water (500ml)": 1000,
        "Tea (Chai)": 1000,
        "Coffee": 1500,
        "Packaged Juice (300ml)": 2500,
    },
    "Snacks": {
        "Mandazi (2 pieces)": 1000,
        "Chapati (Plain)": 1000,
        "Roasted Maize": 1000,
        "Gonja (Roasted Banana)": 1500,
        "Samosa": 1000,
        "Groundnuts (Roasted)": 1000,
        "Cassava Chips": 1500,
        "Rolex (Small)": 2000,
    },
}

# ==========================================
# Predefined Campus Delivery Locations
# ==========================================
campus_locations = {
    "1": {"name": "Victoria Campus - Main Gate", "fee": 2000},
    "2": {"name": "Victoria Campus - Administration Block", "fee": 2500},
    "3": {"name": "Victoria Campus - Library", "fee": 2500},
    "4": {"name": "Faculty of Science and Technology - Block A", "fee": 3000},
    "5": {"name": "Faculty of Science and Technology - Block B", "fee": 3000},
    "6": {"name": "Faculty of Science and Technology - Computer Lab", "fee": 3500},
    "7": {"name": "Faculty of Science and Technology - Engineering Workshop", "fee": 4000},
    "8": {"name": "Victoria Campus - Hostels (Male)", "fee": 2500},
    "9": {"name": "Victoria Campus - Hostels (Female)", "fee": 2500},
}

DEFAULT_RIDER_LIST = ["Ahmed", "Sarah", "John", "Maya", "David", "Grace"]
available_rider_list = DEFAULT_RIDER_LIST.copy()
busy_rider_list = []

# Global data stores
all_orders = []
order_counter = 1000
sales_log_file = "victoria_campus_delivery_log.json"

# ==========================================
# e) File Persistence (Load & Save)
# ==========================================
def refresh_rider_queues():
    """Resync rider availability from the saved order log."""
    global available_rider_list, busy_rider_list

    assigned_riders = {
        order.get("rider")
        for order in all_orders
        if order.get("rider") and order.get("status") != "Delivered"
    }

    busy_rider_list = [rider for rider in DEFAULT_RIDER_LIST if rider in assigned_riders]
    available_rider_list = [rider for rider in DEFAULT_RIDER_LIST if rider not in assigned_riders]


def load_sales_log():
    """Reloads the log automatically when the program starts."""
    global all_orders, order_counter

    if os.path.exists(sales_log_file):
        try:
            with open(sales_log_file, "r") as file:
                data = json.load(file)
                all_orders = data.get("orders", [])
                order_counter = int(data.get("last_order_id", 1000))
            print(f"System loaded: {len(all_orders)} past orders found in log.")
        except json.JSONDecodeError:
            print("Log file is corrupted. Starting with a fresh log.")
            all_orders = []
            order_counter = 1000
        except Exception as e:
            print(f"Error loading file: {e}")
            all_orders = []
            order_counter = 1000
    else:
        print("No previous log file found. Starting fresh.")

    refresh_rider_queues()


def save_sales_log():
    """Saves every completed order to a log file."""
    data = {"last_order_id": order_counter, "orders": all_orders}
    try:
        with open(sales_log_file, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print(f"Error saving the log file: {e}")


# ==========================================
# Helper Functions
# ==========================================
def display_menu():
    print("\n--- VICTORIA CAMPUS DELIVERY MENU (UGX) ---")
    for category, items in menu.items():
        print(f"\n[{category}]")
        for item, price in items.items():
            print(f"  - {item}: UGX {price:,}")
    print("---------------------------------------------")


def display_locations():
    print("\n--- SELECT DELIVERY LOCATION ---")
    for key, loc in campus_locations.items():
        print(f"  {key}. {loc['name']} (Fee: UGX {loc['fee']:,})")
    print("--------------------------------")


def view_rider_status():
    print("\n--- RIDER STATUS ---")
    print(f"Available riders: {available_rider_list if available_rider_list else 'None'}")
    print(f"Busy riders: {busy_rider_list if busy_rider_list else 'None'}")

    active_orders = [order for order in all_orders if order.get("status") != "Delivered"]
    if not active_orders:
        print("No active orders at the moment.")
        return

    print("\nActive Orders:")
    for order in active_orders:
        rider = order.get("rider") or "Unassigned"
        print(
            f"  - Order #{order['order_id']}: {order['status']} | "
            f"Rider: {rider} | Destination: {order['location']}"
        )


def cancel_order():
    if not all_orders:
        print("\nNo orders available to cancel.")
        return

    active_orders = [order for order in all_orders if order.get("status") != "Delivered"]
    if not active_orders:
        print("\nNo active orders available to cancel.")
        return

    print("\n--- CANCEL ORDER ---")
    for order in active_orders:
        print(
            f"  {order['order_id']}. {order['location']} | "
            f"{order.get('status', 'Pending')} | Rider: {order.get('rider') or 'Unassigned'}"
        )

    try:
        order_id = int(input("Enter order ID to cancel (or 0 to return): ").strip())
    except ValueError:
        print("Invalid order ID.")
        return

    if order_id == 0:
        return

    for index, order in enumerate(all_orders):
        if order.get("order_id") == order_id:
            if order.get("status") == "Delivered":
                print("Delivered orders cannot be cancelled.")
                return

            rider = order.get("rider")
            if rider:
                if rider in busy_rider_list:
                    busy_rider_list.remove(rider)
                if rider not in available_rider_list:
                    available_rider_list.append(rider)

            del all_orders[index]
            save_sales_log()
            print(f"Order #{order_id} has been cancelled successfully.")
            return

    print(f"Order #{order_id} was not found.")


def find_menu_item(item_name):
    """Find a menu item using case-insensitive matching."""
    search_term = item_name.strip().lower()
    for items in menu.values():
        for menu_item in items:
            if menu_item.lower() == search_term:
                return menu_item
    return None


def choose_location():
    while True:
        display_locations()
        loc_choice = input("Select your campus location (1-9): ").strip()
        if loc_choice in campus_locations:
            location_data = campus_locations[loc_choice]
            return location_data["name"], location_data["fee"]
        print("Invalid location. Please select a number from 1 to 9.")


# ==========================================
# b) Order Taking (Campus Delivery Mode)
# ==========================================
def take_order():
    current_order = {}

    display_menu()
    print("\n--- NEW CUSTOMER ORDER ---")

    while True:
        try:
            item_name = input("\nEnter item name (or type 'done' to finish order): ").strip()
        except EOFError:
            print("\nInput closed. Order cancelled.")
            return None

        if item_name.lower() == "done":
            break

        actual_item_name = find_menu_item(item_name)
        if not actual_item_name:
            print("Item not found on menu. Please check spelling.")
            continue

        try:
            quantity = int(input(f"Enter quantity for '{actual_item_name}': "))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        if quantity <= 0:
            print("Quantity must be at least 1.")
            continue

        current_order[actual_item_name] = current_order.get(actual_item_name, 0) + quantity
        print(f"Added {quantity}x {actual_item_name} to the ticket.")

    if not current_order:
        print("\nOrder cancelled (empty ticket).")
        return None

    subtotal = 0
    print("\n--- CUSTOMER RECEIPT ---")
    for item, qty in current_order.items():
        for items in menu.values():
            if item in items:
                price = items[item]
                item_total = price * qty
                subtotal += item_total
                print(f"{qty}x {item} @ UGX {price:,} = UGX {item_total:,}")
                break

    print(f"\nSubtotal: UGX {subtotal:,}")

    location_name, base_delivery_fee = choose_location()

    if subtotal >= 30000:
        delivery_fee = 0
        print(f"\nDelivery Fee: FREE (Order over UGX 30,000)")
    else:
        delivery_fee = base_delivery_fee
        print(f"\nDelivery Fee to {location_name}: UGX {delivery_fee:,}")

    total = subtotal + delivery_fee
    print(f"TOTAL TO PAY: UGX {total:,}")

    global order_counter
    order_counter += 1
    order_id = order_counter

    order_record = {
        "order_id": order_id,
        "items": current_order,
        "subtotal": subtotal,
        "location": location_name,
        "delivery_fee": delivery_fee,
        "total": total,
        "status": "Pending",
        "rider": None,
    }

    print(f"\n[System] Order #{order_id} generated successfully for {location_name}.")
    return order_record


# ==========================================
# c) Rider Assignment and Status Tracking
# ==========================================
def assign_rider(order):
    if not available_rider_list:
        print("\n[System] No riders available. Order remains pending.")
        return order

    rider = available_rider_list.pop(0)
    busy_rider_list.append(rider)
    order["rider"] = rider
    order["status"] = "Assigned to Rider"
    print(f"\n[System] Boda-Boda Rider '{rider}' assigned to Order #{order['order_id']}.")
    return order


def release_rider(order):
    rider = order.get("rider")
    if not rider:
        return

    if rider in busy_rider_list:
        busy_rider_list.remove(rider)
    if rider not in available_rider_list:
        available_rider_list.append(rider)

    print(f"[System] Rider '{rider}' is now back in the queue.")


def update_status(order):
    stages = ["Pending", "Assigned to Rider", "Out for Delivery", "Delivered"]
    start_status = order.get("status", "Pending")
    try:
        current_stage_index = stages.index(start_status)
    except ValueError:
        current_stage_index = 0

    print(f"\n--- TRACKING ORDER #{order['order_id']} ---")
    print(f"Destination: {order['location']}")

    while current_stage_index < len(stages) - 1:
        next_stage = stages[current_stage_index + 1]
        try:
            prompt = input(f"Update status to '{next_stage}'? (y/n): ").strip().lower()
        except EOFError:
            print("\nStatus update cancelled.")
            return

        if prompt not in {"y", "n"}:
            print("Please answer y or n.")
            continue

        if prompt == "n":
            print("Status update paused.")
            return

        order["status"] = next_stage
        current_stage_index += 1
        print(f"[System] Status updated: {order['status']}")
        time.sleep(0.5)

        if order["status"] == "Delivered":
            print("Order complete! Delivered to customer.")
            release_rider(order)
            return


# ==========================================
# d) Sales and Reporting
# ==========================================
def generate_report():
    """Computes and displays total revenue, best-selling item, and status counts."""
    if not all_orders:
        print("\nNo orders have been placed yet. No report available.")
        return

    total_revenue = 0
    item_counts = {}
    status_counts = {
        "Pending": 0,
        "Assigned to Rider": 0,
        "Out for Delivery": 0,
        "Delivered": 0,
    }

    for order in all_orders:
        total_revenue += order.get("total", 0)

        for item, qty in order.get("items", {}).items():
            item_counts[item] = item_counts.get(item, 0) + qty

        status = order.get("status", "Pending")
        status_counts[status] = status_counts.get(status, 0) + 1

    best_seller = None
    max_qty = 0
    for item, qty in item_counts.items():
        if qty > max_qty:
            max_qty = qty
            best_seller = item

    print("\n========== VICTORIA CAMPUS SALES REPORT ==========")
    print(f"Total Orders Processed: {len(all_orders)}")
    print(f"Total Revenue (incl. delivery): UGX {total_revenue:,}")
    print(f"Best-Selling Item: {best_seller if best_seller else 'N/A'} ({max_qty} sold)")
    print("\nOrders by Status:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")
    print("==================================================")


# ==========================================
# f) Menu-Driven Driver Programme (Attendant UI)
# ==========================================
def main():
    load_sales_log()

    while True:
        print("\n=== VICTORIA CAMPUS FOOD DELIVERY SYSTEM ===")
        print("1. View Menu")
        print("2. Take New Order")
        print("3. View Sales Report")
        print("4. View Rider Status")
        print("5. Cancel Order")
        print("6. Save Data & Exit")

        try:
            choice = input("Select an option (1-6): ").strip()
        except EOFError:
            print("\nInput closed. Saving data and exiting.")
            save_sales_log()
            break

        if choice == "1":
            display_menu()
        elif choice == "2":
            new_order = take_order()
            if new_order:
                new_order = assign_rider(new_order)
                all_orders.append(new_order)
                update_status(new_order)
                save_sales_log()
        elif choice == "3":
            generate_report()
        elif choice == "4":
            view_rider_status()
        elif choice == "5":
            cancel_order()
        elif choice == "6":
            save_sales_log()
            print("Data saved successfully. System shutting down. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.")


if __name__ == "__main__":
    main()
