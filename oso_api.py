import uvicorn

from fastapi import FastAPI
from fastapi import HTTPException

from fastapi_mcp import FastApiMCP

from pydantic import BaseModel

from oso_cloud import Oso
from oso_cloud import Value


class AuthorizationRequest(BaseModel):
    actor: str 
    action: str
    resource: str 


class AuthorizationResponse(BaseModel):
    authorized: bool
    message: str


app = FastAPI(title="Oso Authorization API")


@app.post("/authorize", response_model=AuthorizationResponse)
async def authorize(request: AuthorizationRequest):
    """
    Check if an actor is authorized to perform an action on a resource.
    """

    actor_split = request.user.split(":")
    
    try:
        actor = Value(actor_split[0], actor_split[1])
    except IndexError:
        raise HTTPException(status_code=400,
                            detail="Actor string incorrectly formatted - use"
                                   " format 'User:alice'")

    resource_split = request.resource.split(":")
    
    try:
        resource = Value(resource_split[0], resource_split[1])
    except IndexError:
        raise HTTPException(status_code=400,
                            detail="Resource string incorrectly formatted - use"
                                   " format 'Item:foo'")

    try:
        authorized = oso.authorize(actor, request.action, resource)
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=e)

    if authorized:
        return authorizationresponse(authorized=True,
                                     message=f"{request.actor} is authorized "
                                             "to {request.action} "
                                             "{request.resource")
    else:
        return authorizationresponse(authorized=False,
                                     message=f"{request.actor} is not "
                                             "authorized "
                                             "to {request.action} "
                                             "{request.resource")


mcp = FastApiMCP(app)
mcp.mount()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
