import builtins
import inspect
from collections import (
    OrderedDict,
)
import weakref
from typing import (
    Callable,
    Dict,
    Union,
    List,
    Any,
    Set, Optional)

from py_type_extractor.type_extractor.__base__ import BaseTypeExtractor
from py_type_extractor.type_extractor.middlewares.class_found import class_found_middleware
from py_type_extractor.type_extractor.middlewares.dict_found import dict_found_middleware
from py_type_extractor.type_extractor.middlewares.enum_found import enum_found_middleware
from py_type_extractor.type_extractor.middlewares.fixed_generic_found import fixed_generic_found_middleware
from py_type_extractor.type_extractor.middlewares.function_found import func_found_middleware
from py_type_extractor.type_extractor.middlewares.list_found import list_found_middleware
from py_type_extractor.type_extractor.middlewares.literal_found import literal_found_middleware
from py_type_extractor.type_extractor.middlewares.mapping_found import mapping_found_middleware
from py_type_extractor.type_extractor.middlewares.newtype_found import newtype_found_middleware
from py_type_extractor.type_extractor.middlewares.tuple_found import tuple_found_middleware
from py_type_extractor.type_extractor.middlewares.type_or import typeor_middleware
from py_type_extractor.type_extractor.nodes.BaseNodeType import NodeType, BaseNodeType
from py_type_extractor.type_extractor.nodes.BaseOption import BaseOption
from py_type_extractor.type_extractor.nodes.NoneNode import none_node_middleware
from py_type_extractor.type_extractor.middlewares.typeddict_found import typeddict_found_middleware
from py_type_extractor.type_extractor.middlewares.TypeVar import typevar_found_middleware
from py_type_extractor.type_extractor.nodes.UnknownFound import unknown_found


def is_builtin(typ):
    return inspect.getmodule(typ) is builtins


def builtin_middleware(typ, type_extractor: 'TypeExtractor', options: Set[BaseOption]):
    if is_builtin(typ):
        return typ


class TypeExtractor(BaseTypeExtractor):
    middlewares: List[
        Callable[
            [Any, 'TypeExtractor', Set[BaseOption]],
            BaseNodeType,
        ]
    ] = [
        enum_found_middleware,
        list_found_middleware,
        typeor_middleware,
        typeddict_found_middleware,
        literal_found_middleware,
        dict_found_middleware,
        tuple_found_middleware,
        mapping_found_middleware,
        typevar_found_middleware,
        fixed_generic_found_middleware,
        class_found_middleware,
        newtype_found_middleware,
        func_found_middleware,
        none_node_middleware,
        builtin_middleware,
        typeddict_found_middleware,
    ]

    collected_types: Dict[str, NodeType]

    def __init__(self):
        self.functions = dict()
        self.classes = dict()
        self.typed_dicts = dict()
        BaseTypeExtractor.__init__(self)

    def params_to_nodes(
            self,
            params: Dict[str, Union[type, None]],
            param_names_list: List[str],
            options: Optional[Set[BaseOption]] = None,
    ):
        processed_params: OrderedDict[str, NodeType] = OrderedDict()
        banned_words = [
            'self', 'return', '_cls',
        ]
        _param_names_list = filter(lambda name: name not in banned_words, param_names_list)
        for param_name in _param_names_list:
            processed_params[param_name] = self.rawtype_to_node(
                params.get(param_name) or inspect._empty,  # type: ignore
                options=options,
            )
        return processed_params

    def rawtype_to_node(
            self, typ,
            options: Optional[Set[BaseOption]] = None,
    ):
        for middleware in self.middlewares:
            value = middleware(typ, self, options or set())
            if value is not None:
                return value
        return unknown_found

    def add(
            self,
            options: Optional[Set[BaseOption]] = None,
    ):
        def add_decoration(typ):
            return self.rawtype_to_node(typ, options or set())

        return add_decoration
