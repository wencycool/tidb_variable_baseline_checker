#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

import pymysql
import logging as log
from collections import namedtuple
import yaml
from util import variable_data_compare, baseline_varidation


def get_baseline_vars_map(baseline_dict):
    BaseLine = namedtuple('BaseLine', ['default_value', 'baseline_policy', 'baseline_type', 'baseline_value'])
    baseline_vars_map = {}
    file_baseline_vars_map = baseline_dict
    for each_baseline in file_baseline_vars_map["variables"]:
        key = (each_baseline["var-type"], each_baseline["var-name"])
        if key not in baseline_vars_map:
            baseline_vars_map[key] = BaseLine(
                each_baseline["default-value"], each_baseline["baseline-policy"], each_baseline["baseline-type"],
                each_baseline["baseline-value"]
            )
    return baseline_vars_map


def get_vars_map(conn: pymysql.Connect):
    """
    获取数据库中所有参数信息
    :param conn:
    :return: {(type,var_name)}
    """
    vars_map = {}
    try:
        cursor = conn.cursor()
        show_var_sql = f"show global variables"
        log.debug(f"查看系统参数信息:{show_var_sql}")
        cursor.execute(show_var_sql)
        var_type = "variable"
        for row in cursor:
            key = (var_type, row[0])
            if key not in vars_map:
                vars_map[key] = row[1]
        show_config_sql = f"show config"
        log.debug(f"查看集群参数信息{show_config_sql}")
        cursor.execute(show_config_sql)
        for row in cursor:
            key = (row[0], row[2])
            if key not in vars_map:
                vars_map[key] = row[3]
    finally:
        cursor.close()
    return vars_map


def baseline_checker(conn: pymysql, baseline_dict):
    """
    连接到数据库中根据基线核查字典:baseline_dict中的规则来检查conn连接中的参数是否符合基线
    :param conn:
    :param baseline_dict:
    :param attr:
    :return:
    """
    # 检查baseline_dict数据是否合法
    baseline_varidation(baseline_dict)

    baseline_checker_map = {}
    BaseLineChecker = namedtuple("BaseLineChecker",
                                 ["var_type", "var_name", "baseline_policy", "check_default", "check_baseline",
                                  "check_policy", "baseline_type", "baseline_value",
                                  "baseline_default", "database_default"])
    vars_map = get_vars_map(conn)
    baseline_vars_map = get_baseline_vars_map(baseline_dict)
    for baseline_key in baseline_vars_map:
        if baseline_key not in vars_map:
            log.info(f"variable:{baseline_key} cannot find in database")
        else:
            # 基线核查主要逻辑部分
            baseline = baseline_vars_map[baseline_key]
            check_baseline = False
            check_default = variable_data_compare(baseline_key[1], baseline.default_value, vars_map[baseline_key], "==")
            if baseline.baseline_type == "point":
                # 处理等值情况
                check_baseline = variable_data_compare(baseline_key[1], baseline.baseline_value[0],
                                                       vars_map[baseline_key], "==")
            elif baseline.baseline_type == "range":
                # 处理范围情况
                check_baseline = variable_data_compare(baseline_key[1], baseline.baseline_value[0],
                                                       vars_map[baseline_key], "<=") and variable_data_compare(
                    baseline_key[1], baseline.baseline_value[1], vars_map[baseline_key], ">=")
            elif baseline.baseline_type == "list":
                # 处理in情况
                for each_baseline_val in baseline.baseline_value:
                    if variable_data_compare(baseline_key[1], each_baseline_val, vars_map[baseline_key], "=="):
                        check_baseline = True
                        break
            baseline_checker = BaseLineChecker(baseline_key[0], baseline_key[1], baseline.baseline_policy,
                                               check_default,
                                               check_baseline,
                                               baseline.baseline_policy, baseline.baseline_type,
                                               baseline.baseline_value,
                                               baseline.default_value,
                                               vars_map[baseline_key])
            # print(dict(baseline_checker._asdict()))
            baseline_checker_map[baseline_key] = baseline_checker._asdict()

    return {"variables": [dict(x) for x in baseline_checker_map.values()]}


if __name__ == "__main__":
    #log.basicConfig(level=log.INFO)
    try:
        conn = pymysql.connect(host="127.0.0.1", port=4000, user="root", password="", database="mysql",
                               connect_timeout=2)
        with open('baseline_check.yml', 'r', encoding='utf-8') as file:
            baseline_dict = yaml.load(file, Loader=yaml.SafeLoader)
        result = baseline_checker(conn, baseline_dict)
        # 只打印policy=force的且check_baseline=false的
        result_filter = []
        for i in reversed(range(len(result["variables"]))):
            baseline = result["variables"][i]
            if baseline["baseline_policy"] == "force" and baseline["check_baseline"] == False:
                result_filter.append(baseline)
        result = yaml.dump(result_filter, indent=2, sort_keys=False)
        print(result)
    except Exception as e:
        print(e)
