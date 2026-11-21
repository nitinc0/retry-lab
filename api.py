from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from main import process_charge
from db import initialize_database, get_charge_by_id


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
