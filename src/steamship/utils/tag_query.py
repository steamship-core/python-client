from abc import ABC
from enum import Enum
from typing import List, Optional


class Predicate(ABC):
    pass


class FluentPredicate(Predicate, ABC):
    def and_(self, other: Predicate):
        if isinstance(other, And):
            preds = [self]
            preds.extend(other.predicates)
            return And(preds)
        return And([self, other])

    def or_(self, other: Predicate):
        if isinstance(other, Or):
            preds = [self]
            preds.extend(other.predicates)
            return Or(preds)
        return Or([self, other])


class SpecialPredicate(ABC):
    pass


class All(SpecialPredicate):
    def __str__(self):
        return "all"


class UnaryPredicate(FluentPredicate, ABC):
    kind: str

    def __init__(self, kind: str):
        self.kind = kind

    def __str__(self):
        return self.kind


class BlockTag(UnaryPredicate):
    def __init__(self):
        super().__init__(kind="blocktag")


class FileTag(UnaryPredicate):
    def __init__(self):
        super().__init__(kind="filetag")


class Op(str, Enum):
    EQUALS = "="
    GT_EQUALS = ">="
    GREATER_THAN = ">"
    LT_EQUALS = "<="
    EXISTS = "exists"


class BinaryPredicate(FluentPredicate, ABC):
    pass


class TagKind(BinaryPredicate):
    kind: str

    def __init__(self, kind: str):
        self.kind = kind

    def __str__(self):
        return f'kind "{self.kind}"'


class TagName(BinaryPredicate):
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self):
        return f'name "{self.name}"'


class TagValue(BinaryPredicate):
    path: str
    operation: Op
    value: Optional[str] = None

    def __init__(self, path: str, operation: Op, value: Optional[str] = None):
        self.path = path
        self.operation = operation
        self.value = value

    def __str__(self):
        if self.value:
            return f'value("{self.path}"){self.operation}"{self.value}"'
        else:
            return f'value("{self.path}") {self.operation}'


class Clause(FluentPredicate, ABC):
    conjunction: str
    predicates: List[Predicate]

    def __init__(self, conjunction: str, predicates: List[Predicate]):
        self.conjunction = conjunction
        self.predicates = predicates

    def __str__(self):
        preds = [str(p) for p in self.predicates]
        return f'({f" {self.conjunction} ".join(preds)})'


class And(Clause):
    def __init__(self, predicates=List[Predicate]):
        super().__init__(conjunction="and", predicates=predicates)


class Or(Clause):
    def __init__(self, predicates=List[Predicate]):
        super().__init__(conjunction="or", predicates=predicates)


class BinaryRelation(FluentPredicate, ABC):
    relation: str
    predicate: Predicate

    def __init__(self, relation: str, predicate: Predicate):
        self.relation = relation
        self.predicate = predicate

    def __str__(self):
        return f"{self.relation} {{ {self.predicate} }}"


class Overlaps(BinaryRelation):
    def __init__(self, predicate: Predicate):
        super().__init__(relation="overlaps", predicate=predicate)


class SameSpan(BinaryRelation):
    def __init__(self, predicate: Predicate):
        super().__init__(relation="samespan", predicate=predicate)


class SameBlock(BinaryRelation):
    def __init__(self, predicate: Predicate):
        super().__init__(relation="sameblock", predicate=predicate)


class SameFile(BinaryRelation):
    def __init__(self, predicate: Predicate):
        super().__init__(relation="samefile", predicate=predicate)
