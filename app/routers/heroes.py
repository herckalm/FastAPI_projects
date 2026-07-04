from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_admin, get_current_user
from app.models import Hero, HeroCreate, HeroUpdate, Mission

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.post("", response_model=Hero, status_code=status.HTTP_201_CREATED)
def create_hero(
    hero: HeroCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    db_hero = Hero.model_validate(hero)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.get("", response_model=List[Hero])
def read_heroes(session: Session = Depends(get_session)):
    return session.exec(select(Hero)).all()


@router.get("/{hero_id}", response_model=Hero)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.patch("/{hero_id}", response_model=Hero)
def update_hero(
    hero_id: int,
    hero_patch: HeroUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero_patch.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)

    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(
    hero_id: int,
    session: Session = Depends(get_session),
    admin_user: str = Depends(get_current_admin),
):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    # Επιχειρηματικός κανόνας: Όχι διαγραφή αν έχει ενεργές (μη ολοκληρωμένες) αποστολές
    statement = select(Mission).where(
        Mission.hero_id == hero_id, Mission.completed == False
    )
    active_missions = session.exec(statement).all()
    if active_missions:
        raise HTTPException(
            status_code=400, detail="Cannot delete a hero with active missions"
        )

    session.delete(hero)
    session.commit()
    return None
