import unittest
from pmworker.step import Step


class TestStep(unittest.TestCase):

    def test_step(self):
        step = Step(1)
        self.assertFalse(
            step.is_thumbnail,
            f"{step} is is_thumbnail, but it should not be!"
        )
