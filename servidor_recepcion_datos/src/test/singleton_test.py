import sys
import os
import json
import unittest

sys.path.append(os.path.abspath("../src"))
from services.singleton import Singleton


class singleton_test(unittest.TestCase):
    def test_singleton_class_if(self):
        """
        Instance is not in the list so the class adds it two times,
        and we assert if there are 2 elements
        """
        singleton_instance = Singleton("1", (), {})
        Singleton.__call__(singleton_instance)
        test = 2
        self.assertEqual(test, len(Singleton._instances.keys()))

    def test_singleton_class_else(self):
        """
        Instance is in the list so the method initializes once
        instead of adding instance two times. so we assert if there's one element
        """
        singleton_instance = Singleton("1", (), {})
        Singleton._instances[singleton_instance] = singleton_instance
        Singleton.__call__(singleton_instance, (), {})
        test = 1
        self.assertEqual(test, len(Singleton._instances.keys()))
