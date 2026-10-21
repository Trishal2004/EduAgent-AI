from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from uuid import UUID
from app.models.mentor import MentorInsight

class MentorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, owner_id: UUID, insights_json: dict) -> MentorInsight:
        insight = MentorInsight(
            owner_id=owner_id,
            insights_json=insights_json
        )
        self.session.add(insight)
        await self.session.commit()
        await self.session.refresh(insight)
        return insight

    async def get_latest_by_owner(self, owner_id: UUID) -> Optional[MentorInsight]:
        result = await self.session.execute(
            select(MentorInsight)
            .where(MentorInsight.owner_id == owner_id)
            .order_by(MentorInsight.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
