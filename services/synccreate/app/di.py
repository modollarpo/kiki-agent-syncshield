from dependency_injector import containers, providers
from internal.interfaces import CreativeGenerator

class Container(containers.DeclarativeContainer):
    creative_generator = providers.Factory(CreativeGenerator)
