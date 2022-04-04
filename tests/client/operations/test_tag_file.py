from steamship import MimeTypes, DocTag, PluginInstance
from steamship.base import Client
from steamship.base.response import TaskStatus

from tests.client.helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.

def parse_file(client: Client, parserInstanceHandle: str):
    name_a = "{}.mkd".format(_random_name())
    T = "A Poem"
    P1_1 = "Roses are red."
    P1_2 = "Violets are blue."
    P2_1 = "Sugar is sweet, and I love you."

    CONTENT = "# {}\n\n{} {}\n\n{}".format(T, P1_1, P1_2, P2_1)

    a = client.upload(
        name=name_a,
        content=CONTENT,
        mimeType=MimeTypes.MKD
    ).data
    assert (a.id is not None)
    assert (a.name == name_a)
    assert (a.mimeType == MimeTypes.MKD)

    a.convert(pluginInstance="markdown-converter-default-1.0").wait()

    raw = a.raw()
    assert (raw.data.decode('utf-8') == CONTENT)

    q1 = a.query().data
    assert (len(q1.blocks) == 1)
    assert (q1.blocks[0].type == DocTag.h1)
    assert (q1.blocks[0].text == T)

    q2 = a.query().data
    assert (len(q2.blocks) == 2)
    assert (q2.blocks[0].type == DocTag.paragraph)
    assert (q2.blocks[0].text == "{} {}".format(P1_1, P1_2))

    # The sentences aren't yet parsed out!
    q2 = a.query().data
    assert (len(q2.blocks) == 0)

    # Now we parse
    task = a.tag(pluginInstance=parserInstanceHandle)
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.state == TaskStatus.succeeded)

    # Now the sentences should be parsed!
    q2 = a.query().data
    assert (len(q2.blocks) == 2)  # The 5th is inside the header!

    a.clear()

    q2 = a.query().data
    assert (len(q2.blocks) == 0)  # The 5th is inside the header!

    a.delete()


def test_parse_file():
    steamship = _steamship()
    parser = PluginInstance.create(steamship, pluginHandle='test-tagger').data
    parse_file(steamship, parser.handle)
