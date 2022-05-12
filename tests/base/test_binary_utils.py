import dataclasses

__copyright__ = "Steamship"
__license__ = "MIT"

from steamship.base.binary_utils import flexi_create


def test_dump_string():
    data, mime, encoding = flexi_create(string="Hi")
    assert (data == "Hi")


def test_dump_json():
    assert (flexi_create(json="Hi")[0] == '"Hi"')
    assert (flexi_create(json=True)[0] == 'true')
    assert (flexi_create(json=1.2)[0] == '1.2')
    assert (flexi_create(json=[1, 2, 3])[0] == '[1, 2, 3]')
    assert (flexi_create(json={'hi': 'there'})[0] == '{"hi": "there"}')

    @dataclasses.dataclass
    class Person:
        name: str

    person = Person(name="Ted")
    assert (flexi_create(json=person)[0] == '{"name": "Ted"}')

    @dataclasses.dataclass
    class Person2:
        name: str

        def to_dict(self):
            return {"takes": "precedence"}

    person2 = Person2(name="Ted")
    assert (flexi_create(json=person2)[0] == '{"takes": "precedence"}')
