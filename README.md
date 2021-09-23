# auto-reporter
上海科技大学研究生学术报告信息填写脚本

### 运行方法

#### 创建conda虚拟环境并激活
```bash
conda create -n web python=3.8
conda activate web
```

#### 安装依赖包
```bash
conda install -c anaconda pycrypto
pip install requests bs4 xlrd==1.2.0
```
#### 设置参数
学号密码在`config.py`文件里设置，各个参数都有注释，仔细看

#### 学术报告列表
参考Excel文件`report_examples.xlsx`，各个字段的格式最好统一

#### 运行脚本
```bash
python auto_reporter.py xxx.xlsx
```

#### 写在后面的话
我写这个脚本的初衷是为了方便大家填写学术报告信息，对研究生系统进行洪水攻击等行为均与本人无关，一切后果自负！

#### 联系
有问题联系我 <guanjw@shanghaitech.edu.cn>
