
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

orders = []
next_order_id = 1

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Order Management - V1</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            background: #f2f4f7;
            padding: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
        }
        input, button {
            padding: 10px;
            margin: 8px 0;
        }
        button {
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Order Management System</h1>
        <h2>Version 1 — Place Order</h2>

        <form method="POST" action="/orders">
            <label>Item name</label><br>
            <input name="item" required maxlength="100"
                   placeholder="Enter item name"><br>

            <label>Quantity</label><br>
            <input name="quantity" type="number"
                   min="1" max="10000" value="1" required><br>

            <button type="submit">Place Order</button>
        </form>

        {% if message %}
            <p>{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.get("/")
def home():
    return render_template_string(HTML, message="")


@app.post("/orders")
def place_order():
    global next_order_id

    item = request.form.get("item", "").strip()
    quantity = request.form.get("quantity", type=int)

    if not item or quantity is None or not 1 <= quantity <= 10000:
        return "Invalid item or quantity", 400

    orders.append({
        "id": next_order_id,
        "item": item,
        "quantity": quantity
    })

    next_order_id += 1

    return render_template_string(
        HTML,
        message="Order placed successfully!"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
