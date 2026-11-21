"""
Version 1 — The core engine
Start here

Target: 60-90 minutes

Build a Python program that processes simulated charges and handles duplicate requests correctly.

No web server. No database. No LLM. Just Python dictionaries, functions, and tests.

Your program needs to:
- Process a request using an idempotency key.
- Avoid processing the same request twice.
- Detect when the same key is reused with different data.
- Simulate a response disappearing after a successful operation.
- Correctly recover when the client retries.
Finished when:

You can demonstrate that a client experiences a timeout, retries, and the server still records only one charge.
"""

# request comes in, check if the idempotency key already exists, if not log transcction, if it does exist, see if the 
# data is the same, if so return stored data, else throw an exception. 

import uuid
from db import insert_charge, get_charge 


# simulates the server, taking in an order doing work 
def process_charge(idempotency_key, order_id, amount):

    # 1 - check for existing charge 
    existing_charge = get_charge(idempotency_key)

    # 2 - if existing, then validate it, return if all good, else return error
    if existing_charge is not None:
        if existing_charge["order_id"] == order_id and existing_charge["amount"] == amount:
            return existing_charge
        else:
            raise ValueError("Idempotency key reused with different data")

    # 3 - charge not existing, create it
    charge_id = str(uuid.uuid4())
    insert_charge(idempotency_key, charge_id, order_id, amount, "success")

    return get_charge(idempotency_key)


# using this to simulate network failure. Simulate calling the function. 
def send_request(idempotency_key, order_id, amount, lose_response=False):
    result = process_charge(idempotency_key, order_id, amount)

    if lose_response:
        raise TimeoutError("Response lost after charge succeeded")
    
    return result



#this is where we actually run the functions, acts like the client calling servers and shit
if __name__ == "__main__":
    try:
        send_request("abc", "order_123", 500, lose_response=True)
    except TimeoutError:
        print("Timeout occurred. Retrying...")

        result = send_request(
            "abc", "order_123", 500, lose_response=False
        ) 

        print("Retry result:", result)
    
    print("Transaction log:", transaction_log)
