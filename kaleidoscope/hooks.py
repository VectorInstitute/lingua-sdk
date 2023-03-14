from types import SimpleNamespace

import torch

"""save data in these hooks

next gen will be web pdb
"""


class TestForwardHook(SimpleNamespace):
    """this class's call signature should mimic the same
    thing as the pytorch forward hooks, except you don't have access
    to the module, this is to prevent accidental mutation of the model
    """

    def __call__(self, input, output):
        print(input[0].shape, output[0].shape)
        with torch.no_grad():
            self.output = output[0].sum()
