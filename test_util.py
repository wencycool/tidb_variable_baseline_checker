#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import logging as log
from util import variable_data_compare


class TestUtil(unittest.TestCase):
    def test_variable_data_compare(self):
        self.assertTrue(variable_data_compare('transaction_isolation', 'REPEATABLE-READ', 'REPEATABLE-READ', '=='))


if __name__ == "__main__":
    log.basicConfig(level=log.INFO)
    unittest.main()
