import httpx

BASE_URL = "http://127.0.0.1:8000"

def get_charge_id(charge_id):
    get_charge_response = httpx.get(
        f"{BASE_URL}/charges/{charge_id}",
        timeout=5.0
    )
    return get_charge_response.json()



def main():
    payload = {
        "idempotency_key": "httpx_test_1",
        "order_id": "order_123",
        "amount": 500
    }

    # First request
    response = httpx.post(
        f"{BASE_URL}/charges",
        json=payload,
        timeout=5.0
    )

    print("Status:", response.status_code)
    print("Body:", response.json())

    charge_id = response.json()["charge_id"]
    retrieved_charge = get_charge_id(charge_id)



    print("Created charge:", response.json())
    print("Retrieved charge:", retrieved_charge)

    assert retrieved_charge["charge_id"] == charge_id
    assert retrieved_charge["amount"] == 500


if __name__ == "__main__":
    main()
