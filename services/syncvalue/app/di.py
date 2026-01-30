from dependency_injector import containers, providers
from internal.interfaces import LtvService

class Container(containers.DeclarativeContainer):
    ltv_service = providers.Factory(LtvService)
