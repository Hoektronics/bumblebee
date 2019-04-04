import json

from bumblebee.host.types import Bot


class TestTypes(object):
    def test_bot_driver_handles_object(self):
        bot = Bot(
            id=1,
            name="Test",
            status="idle",
            type="3d_printer",
            driver={
                "type": "dummy",
            }
        )

        assert bot.driver == {
            "type": "dummy"
        }

    def test_bot_driver_handles_serialized_json(self):
        bot = Bot(
            id=1,
            name="Test",
            status="idle",
            type="3d_printer",
            driver=json.dumps({
                "type": "dummy",
            })
        )

        assert bot.driver == {
            "type": "dummy"
        }