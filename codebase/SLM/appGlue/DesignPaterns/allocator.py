class Allocator:
    _registry = {}

    @classmethod
    def register(cls, klass, instance):
        cls._registry[klass] = instance

    @classmethod
    def get_instance(cls, klass):
        return cls._registry.get(klass)
