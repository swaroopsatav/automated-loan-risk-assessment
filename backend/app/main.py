from fastapi import FastAPI

app = FastAPI(
    title="Automated Loan Processing & Risk Assessment",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "Loan Risk System is running"}
