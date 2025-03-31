# WAF日志自动分析系统

这是一个基于AWS WAF日志的自动分析系统，用于检测和处理异常访问行为。

## 架构
![架构](/image/image2.png "架构")
- Eventbridge: 定义定期任务触发Lambda函数执行。例如可以设置每十分钟执行一次。
- Lambda：定期调度并执行任务，逐个任务进行执行，查询OpenSearch中的日志进行分析，保存执行日志、异常记录、以及对WAF进行自动化更新或者邮件通知。
- RDS：Mysql关系型数据，用以保存执行日志、异常记录、黑名单IP池。
- Opensearch：存储WAF日志。
- Bedrock：调用Claude 3.5 sonnet进行日志的智能分析。
- SNS：用于发送分析结果，尤其是出现异常时的通知。
- Quicksight：提供报表能力，用以展示Mysql相关记录


## 日志处理流程
![数据流](/image/image1.png "数据流")

## AI异常检测范围
![AI检测](/image/image.png "AI检测")

## 项目结构
```
waf_automation/
├── Lambda    
├──── lambda_function.py        # AWS Lambda函数入口
├──── waf_handler.py            # WAF操作处理模块
├──── opensearch_handler.py     # OpenSearch查询处理模块
├──── mysql_handler.py          # MySQL数据库处理模块
├──── claude_handler.py         # Claude AI分析处理模块
├──── allow_iprate_list.py      # IP访问频率分析模块
├──── allow_multija3_list.py    # 多IP使用相同JA3指纹分析模块
├──── block_rules_list.py       # 封禁规则列表处理模块
└──── config.ini                # 项目配置文件
```

## 核心功能模块
### 1. WAF处理模块 (waf_handler.py)
- WAF IP集管理（获取/更新）
- WAF规则组管理
- JA3指纹规则处理
- 支持规则的动态添加和更新
### 2. OpenSearch处理模块 (opensearch_handler.py)
- 提供SQL和DSL两种查询方式
- 支持复杂的日志分析查询
- 与OpenSearch集群的连接管理
### 3. 安全分析功能
- **IP访问频率分析**
  - 分析高频访问IP
  - 识别异常访问模式
- **JA3指纹分析**
  - 多IP使用相同JA3指纹检测
  - 异常JA3指纹识别
- **封禁规则管理**
  - 自动识别需要封禁的IP
  - 基于访问模式的规则生成


## 方案优势
- 智能分析能力 
 - - 运用数据分析技术，快速从海量 WAF 日志中精准定位异常行为
 - - 借助LLM的强大语义理解能力，实现对复杂攻击行为的智能识别
 - - 通过多维度特征分析，有效提取攻击特征，提升检测准确率
- 自动化响应机制 
 - - 基于 AWS WAF SDK 实现防护规则的自动化配置与更新
 - - 建立动态的封禁-解封机制，确保防护策略的灵活性
 - - 支持人工审核与自动处置双模式切换，满足不同场景需求
- 运维效能提升 
 - - 显著降低安全运维人员的工作负载
 - - 加快异常行为的发现、分析和处置流程
 - - 提供可视化的分析结果，辅助决策制定


## 配置说明

### 前置条件
- 配置WAF
 - - WAF 配置
 - - IP set 配置
 - - Rules Group 配置 
- 部署LogHub Solution，并配置采集管道将WAF日志采集到OpenSearch
 - - https://aws-solutions.github.io/centralized-logging-with-opensearch/zh/
- SNS 配置
- Quicksight 配置（选择）


### OpenSearch配置
```ini
[aos-config]
host = host             # OpenSearch主机地址
service = es            # 服务类型
user = admin            # 用户名
pwd = pwd               # 密码
table_name = indexname  # 索引名
```

### MySQL配置
```ini
[mysql-config]
host = host          # MySQL主机地址
user = admin         # 用户名
pwd = pwd            # 密码
database = waf       # 数据库名
```

### WAF配置
```ini
[waf-config]
ipset_name = blackip         # IP集合名称
ipset_region = CLOUDFRONT    # 区域
ipset_id = wafipsetid       # IP集合ID
group_name = ja3            # 规则组名称
group_id = wafgroupid       # 规则组ID
```

### SNS配置
```ini
[sns]
topic_arn = arn:aws:sns:region:accountid:snsname  # SNS主题ARN
```


## 部署方法

### 手动部署

1. 配置文件设置
- 修改config.ini
- 填写相应的配置信息

2. 部署Lambda
- 将代码下载后打包上传到AWS Lambda

3. 配置Lambda
- 执行时长
- VPC(可访问opensearch和mysql)
- 权限（bedrock、waf）

4. 配置Eventbridge
- 配置计划任务

5. 查看结果
- 邮件通知
- 查看WAF规则组更新
- mysql查询执行日志


