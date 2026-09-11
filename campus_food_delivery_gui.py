import json
import os
import tkinter as tk
from tkinter import messagebox

MENU = {
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

CAMPUS_LOCATIONS = {
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

RIDERS = ["Ahmed", "Sarah", "John", "Maya", "David", "Grace"]
LOG_FILE = "victoria_campus_delivery_log.json"


def load_orders():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as file:
                data = json.load(file)
                return data.get("orders", []), int(data.get("last_order_id", 1000))
        except (json.JSONDecodeError, ValueError):
            return [], 1000
    return [], 1000


def save_orders(orders, last_order_id):
    data = {"last_order_id": last_order_id, "orders": orders}
    with open(LOG_FILE, "w") as file:
        json.dump(data, file, indent=4)


class DeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Victoria Campus Food Delivery")
        self.root.geometry("900x700")
        self.root.configure(bg="#f4f4f4")

        self.orders, self.last_order_id = load_orders()
        self.available_riders = RIDERS.copy()
        self.busy_riders = []

        self._sync_riders()

        self.menu_text = tk.Text(root, height=18, width=80, wrap="word")
        self.menu_text.insert(tk.END, self._format_menu())
        self.menu_text.config(state="disabled")

        tk.Label(root, text="Item Name:", bg="#f4f4f4", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        self.item_entry = tk.Entry(root, width=50)
        self.item_entry.pack()

        tk.Label(root, text="Quantity:", bg="#f4f4f4", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        self.qty_entry = tk.Entry(root, width=20)
        self.qty_entry.pack()

        tk.Label(root, text="Location Number (1-9):", bg="#f4f4f4", font=("Arial", 11, "bold")).pack(pady=(10, 0))
        self.location_entry = tk.Entry(root, width=20)
        self.location_entry.pack()

        tk.Button(root, text="Place Order", command=self.place_order, width=20, bg="#2e7d32", fg="white").pack(pady=10)
        tk.Button(root, text="View Report", command=self.show_report, width=20, bg="#1565c0", fg="white").pack(pady=5)
        tk.Button(root, text="View Rider Status", command=self.show_rider_status, width=20, bg="#ef6c00", fg="white").pack(pady=5)

        self.output = tk.Text(root, height=18, width=95)
        self.output.pack(pady=10)
        self.output.insert(tk.END, "System ready.\n")

    def _sync_riders(self):
        assigned = {order.get("rider") for order in self.orders if order.get("rider") and order.get("status") != "Delivered"}
        self.busy_riders = [rider for rider in RIDERS if rider in assigned]
        self.available_riders = [rider for rider in RIDERS if rider not in assigned]

    def _format_menu(self):
        lines = ["--- VICTORIA CAMPUS DELIVERY MENU (UGX) ---\n"]
        for category, items in MENU.items():
            lines.append(f"[{category}]\n")
            for item, price in items.items():
                lines.append(f"- {item}: UGX {price:,}\n")
        return "".join(lines)

    def _find_item(self, item_name):
        item_name = item_name.strip().lower()
        for items in MENU.values():
            for item in items:
                if item.lower() == item_name:
                    return item
        return None

    def place_order(self):
        item_name = self.item_entry.get().strip()
        try:
            qty = int(self.qty_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a valid number.")
            return

        if qty <= 0:
            messagebox.showerror("Error", "Quantity must be at least 1.")
            return

        item = self._find_item(item_name)
        if not item:
            messagebox.showerror("Error", "Item not found on the menu.")
            return

        location_key = self.location_entry.get().strip()
        if location_key not in CAMPUS_LOCATIONS:
            messagebox.showerror("Error", "Location must be a number from 1 to 9.")
            return

        location = CAMPUS_LOCATIONS[location_key]
        price = MENU[next(cat for cat, items in MENU.items() if item in items)][item]
        subtotal = price * qty
        delivery_fee = 0 if subtotal >= 30000 else location["fee"]
        total = subtotal + delivery_fee

        self.last_order_id += 1
        order_id = self.last_order_id

        order = {
            "order_id": order_id,
            "items": {item: qty},
            "subtotal": subtotal,
            "location": location["name"],
            "delivery_fee": delivery_fee,
            "total": total,
            "status": "Pending",
            "rider": None,
        }

        if self.available_riders:
            rider = self.available_riders.pop(0)
            self.busy_riders.append(rider)
            order["rider"] = rider
            order["status"] = "Assigned to Rider"
        else:
            messagebox.showwarning("Notice", "No rider available; order remains pending.")

        self.orders.append(order)
        save_orders(self.orders, self.last_order_id)

        self.output.insert(
            tk.END,
            f"\nOrder #{order_id} placed for {location['name']} | Total: UGX {total:,}\n"
            f"Assigned rider: {order['rider'] or 'None'} | Status: {order['status']}\n"
        )
        self.output.see(tk.END)
        self.item_entry.delete(0, tk.END)
        self.qty_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)

    def show_report(self):
        if not self.orders:
            messagebox.showinfo("Report", "No orders have been placed yet.")
            return

        total_revenue = sum(order.get("total", 0) for order in self.orders)
        item_counts = {}
        for order in self.orders:
            for item, qty in order.get("items", {}).items():
                item_counts[item] = item_counts.get(item, 0) + qty

        best_item = max(item_counts.items(), key=lambda x: x[1], default=("N/A", 0))
        report = [
            "\n========== VICTORIA CAMPUS SALES REPORT ==========",
            f"Total Orders Processed: {len(self.orders)}",
            f"Total Revenue: UGX {total_revenue:,}",
            f"Best-Selling Item: {best_item[0]} ({best_item[1]} sold)",
            "\nOrders by Status:",
        ]

        status_counts = {"Pending": 0, "Assigned to Rider": 0, "Out for Delivery": 0, "Delivered": 0}
        for order in self.orders:
            status = order.get("status", "Pending")
            status_counts[status] = status_counts.get(status, 0) + 1

        for key, value in status_counts.items():
            report.append(f"- {key}: {value}")

        report.append("==================================================")
        self.output.insert(tk.END, "\n" + "\n".join(report) + "\n")
        self.output.see(tk.END)

    def show_rider_status(self):
        self.output.insert(
            tk.END,
            f"\nAvailable riders: {self.available_riders}\nBusy riders: {self.busy_riders}\n"
        )
        self.output.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()
