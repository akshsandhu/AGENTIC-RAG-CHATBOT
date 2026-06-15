from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Mock Account API")


# Sample account data for testing.
# Replace/extend with your real data source as needed.
ACCOUNTS = {
    "12345": {"name": "Aksh Chaudhary", "balance": 50000},
    "67890": {"name": "Test User", "balance": 12000},
    "11111": {"name": "Riya Sharma", "balance": 75500},
}


class AccountRequest(BaseModel):
    acc_no: str


@app.post("/account")
def get_account(req: AccountRequest):
    account = ACCOUNTS.get(req.acc_no)

    if account is None:
        return {"error": "Account not found"}

    return account


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
