from steamship.invocable import Invocable, post


class ReturnsList(Invocable):
    @post("gimme_a_list")
    def gimme_a_list(self) -> [str]:
        return ["here's", "a", "list"]
