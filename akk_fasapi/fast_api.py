import uvicorn
from fastapi import FastAPI, HTTPException, Header
import httpx

app = FastAPI(title="FastApi django client example",
              description="fastapi thats consume the api of django",
              version="1.0.0")

DJANGO_API_BASE_URL = 'https://127.0.0.1:8000/api/'

@app.get("/")
async def read_root():
    return {'message': 'Welcome to the fastapi client for django api tasks'}

@app.get("/tasks")
async def get_tasks(
    authorization: str = Header(None, description="Token of authentication (e.g., 'Token My_token')")
):
    headers = {'Authorization': authorization} if authorization else {}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{DJANGO_API_BASE_URL}tasks/", headers=headers)
            response.raise_for_status()

            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500, detail=f"Error de red al conectar con django api: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error of the django api: {exc.response.json().get('detail', 'Error unnknown')}"
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Ocurrio un error inesperado: {exc}"
            )
        

@app.get("/labels/")
async def get_labels(
    authorization: str = Header(None, description="Token of authorization of django")
):
    headers = {'Authorization': authorization} if authorization else {}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{DJANGO_API_BASE_URL}labels/", headers=headers)
            response.raise_for_status()

            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=500, detail=f"Error de red al conectar con django api: {exc}"
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error of the django api: {exc.response.json().get('detail', 'Error unnknown')}"
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Ocurrio un error inesperado: {exc}"
            ) 
        
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1",
                port=8001, reload=True)