import threading
import time
import random

"""
Pizza Shop Simulation!
=====================

Imagine you're running a pizza shop. If you had only one worker (single-thread),
they would have to:
1. Take orders
2. Make pizzas
3. Deliver pizzas
...all by themselves, one at a time!

But with multiple workers (multi-threading), you can have:
- One person taking orders
- Another making pizzas
- Another delivering pizzas
All at the same time!

Let's simulate this:
"""

# This will keep track of our pizzas
class PizzaShop:
    def __init__(self):
        self.orders = []
        self.pizzas_to_deliver = []
        
        # This is like a lock on the kitchen door - only one person can go in at a time
        self.kitchen_lock = threading.Lock()
        
        print("🏪 Pizza shop is open!")

    def take_order(self, order_num):
        """One worker taking orders"""
        time.sleep(random.randint(1, 3))  # Taking order takes 1-3 seconds
        self.orders.append(order_num)
        print(f"📝 Took order #{order_num}")

    def make_pizza(self, order_num):
        """Another worker making pizzas"""
        # Only one person can use the kitchen at a time
        with self.kitchen_lock:
            print(f"👨‍🍳 Making pizza for order #{order_num}")
            time.sleep(random.randint(2, 4))  # Making pizza takes 2-4 seconds
            self.pizzas_to_deliver.append(order_num)
            print(f"✨ Finished making pizza for order #{order_num}")

    def deliver_pizza(self, order_num):
        """Another worker delivering pizzas"""
        time.sleep(random.randint(1, 3))  # Delivery takes 1-3 seconds
        print(f"🛵 Delivered pizza for order #{order_num}")

def process_order(shop, order_num):
    """Handle the complete order process"""
    # Take the order
    shop.take_order(order_num)
    
    # Make the pizza
    shop.make_pizza(order_num)
    
    # Deliver the pizza
    shop.deliver_pizza(order_num)

def main():
    # Open our pizza shop
    shop = PizzaShop()
    
    # Create threads for multiple orders (like having multiple customers)
    threads = []
    for order_num in range(1, 6):  # Handle 5 orders
        # Each thread is like assigning a new worker to handle an order
        thread = threading.Thread(
            target=process_order, 
            args=(shop, order_num)
        )
        threads.append(thread)
        thread.start()
        print(f"👤 Customer #{order_num} entered the shop")
    
    # Wait for all orders to be completed
    for thread in threads:
        thread.join()
    
    print("🎉 All orders completed! Time to close the shop!")

if __name__ == "__main__":
    main()
