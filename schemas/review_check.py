from pydantic import BaseModel


class ReviewCheckRequest(BaseModel):
    requestId: str
    blogUrl: str