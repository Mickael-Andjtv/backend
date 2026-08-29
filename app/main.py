from fastapi import FastAPI

app = FastAPI()

@app.get('/hello')
async def Hello():
    return "hello from back :)"