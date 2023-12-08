#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import getpass
import logging as log
import pymysql
import yaml
from tidb_info import baseline_checker


def output_dict(conn: pymysql.connect, baselinefile: str, policy, checkout):
    """
    按照规则输出核查结果的字典
    :param conn:
    :param baselinefile:
    :param policy: ["force","recommend","all"]
    :param checkout: ["true","false","all"]
    :return:
    """
    with open(baselinefile, 'r', encoding='utf-8') as f:
        baseline_dict = yaml.load(f, Loader=yaml.SafeLoader)
    baseline_result_dict = baseline_checker(conn, baseline_dict)
    result_filter = []
    for i in range(len(baseline_result_dict["variables"])):
        baseline = baseline_result_dict["variables"][i]
        p = baseline["baseline_policy"]
        c = str(baseline["check_baseline"]).lower()
        if p == policy and c == checkout:
            result_filter.append(baseline)
        elif p == policy and checkout == "all":
            result_filter.append(baseline)
        elif policy == "all" and c == checkout:
            result_filter.append(baseline)
        elif policy == "all" and checkout == "all":
            result_filter.append(baseline)
    return {"variables": result_filter}
    # result = yaml.dump(result_filter, indent=2, sort_keys=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TiDB基线核查工具")
    parser.add_argument('-H', '--host', help="IP地址", default="127.0.0.1")
    parser.add_argument('-P', '--port', help="端口号", default=4000, type=int)
    parser.add_argument('-u', '--user', help="用户名", default="root")
    parser.add_argument('-p', '--password', help="密码", nargs="?")
    parser.add_argument("-f", "--baseline-check-file", default="baseline_check.yml", help="基线配置文件,yaml形式")
    parser.add_argument("-o", "--output", help="核查结果")
    parser.add_argument("--type", choices=["force", "recommend", "all"], default="all",
                        help="选择打印级别，force：只打印强制检查不匹配的参数项；recommend：打印force和recommend不匹配的参数项；"
                             "all：忽略打印级别，打印参数项")
    parser.add_argument("--checkout", choices=["true", "false", "all"], default="all",
                        help="打印核查结果符合条件的匹配项，true：打印核查通过的参数项；false：打印核查不通过的参数项；all：忽略核查结果打印参数项")
    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass("Enter your password:")
    log.basicConfig(level=log.INFO,
                    format='%(asctime)s-%(name)s-%(filename)s[line:%(lineno)d]-%(levelname)s-%(message)s')
    try:
        conn = pymysql.connect(host=args.host, port=args.port, user=args.user, password=args.password,
                               database="information_schema")
        output = output_dict(conn, args.baseline_check_file, args.type, args.checkout)
        output_yml = yaml.dump(output, indent=2, sort_keys=False)
        if args.output is None:
            print(output_yml)
        else:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_yml)
    except Exception as e:
        print(f"Error:{e}")
        exit(1)
    if args.output is not None:
        log.info(f"输出文件名为：{args.output}")
    print("Done")
