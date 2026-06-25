import typing

T = typing.TypeVar("T", covariant = True)
E = typing.TypeVar("E", covariant = True)

class Ok[T1]:
    def __init__(self, value: T1) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"
    
    def is_ok(self) -> bool:
        return True
    
    def is_err(self) -> bool:
        return False
    
    def ok(self) -> T1:
        return self._value
    
    def err(self) -> None:
        return None
    
    def expect_ok(self, message: str) -> T1:
        return self._value
    
    def expect_err(self, message: str) -> typing.NoReturn:
        raise UnwrapError(self, message)
    
    def expect_ok_or(self, default: typing.Any) -> T1:
        return self._value
    
    def expect_err_or[U](self, default: U) -> U:
        return default
    
    def propagate(self) -> "Ok[T1]":
        return Ok[T1](self.ok())
    
class Err[E1]:
    def __init__(self, value: E1) -> None:
        self._value = value
    
    def __repr__(self) -> str:
        return f"Err({self._value!r})"
    
    def is_ok(self) -> bool:
        return False
    
    def is_err(self) -> bool:
        return True
    
    def ok(self) -> None:
        return None
    
    def err(self) -> E1:
        return self._value
    
    def expect_ok(self, message: str) -> typing.NoReturn:
        raise UnwrapError(self, message)
    
    def expect_err(self, message: str) -> E1:
        return self._value
    
    def expect_ok_or[U](self, default: U) -> U:
        return default
    
    def expect_err_or(self, default: typing.Any) -> E1:
        return self._value
    
    def propagate(self) -> "Err[E1]":
        return Err[E1](self.err())

Result: typing.TypeAlias = typing.Union[Ok[T], Err[E]]

class UnwrapError[T1, E1](Exception):
    def __init__(self, result: Result[T1, E1], message: str) -> None:
        self._result = result

        super().__init__(message)

    @property
    def result(self) -> Result[T1, E1]:
        return self._result

class Check:
    @staticmethod
    def is_ok[T2, E2](result: Result[T2, E2]) -> typing.TypeGuard[Ok[T2]]:
        return result.is_ok()
    
    @staticmethod
    def is_err[T2, E2](result: Result[T2, E2]) -> typing.TypeGuard[Err[E2]]:
        return result.is_err()

    @staticmethod
    def any_ok[T2, E2](iter_: typing.Iterable[Result[T2, E2]]) -> bool:
        def check(x: Result[T2, E2]) -> bool:
            return x.is_ok()
        
        return any(map(check, iter_))

    @staticmethod
    def all_ok[T2, E2](iter_: typing.Iterable[Result[T2, E2]]) -> bool:
        def check(x: Result[T2, E2]) -> bool:
            return x.is_ok()
        
        return all(map(check, iter_))
    
    @staticmethod
    def any_err[T2, E2](iter_: typing.Iterable[Result[T2, E2]]) -> bool:
        def check(x: Result[T2, E2]) -> bool:
            return x.is_err()
        
        return any(map(check, iter_))

    @staticmethod
    def all_err[T2, E2](iter_: typing.Iterable[Result[T2, E2]]) -> bool:
        def check(x: Result[T2, E2]) -> bool:
            return x.is_err()
        
        return all(map(check, iter_))
    
    @classmethod
    def first_ok[T2, E2](cls, iter_: typing.Iterable[Result[T2, E2]]) -> Ok[T2] | None:
        if not cls.any_ok(iter_):
            return None

        if cls.all_ok(iter_):
            return typing.cast(Ok[T2], next(iter(iter_)))
        
        def check[T, E](x: Result[T, E]) -> Ok[T] | None:
            if x.is_ok():
                return typing.cast(Ok[T], x)

        if any((ok := check(x)) for x in iter_):
            if ok is not None:
                return ok
    
    @classmethod
    def first_err[T2, E2](cls, iter_: typing.Iterable[Result[T2, E2]]) -> Err[E2] | None:
        if not cls.any_err(iter_):
            return None

        if cls.all_err(iter_):
            return typing.cast(Err[E2], next(iter(iter_)))
        
        def check[T, E](x: Result[T, E]) -> Err[E] | None:
            if x.is_err():
                return typing.cast(Err[E], x)

        if any((err := check(x)) for x in iter_):
            if err is not None:
                return err