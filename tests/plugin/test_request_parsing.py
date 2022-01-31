from steamship import RemoteError, Block
from steamship.plugin.parser import ParseRequest, ParseResponse, Parser
from steamship.plugin.service import PluginRequest, PluginResponse

__copyright__ = "Steamship"
__license__ = "MIT"


class TestParser(Parser):
    def run(self, request: PluginRequest[ParseRequest]) -> PluginResponse[ParseResponse]:
        request = TestParser.parse_request(request)
        if type(request) == PluginRequest:
            data = request.data
            assert (len(data.docs) == 1)
            assert (data.docs[0] == "Hi there.")
            return PluginResponse(data=ParseResponse(blocks=[Block(text=data.docs[0])]))
        else:
            return PluginResponse(error=RemoteError(message="Bad type"))


TEST_REQ = ParseRequest(
    docs=["Hi there."],
    blockIds=["ABC"]
)
TEST_PLUGIN_REQ = PluginRequest(data=TEST_REQ)
TEST_REQ_DICT = TEST_PLUGIN_REQ.to_dict()


def _test_resp(res):
    assert (type(res) == PluginResponse)
    assert (type(res.data) == ParseResponse)
    assert (len(res.data.blocks) == 1)
    assert (res.data.blocks[0].text == TEST_REQ.docs[0])


def test_dict_req():
    parser = TestParser()
    res = parser.run(TEST_REQ_DICT)
    _test_resp(res)


def test_obj_req():
    parser = TestParser()
    res = parser.run(TEST_PLUGIN_REQ)
    _test_resp(res)
