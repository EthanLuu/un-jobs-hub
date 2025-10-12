"""Favorites/bookmarks routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models.user import User
from models.job import Job
from models.favorite import Favorite
from schemas.favorite import FavoriteCreate, FavoriteResponse, FavoriteUpdate
from utils.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FavoriteResponse])
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's favorites."""
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == current_user.id)
    )
    favorites = result.scalars().all()
    return [FavoriteResponse.model_validate(fav) for fav in favorites]


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a job to favorites."""
    # Check if job exists
    job_result = await db.execute(select(Job).where(Job.id == favorite_data.job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if already favorited
    existing_result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.job_id == favorite_data.job_id
        )
    )
    existing_favorite = existing_result.scalar_one_or_none()
    
    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job already in favorites"
        )
    
    # Create favorite
    new_favorite = Favorite(
        user_id=current_user.id,
        job_id=favorite_data.job_id,
        notes=favorite_data.notes
    )
    
    db.add(new_favorite)
    await db.flush()
    await db.refresh(new_favorite)
    
    return FavoriteResponse.model_validate(new_favorite)


@router.put("/{favorite_id}", response_model=FavoriteResponse)
async def update_favorite(
    favorite_id: int,
    favorite_data: FavoriteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update favorite notes or status."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == current_user.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    if favorite_data.notes is not None:
        favorite.notes = favorite_data.notes
    if favorite_data.status is not None:
        favorite.status = favorite_data.status
    
    await db.flush()
    await db.refresh(favorite)
    
    return FavoriteResponse.model_validate(favorite)


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a job from favorites."""
    result = await db.execute(
        select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == current_user.id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    await db.delete(favorite)
    await db.flush()
    
    return None



