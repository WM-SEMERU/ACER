from typing import Callable, Set, TypeVar
import typing


T = TypeVar("T")
def unique(generator: Callable[..., typing.Generator[T, None, None]]) -> Callable[..., typing.Generator[T, None, None]]: 
    '''
    Decorates a generator to return unique items.
    '''
    def _inner(value: T) -> typing.Generator[T, None, None]: 
        seen: Set[T] = set()
        for next in generator(value):
            if next not in seen: 
                yield next 
                seen.add(next)
    
    return _inner
