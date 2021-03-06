from dataclasses import dataclass, field
from typing import Set

from py_type_extractor.type_extractor.nodes.BaseNodeType import BaseNodeType, NodeType
from py_type_extractor.type_extractor.nodes.BaseOption import BaseOption


@dataclass
class DictFound(BaseNodeType):

    key: NodeType
    value: NodeType

    options: Set[BaseOption] = field(default_factory=set)
