#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import ast
def check_number(s):
    """
    判断当前字符串是否数字类型，并返回浮点数
    :param s:
    :return: (数字,是否数字)
    """
    # 确保传入的是字符串类型
    s = str(s)
    if re.match(r'^-?\d+$', s):
        return int(s), True
    elif re.match(r'^-?\d+\.\d+$', s):
        return float(s), True
    elif re.match(r'^-\d+$', s):
        return int(s), True
    else:
        return None, False
def check_list(s):
    """
    检查当前字符串是否列表形式，并返回列表
    :param s:
    :return: （列表，是否列表）
    """
    # 确保传入的是字符串类型
    s = str(s)
    try:
        result = ast.literal_eval(s)
        if isinstance(result, list):
            return result, True
    except (SyntaxError, ValueError):
        return None, False
    return None,False


def variable_data_compare(parm, val1: str, val2: str,operator = "=="):
    """
    比较两个参数值是否符合compare_flag逻辑
    operator="="时，判断val1和val2是否相等（对于路径，可能存在包含关系也代表相同）
    operator="<"时,判断val1小于val2,如果小于则返回True
    operator=">"时，判断val1大于val2,如果大于则返回True
    :param parm:参数名称，对于指定类型参数包含关系也代表相同
    :param val1:
    :param val2:
    :return:返回两个值是否逻辑相等
    """
    if operator not in ["==", ">=", "<=", ">", "<", "!=", "<>"]:
        if operator == "lt":
            operator = "<"
        elif operator == "gt":
            operator = ">"
        elif operator == "ne":
            operator = "!="
        elif operator == "eq":
            operator = "=="
        else:
            operator = "=="
    # 支持like语句写法比如['%path%','a%','%b']
    in_to_eq_parms = ['%path%']
    _val1, changed1 = data_cleansing(val1)
    _val2, changed2 = data_cleansing(val2)
    # if changed1 or changed2:
    #     print(f"------>parm:{parm},val1:{val1}~{_val1},val2:{val2}~{_val2}")
    def in_like_list(val, l: list):
        """
        l列表中支持类似于like语法的字符串，当遇到%a%情况时需要进行like匹配处理
        :param val: val值是否在l列表中，如果l列表中元素起始包含%则按照like进行处理
        :param l:
        :return:
        """
        for each_data in l:
            if each_data.startswith("%") and each_data.endswith("%"):
                if each_data.strip("%") in val:
                    return True
            elif each_data.startswith("%"):
                if each_data.endswith(each_data.lstrip("%")):
                    return True
            elif each_data.endswith("%"):
                if each_data.startswith(each_data.rstrip("%")):
                    return True
            else:
                if each_data == val:
                    return True
        return False
    if operator == "==":
        if in_like_list(parm, in_to_eq_parms):
            if _val1 in _val2 or _val2 in _val1:
                return True
            else:
                return False
        else:
            if _val1 == _val2:
                return True
            else:
                return False

    _val1_number,ok1 = check_number(_val1)
    _val2_number,ok2 = check_number(_val2)
    # 可以进行比较
    if ok1 and ok2:
        if operator == ">":
            return _val1_number > _val2_number
        elif operator == ">=":
            return _val1_number >= _val2_number
        elif operator == "<":
            return _val1_number < _val2_number
        elif operator == "<=":
            return _val1_number <= _val2_number
        elif operator == "!=" or operator == "<>":
            return _val1_number != _val2_number
    return False

# 对参数值进行清理
def data_cleansing(val: str) -> (str, bool):
    """
    处理参数值，将其进行标准化
    :param val:
    :return:返回参数值以及是否发生了处理
    """
    val = str(val).strip()
    # 处理bool类型，将bool类型统一变为0,1
    if val.lower() in ["true", "yes", "on"]:
        return "1", True
    elif val.lower() in ["false", "no", "off"]:
        return "0", True
    # 处理MB,MiB等计量单位，统一修改成为Byte并返回
    pattern = re.compile(r'^\d+(\.\d+)?(GiB|MiB|KiB|GB|MB|KB|B)$', re.IGNORECASE)
    if pattern.match(val):
        val = val.lower()
        if "kib" in val:
            return str((2 ** 10) * int(float(val.rstrip("kib")))), True
        elif "mib" in val:
            return str((2 ** 20) * int(float(val.rstrip("mib")))), True
        elif "gib" in val:
            return str((2 ** 30) * int(float(val.rstrip("gib")))), True
        elif "kb" in val:
            return str((1 << 10) * int(float(val.rstrip("kb")))), True
        elif "mb" in val:
            return str((1 << 20) * int(float(val.rstrip("mb")))), True
        elif "gb" in val:
            return str((1 << 30) * int(float(val.rstrip("gb")))), True
        elif "b" in val:
            return str(int(float(val.rstrip("b")))), True
    # 处理x.0形式
    if re.match(r'^\d+\.(0)*$', val):
        return str(int(float(val))), True
    # 处理时间格式，对于xxhxxmxxs形式统一返回成秒
    match = re.compile(r"^((?P<_d>\d+)d)?((?P<_h>\d+)h)?((?P<_m>\d+)m)?(?P<_s>\d+)s$").match(val)
    if match:
        _d, _h, _m, _s = match.group('_d'), match.group('_h'), match.group('_m'), match.group('_s')
        _d = 0 if _d is None else int(_d)
        _h = 0 if _h is None else int(_h)
        _m = 0 if _m is None else int(_m)
        _s = 0 if _s is None else int(_s)
        return _d * 24 * 3600 + _h * 3600 + _m * 60 + _s, True
    match = re.compile(r"^(\d+)d$").match(val)
    if match:
        _d = match.group(1)
        _d = 0 if _d is None else int(_d)
        return _d * 24 * 3600, True
    match = re.compile(r"^(\d+)h$").match(val)
    if match:
        _h = match.group(1)
        _h = 0 if _h is None else int(_h)
        return _h * 3600, True
    match = re.compile(r"^(\d+)m$").match(val)
    if match:
        _m = match.group(1)
        _m = 0 if _m is None else int(_m)
        return _m * 60, True
    # 对列表形式进行处理
    l, ok =  check_list(val)
    if ok:
        return ",".join(l), True
    return val, False
