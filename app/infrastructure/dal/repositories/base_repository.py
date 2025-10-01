from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    @property
    def db(self) -> AsyncSession:
        return self._db

    def transaction(self):
        class TransactionContext:
            def __init__(self, db: AsyncSession):
                self.db = db

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    await self.db.rollback()
                else:
                    await self.db.commit()

        return TransactionContext(self._db)
