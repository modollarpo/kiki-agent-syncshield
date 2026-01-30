from dependency_injector import containers, providers
from internal.interfaces import CRMTrigger

class Container(containers.DeclarativeContainer):
    crm_trigger = providers.Factory(CRMTrigger)
