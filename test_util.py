#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import logging as log

import yaml

from util import variable_data_compare,baseline_varidation


class TestUtil(unittest.TestCase):
    def test_variable_data_compare(self):
        self.assertTrue(variable_data_compare('transaction_isolation', 'REPEATABLE-READ', 'REPEATABLE-READ', '=='))
    def test_baseline_varidation(self):
        with open('baseline_check.yml','r') as file:
            yml_dict = yaml.load(file,Loader=yaml.SafeLoader)
        baseline_varidation(yml_dict)

if __name__ == "__main__":
    log.basicConfig(level=log.INFO)
    unittest.main()
