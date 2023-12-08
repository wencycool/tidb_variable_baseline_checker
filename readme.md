## tidb-variable-baseline-checker
* **
TiDB参数基线核查工具，给定参数基线模板（参考baseline_check.yml），会对指定tidb集群进行参数检查，包括集群级和系统级参数。

对任意一个参数提供三种匹配方式：
* **point** &nbsp;&nbsp;&nbsp;&nbsp;按照值进行匹配，参数应和基线中给定值**逻辑相等**
* **list** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;按照多值进行匹配，参数值应在该列表中存在
* **range**&nbsp;&nbsp;&nbsp;&nbsp;按照范围进行匹配，参数值应在检查范围之间

参数核查整改分两个模式：
* **force** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;强制整改，对于一些参数如隔离级别会强制设置为RC隔离级别，如果设置为force，则为必须整改项。
* **recommend** &nbsp;推荐整改，对于一些性能参数或者内存参数如语句内存占用会推荐整改成符合基线标准，如果设置为recommend，则为推荐整改项。


**baseline_check.yml** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;提供了参数核查的基线模板，详细描述了填写方法

**baseline_validation.json** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;提供了基线模板中的数据有效性校验


使用方法：
```shell
(venv) PS E:\pythonProject\tidb_variable_baseline_checker> python main.py -h
usage: main.py [-h] [-H HOST] [-P PORT] [-u USER] [-p [PASSWORD]] [-f BASELINE_CHECK_FILE] [-o OUTPUT] [--type {force,recommend,all}] [--checkout {true,false,all}]

TiDB基线核查工具

options:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  IP地址
  -P PORT, --port PORT  端口号
  -u USER, --user USER  用户名
  -p [PASSWORD], --password [PASSWORD]
                        密码
  -f BASELINE_CHECK_FILE, --baseline-check-file BASELINE_CHECK_FILE
                        基线配置文件,yaml形式
  -o OUTPUT, --output OUTPUT
                        核查结果
  --type {force,recommend,all}
                        选择打印级别，force：只打印强制检查不匹配的参数项；recommend：打印force和recommend不匹配的参数项；all：忽略打印级别，打印参数项
  --checkout {true,false,all}
                        打印核查结果符合条件的匹配项，true：打印核查通过的参数项；false：打印核查不通过的参数项；all：忽略核查结果打印参数项

```
示例：   
对`192.168.31.201:4000`的tidb数据库的参数进行基线核查，基线文件为baseline_check.yml,只打印参数基线为推荐整改（type=recommend）且不符合基线（checkout=false）的参数，并输出到result.yml文件中。

```shell
(venv) PS E:\pythonProject\tidb_variable_baseline_checker> python main.py -H 192.168.31.201 -P 4000 -u root -p -f "baseline_check.yml" --type=recommend --checkout=false --output=result.yml
Enter your password:
2023-12-08 22:42:08,204-root-tidb_info.py[line:75]-INFO-variable:('tidb', 'log.enable-slow-log') cannot find in database
2023-12-08 22:42:08,205-root-tidb_info.py[line:75]-INFO-variable:('tidb', 'oom-use-tmp-storage') cannot find in database
2023-12-08 22:42:08,205-root-tidb_info.py[line:75]-INFO-variable:('tidb', 'performance.run-auto-analyze') cannot find in database
2023-12-08 22:42:08,205-root-tidb_info.py[line:75]-INFO-variable:('tikv', 'log-level') cannot find in database
2023-12-08 22:42:08,205-root-tidb_info.py[line:75]-INFO-variable:('tiflash', 'logger.level') cannot find in database
2023-12-08 22:42:08,207-root-main.py[line:72]-INFO-输出文件名为：result.yml
Done
(venv) PS E:\pythonProject\tidb_variable_baseline_checker> 

```    
_log日志打印在基线参数中配置但是在数据库中不存在的参数（可能基线参数模板是老系统配置项，但集群版本较新，参数已经废弃）_   
查看生成的`result.yml`文件，生成不符合推荐整改的基线参数
```yaml
variables:
- var_type: variable
  var_name: tidb_mem_quota_query
  baseline_policy: recommend
  check_default: true
  check_baseline: false
  baseline_type: range
  baseline_value:
  - 2GB
  - 10GB
  baseline_default: 1073741824
  database_default: '1073741824'
```
对于`result.yml`文件结果说明：
```text
var_type:          参数类型，参考baseline_check.yml部分说明。
var_name:          参数名称，参考baseline_check.yml部分说明。
baseline_policy:   参数核查整改级别，参考baseline_check.yml部分说明。
check_default:     数据库中参数值是否和基线默认值一致，一致则为true。
check_baseline:    数据库中参数值是否在基线核查范围之内，满足条件则为true。
baseline_type:     基线参数取值类别，参考baseline_check.yml部分说明。
baseline_value：   基线参数值，参考baseline_check.yml部分说明。
baseline_default： 基线参数默认值，参考baseline_check.yml部分说明。
database_default： 数据库中参数默认值，如果看到和baseline_default不同但是check_default=true，则说明两个值逻辑一致，比如1h10m0s和70m0s结果是一致的。
```

对于`baseline_check.yml`文件中关键属性进行说明：   
```yaml
  - var-type: tidb
    var-name: "binlog.enable"
    default-value: "true"
    baseline-policy: force
    baseline-type: point
    baseline-value: ["true"]
```
说明：
```text
var_type:        参数类型包含系统参数类型：variable,集群配置参数类型：pd,tidb,tikv,tiflash，因此取值范围：['variable','pd','tidb','tikv','tiflash']，必填
var_name:        参数名称，必填
default-value:   基线推荐默认值，必填
baseline_policy: 参数核查整改级别：['force','recommend'],force：强烈建议整改，recommend：推荐整改，必填。
baseline-type:   基线参数取值类别(参考匹配方式）：['point','list','range'] 检查数据库中参数默认值是否和基线模板中默认值一致，用于判断当前参数值是否和推荐默认值一致，必填。
baseline-value:  基线值，必须为列表形式，当baseline-type=point时，baseline-value=['xx'] 列表中只有一个值；当baseline-type=list时，baseline-value=['aa','bb','cc']列表中大于一个值;当baseline-type=range时，baseline-value=['lbound','ubound']列表中为2个值，分别是范围的上下界值（包含上下界）。

根据baseline-value和系统参数值比较时会做数据处理转换后再做匹配，大体处理规则包括如下：
  #['+']代表该参数值不能为空，必须存在,比如在判断路径时候，如果根据系统默认设置为空则不符合规范，需要人工设置。
  #['*']代表该参数值可存在，当出现该值时，都会满足条件，主要用于测试，避免频繁更改整个yml文件的基线条目，直接打标记为["*"]即可忽略基线核查。
  #['%xx%']支持正则形式，如果参数值设置为正则形式，那么对于baseline-type=point,list 类型来说只需要确定参数值like '%xx%'即符合基线值。长用于路径的匹配。
  #['!xx']支持不以xx开头形式
  #['8h10m0s']这种时间格式会统一处理成秒进行匹配
  #['true','Yes','ON']等忽略大小写会统一转换成1进行匹配，同样的['false','No','OFF']会统一转换成0进行匹配。
  #['0.0','0'] 统一设置成0进行匹配
  #['GiB','MiB','KiB','GB','MB','KB'] 等字节计量单位会统一转换成byte进行匹配
```