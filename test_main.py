from main import process_charge, send_request, transaction_log

def test_lost_response():
    # Start with an empty transaction log
    transaction_log.clear()

    # First request: charge succeeds, response gets lost
    try:
        send_request("abc", "order_123", 500, lose_response=True)
    except TimeoutError:
        pass

    # The server should have recorded one charge
    assert len(transaction_log) == 1

    original_charge_id = transaction_log["abc"]["charge_id"]

    # Retry the exact same request
    result = send_request("abc", "order_123", 500)

    # Verify the retry returns the original charge
    assert result["charge_id"] == original_charge_id

    # Verify no duplicate charge was created
    assert len(transaction_log) == 1

    print("Lost response test passed!")


def test_conflicting_request():
    transaction_log.clear()

    original_request = send_request("abc", "order_123", 500)

    error_occurred = False

    try:
        send_request("abc", "order_1234", 600)
    except ValueError:
        error_occurred = True

    # Verify the conflicting request was rejected
    assert error_occurred

    # Verify no duplicate charge was created
    assert len(transaction_log) == 1

    # Verify the original charge wasn't modified
    assert transaction_log["abc"] == original_request

    print("Conflicting request test passed!")


if __name__ == "__main__":
    test_lost_response()
    test_conflicting_request()