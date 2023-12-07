#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml

if __name__ == "__main__":
    data_dict = yaml.load(open('baseline_check.yml', encoding='utf-8').read(),yaml.SafeLoader)
    print(yaml.dump(data_dict,indent=2))
    print(data_dict["variables"][2]["baseline-value"])
