import unittest

from main import AsistenAI


class TestAsistenAI(unittest.TestCase):
    def test_device_index_is_valid(self):
        asisten = AsistenAI()
        self.assertTrue(asisten.device_index is None or isinstance(asisten.device_index, int))
        self.assertIsNotNone(asisten.browser_controller)
        self.assertIsNotNone(asisten.system_controller)

    def test_process_command_notepad_and_time(self):
        asisten = AsistenAI()
        asisten.speak = lambda text: None
        asisten.system_controller.open_application = lambda app: True
        asisten.process_command("buka notepad")
        asisten.process_command("jam berapa")


if __name__ == "__main__":
    unittest.main()
