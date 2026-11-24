"""Users, roles, and canonical identity mappings."""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])
