from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from main import process_charge
from db import initialize_database, get_charge_by_id, get_request_attempts


# this is the server, handles incoming HTTP requests, parsing them, sending responses 
app = FastAPI()


initialize_database()


# pydantic model, schema/structure of data that clients are allowed to send. FastAPI uses this model to validate incoming data
# If validation fails, FastAPI returns 422 error
class ChargeRequest(BaseModel):
    idempotency_key: str
    order_id: str
    amount: int = Field(gt=0)


# decorator - when someone sendes POST request to /charges, run function below
@app.post("/charges")
def create_charge(request: ChargeRequest):
    try:
        return process_charge(
                request.idempotency_key, 
                request.order_id, 
                request.amount
            )
    except ValueError as e: # getting the valueError exception from process_charge, and storing it as e
        raise HTTPException( # valueError is python exception not HTTP exception, so just translate it to HTTP so we can send something back. 
            status_code=409, # 409 = conflict with existing state 
            detail=str(e)
        )

# looking up by its chargeID not idempotency key 
@app.get("/charges/{charge_id}")
def read_charge(charge_id: str):

    charge = get_charge_by_id(charge_id)

    if charge is None:
        raise HTTPException(
            status_code=404,
            detail="Charge not found"
        )

    return charge



# Return the request ID, attempt count, success count, and most recent outcome
@app.get("/requests/{order_id}/summary")
def get_request_summmary(order_id: str):
    try:
        summary = {
        "order_id" : order_id,
        "attempt_count" : 0,
        "success_count" : 0,
        "most_recent_outcome" : None

        }
        all_reqs = get_request_attempts(order_id) # gets us all the request attempts for that order_id
        most_recent_outcome = all_reqs[0]["created_at"]

        for req in all_reqs:

            summary["attempt_count"] += 1
            if req["outcome"] == "success":
                summary["success_count"] += 1


            # FINISH THIS UP, LAST CREATED TIMESTAMP
            if req["created_at"] < most_recent_outcome:
                summary["most_recent_outcome"] = req

        return summary
    except ValueError as e: # error from get_request_attempts if order_id not existent
        raise HTTPException(
            status_code=404,
            detail="Order_id not found"
        )

        


