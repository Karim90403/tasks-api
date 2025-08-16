import contextlib

from redis.asyncio import Redis

from db.base.abc_session_manager import BaseSessionManager


class RedisSessionManager(BaseSessionManager):
    def __init__(self) -> None:
        self._sessionmaker = None

    def init(self, host: str, port: int) -> None:
        """
        Init sessionmaker of redis database
        Args:
            host: redis host
            port: redis port

        Returns:
            None
        """
        self._sessionmaker = self._redis_sessionmaker(host, port)

    @staticmethod
    def _redis_sessionmaker(host: str, port: int):
        """
        Init redis session
        Args:
            host: redis host
            port: redis port

        Returns:
            redis sessionmaker(function)
        """

        def get_client():
            client: Redis = Redis(host=host, port=port)
            return client

        return get_client

    async def close(self) -> None:
        """
        Delete sessionmaker of redis database
        Returns:
            None
        """
        self._sessionmaker = None

    async def ping(self) -> None:
        """
        Ping to redis database
        Returns:
            None or rise errors
        """
        async with self.session() as session:
            await session.ping()

    @contextlib.asynccontextmanager
    async def session(self) -> Redis:
        """
        Get session of redis database
        Returns:
            yield session of redis database
        """
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            yield session


redis_db_manager = RedisSessionManager()
