from typing import Any, Callable
from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable


class APIRouter(FastAPIRouter):
    def api_route(
        self, path: str, *, include_in_schema: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        given_path = path
        path_no_slash = given_path[:-1] if given_path.endswith("/") else given_path

        add_nontrailing_slash_path = super().api_route(
            path_no_slash, include_in_schema=include_in_schema, **kwargs
        )

        add_trailing_slash_path = super().api_route(
            path_no_slash + "/", include_in_schema=False, **kwargs
        )

        def add_path_and_trailing_slash(func: DecoratedCallable) -> DecoratedCallable:
            add_trailing_slash_path(func)
            return add_nontrailing_slash_path(func)

        return (
            add_trailing_slash_path
            if given_path == "/"
            else add_path_and_trailing_slash
        )
