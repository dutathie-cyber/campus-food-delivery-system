# Victoria Campus Food Delivery System

This project is a simple campus food delivery system for students and staff at Victoria Campus. It allows an attendant to:

- view the menu,
- place customer orders,
- assign riders,
- track delivery stages,
- view sales reports,
- check rider availability,
- cancel active orders,
- save data to a local JSON log.

## Files

- `campus_food_delivery_system.py` — command-line version
- `campus_food_delivery_gui.py` — lightweight Tkinter GUI version

## Run the command-line version

```powershell
cd "c:\Users\hp\Desktop\zac"
py -3 "campus_food_delivery_system.py"
```

## Run the GUI version

```powershell
cd "c:\Users\hp\Desktop\zac"
py -3 "campus_food_delivery_gui.py"
```

## Project features

- Uganda-based menu pricing in UGX
- campus delivery location charges
- free delivery for large orders over UGX 30,000
- rider assignment and queue tracking
- order status progression: Pending -> Assigned -> Out for Delivery -> Delivered
- JSON persistence for orders and last order ID
- sales summary report

## Output data

The app stores order data in:

- `victoria_campus_delivery_log.json`

This keeps order history between program runs.
