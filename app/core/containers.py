from dependency_injector import containers, providers

from infrastructure.postgres_repository import LavkaPostgresRepository
from services.use_cases.courier_service import CourierService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["endpoints"])
    config = providers.Configuration()

    repository = providers.Singleton(
        LavkaPostgresRepository,
        config=config.storage_url,
    )

    courier_service = providers.Factory(CourierService, repository=repository)
