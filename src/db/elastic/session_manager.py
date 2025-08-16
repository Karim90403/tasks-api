import contextlib
from typing import Optional

from elasticsearch._async.client import AsyncElasticsearch
from loguru import logger

from db.base.abc_session_manager import BaseSessionManager


class ElasticSessionManager(BaseSessionManager):
    def __init__(self) -> None:
        self._sessionmaker = None

    def init(self, url: str, login: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Init sessionmaker of elasticsearch database
        Args:
            url: elasticsearch protocol://host:port
            login: elasticsearch login if exists
            password: elasticsearch password if exists

        Returns:
            None
        """
        self._sessionmaker = self._elastic_sessionmaker(url, login, password)

    @staticmethod
    def _elastic_sessionmaker(url: str, login: Optional[str] = None, password: Optional[str] = None):
        """
        Init elasticsearch session
        Args:
            url: elasticsearch protocol://host:port
            login: elasticsearch login if exists
            password: elasticsearch password if exists

        Returns:
            elasticsearch sessionmaker(function)
        """

        def get_client():
            logger.info(f"Connecting elasticsearch in {url}")
            elasticsearch_kwargs = {"hosts": url}
            if login and password:
                elasticsearch_kwargs["http_auth"] = (login, password)

            if url.startswith("https://"):
                elasticsearch_kwargs["verify_certs"] = False

            client: AsyncElasticsearch = AsyncElasticsearch(**elasticsearch_kwargs)

            return client

        return get_client

    async def close(self) -> None:
        """
        Delete sessionmaker of elasticsearch database
        Returns:
            None
        """
        self._sessionmaker = None

    async def ping(self) -> None:
        """
        Ping to elastic database
        Returns:
            None or rise errors
        """
        async with self.session() as session:
            await session.ping()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncElasticsearch:
        """
        Get session of elasticsearch database
        Returns:
            yield session of elasticsearch database
        """
        if self._sessionmaker is None:
            raise IOError("DatabaseSessionManager is not initialized")
        async with self._sessionmaker() as session:
            yield session


elastic_db_manager = ElasticSessionManager()
