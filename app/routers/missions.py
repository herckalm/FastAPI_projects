from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.dependencies import get_current_admin, get_current_user
from app.models import Hero, Mission, MissionCreate, MissionUpdate

router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("", response_model=Mission, status_code=status.HTTP_201_CREATED)
def create_mission(
    mission: MissionCreate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    hero = session.get(Hero, mission.hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    db_mission = Mission.model_validate(mission)
    session.add(db_mission)
    session.commit()
    session.refresh(db_mission)
    return db_mission


@router.get("", response_model=List[Mission])
def read_missions(session: Session = Depends(get_session)):
    return session.exec(select(Mission)).all()


@router.get("/{mission_id}", response_model=Mission)
def read_mission(mission_id: int, session: Session = Depends(get_session)):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@router.patch("/{mission_id}", response_model=Mission)
def update_mission(
    mission_id: int,
    mission_patch: MissionUpdate,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    db_mission = session.get(Mission, mission_id)
    if not db_mission:
        raise HTTPException(status_code=404, detail="Mission not found")

    if mission_patch.hero_id is not None:
        hero = session.get(Hero, mission_patch.hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")

    mission_data = mission_patch.model_dump(exclude_unset=True)
    for key, value in mission_data.items():
        setattr(db_mission, key, value)

    session.add(db_mission)
    session.commit()
    session.refresh(db_mission)
    return db_mission


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(
    mission_id: int,
    session: Session = Depends(get_session),
    admin_user: str = Depends(get_current_admin),
):
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    session.delete(mission)
    session.commit()
    return None
