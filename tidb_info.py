#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pymysql
import logging as log
from collections import namedtuple, OrderedDict
import yaml
from util import variable_data_compare


def get_baseline_vars_map(baselinefile):
    BaseLine = namedtuple('BaseLine', ['default_value', 'baseline_policy', 'baseline_type', 'baseline_value'])
    baseline_vars_map = {}
    file_baseline_vars_map = yaml.load(open(baselinefile, encoding='utf-8'), yaml.SafeLoader)
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


def baseline_checker(conn: pymysql, baselinefile):
    baseline_checker_map = {}
    BaseLineChecker = namedtuple("BaseLineChecker", ["var_type", "var_name", "check_default", "check_baseline",
                                                     "check_policy", "baseline_type", "baseline_value",
                                                     "baseline_default", "database_default"])
    vars_map = get_vars_map(conn)
    baseline_vars_map = get_baseline_vars_map(baselinefile)
    for baseline_key in baseline_vars_map:
        if baseline_key not in vars_map:
            log.log(f"variable:{baseline_key} cannot find in database")
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
                    baseline.baseline_value[1], vars_map[baseline_key], ">=")
            elif baseline.baseline_type == "list":
                # 处理in情况
                for each_baseline_val in baseline.baseline_value:
                    if variable_data_compare(baseline_key[1], each_baseline_val, vars_map[baseline_key], "=="):
                        check_baseline = True
                        break
            baseline_checker_map[baseline_key] = BaseLineChecker(baseline_key[0], baseline_key[1], check_default,
                                                                 check_baseline,
                                                                 baseline.baseline_policy, baseline.baseline_type,
                                                                 baseline.baseline_value,
                                                                 baseline.default_value,
                                                                 vars_map[baseline_key])._asdict()
    return {"variables":[x for x in baseline_checker_map.values()]}



if __name__ == "__main__":
    try:
        conn = pymysql.connect(host="192.168.31.201", port=4000, user="root", password="", database="mysql")
        # result = baseline_checker(conn,'baseline_check.yml')
        result = baseline_checker(conn, 'baseline_check.yml')
        result = yaml.dump(result,indent=2)
        print(result)
    except pymysql.Error as e:
        print(e)
