import uvicorn

if __name__ == '__main__':
    uvicorn.run('fastapi_user_signups.api:app', host="0.0.0.0", reload=True)
