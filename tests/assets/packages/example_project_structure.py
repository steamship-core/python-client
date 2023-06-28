from steamship.invocable import InvocableResponse, PackageService, get, post

# This is reflected in the docs as Package Project Structure.  If you have to change it
# for SDK changes, make sure to update the docs as well.


class MyPackage(PackageService):
    @get("say_hello")
    def _method_name_need_not_match(self, name: str = None) -> InvocableResponse:
        return InvocableResponse(string=f"Hello, {name}")

    @post("do_something")
    def do_something(self, number: int = None) -> InvocableResponse:
        return InvocableResponse(json={"number": number})
