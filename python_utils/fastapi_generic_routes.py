from fastapi import FastAPI, Request, Response


def load_routes(fastapi_app: FastAPI, application_name: str, version: str) -> None:
    @fastapi_app.get("/", include_in_schema=False)
    async def root(request: Request):  # pyright: ignore[reportUnusedFunction]
        ip = None
        if request.client:
            ip = request.client.host
        return {
            "application_name": application_name,
            "version": version,
            "client_ip": ip,
        }

    @fastapi_app.get("/health", include_in_schema=False)
    async def health(response: Response):  # pyright: ignore[reportUnusedFunction]
        response.headers["X-App-Alive"] = "True"
        return {"message": "It's alive!"}

    @fastapi_app.get("/force_exception", include_in_schema=False)
    async def force_error():  # pyright: ignore[reportUnusedFunction]
        raise Exception("This always fails")
