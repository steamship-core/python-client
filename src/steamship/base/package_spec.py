from typing import List, Optional

from steamship.base.configuration import CamelModel


class ArgSpec(CamelModel):
    name: str
    kind: str
    doc: Optional[str] = None

    def doc_string(self, name_width: Optional[int] = None, prefix: str = "") -> str:
        width = name_width or len(self.name)
        ret = f"{prefix}{self.name.ljust(width)} - {self.kind}"
        if self.doc:
            ret += f"\n{prefix}  {self.doc}"
        return ret


class MethodSpec(CamelModel):
    path: str
    verb: str
    returns: str
    doc: Optional[str] = None
    args: Optional[List[ArgSpec]] = None

    def doc_string(self, name_width: Optional[int] = None, prefix: str = "  ") -> str:
        width = name_width or len(self.path)
        ret = f"{self.verb.ljust(4)} {self.path.lstrip('/').ljust(width)} -> {self.returns}"
        if self.args:
            name_width = max([len(arg.name) or 0 for arg in self.args])
            for arg in self.args:
                arg_doc_string = arg.doc_string(name_width, prefix)
                ret += f"\n{arg_doc_string}"
        return ret


class PackageSpec(CamelModel):
    name: str
    doc: Optional[str] = None
    methods: Optional[List[MethodSpec]] = None

    def doc_string(self, prefix: str = "  ") -> str:
        underline = "=" * len(self.name)
        ret = f"{self.name}\n{underline}\n"
        if self.doc:
            ret += f"{self.doc}\n\n"
        else:
            ret += "\n"

        if self.methods:
            name_width = max([len(method.path) or 0 for method in self.methods])
            for method in self.methods:
                method_doc_string = method.doc_string(name_width, prefix)
                ret += f"\n{method_doc_string}"
        return ret
