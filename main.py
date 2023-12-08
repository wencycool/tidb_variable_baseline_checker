#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import yaml
from jsonschema import validate

if __name__ == "__main__":
    data_dict = yaml.load(open('baseline_check.yml', encoding='utf-8').read(), yaml.SafeLoader)
    validation_data = json.load(open('baseline_validation.json'))
    # print(yaml.dump(data_dict,indent=2))
    try:
        validate(instance=data_dict, schema=validation_data)
    except Exception as e:
        print(e)
