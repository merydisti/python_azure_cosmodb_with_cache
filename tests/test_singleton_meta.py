from classes.singleton_meta import SingletonMeta


def test_singleton():
    class ASingleton(metaclass=SingletonMeta):
        pass

    instance_a = ASingleton()
    instance_b = ASingleton()
    assert instance_a is instance_b
