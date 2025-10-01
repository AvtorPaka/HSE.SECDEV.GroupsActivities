class InfrastructureException(Exception):
    pass


class EntityNotFoundException(InfrastructureException):
    def __init__(self, message: str, entity_id: str = None):
        super().__init__(message)
        self.entity_id = entity_id


class EntityAlreadyExistsException(InfrastructureException):
    def __init__(self, message: str, entity_id: str = None):
        super().__init__(message)
        self.entity_id = entity_id
