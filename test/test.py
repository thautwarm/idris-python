import sys
import os
import json
import unittest
sys.path.append('..')

from idris_python.read_ir import *



class Test(unittest.TestCase):
    def test_too_known(self):
        sess = LinkSession()
        # load_cam('./test.cam', sess)
        load_cam('/tmp/idris15523-1', sess)
unittest.main()
