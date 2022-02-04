from steamship import BlockTypes, MimeTypes
from steamship.base import Client
from steamship.base.response import TaskStatus
from .helpers import _random_name, _steamship

__copyright__ = "Steamship"
__license__ = "MIT"


# TODO: It should fail if the docs field is empty.
# TODO: It should fail if the file hasn't been converted.

def parse_file(client: Client, parserModel: str):
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

    a.convert().wait()

    raw = a.raw()
    assert (raw.data.decode('utf-8') == CONTENT)

    q1 = a.query(blockType=BlockTypes.H1).data
    assert (len(q1.blocks) == 1)
    assert (q1.blocks[0].type == BlockTypes.H1)
    assert (q1.blocks[0].text == T)

    q2 = a.query(blockType=BlockTypes.Paragraph).data
    assert (len(q2.blocks) == 2)
    assert (q2.blocks[0].type == BlockTypes.Paragraph)
    assert (q2.blocks[0].text == "{} {}".format(P1_1, P1_2))

    # The sentences aren't yet parsed out!
    q2 = a.query(blockType=BlockTypes.Sentence).data
    assert (len(q2.blocks) == 0)

    # Now we parse
    task = a.parse(model="test-parser-v1")
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.taskStatus == TaskStatus.waiting)

    task.wait()
    assert (task.error is None)
    assert (task.task is not None)
    assert (task.task.taskStatus == TaskStatus.succeeded)

    # Now the sentences should be parsed!
    q2 = a.query(blockType=BlockTypes.Sentence).data
    assert (len(q2.blocks) == 2)  # The 5th is inside the header!

    a.clear()

    q2 = a.query(blockType=BlockTypes.Sentence).data
    assert (len(q2.blocks) == 0)  # The 5th is inside the header!

    a.delete()


def test_file_parse():
    steamship = _steamship()
    parse_file(steamship, "test-parser-v1")
