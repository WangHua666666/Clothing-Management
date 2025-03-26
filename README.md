# 服装管理系统

一个基于 Flask 的服装库存管理系统，提供服装信息的增删改查功能，并包含管理员登录认证。

## 功能特点

- 管理员登录认证
- 服装信息管理（增删改查）
- 库存查询
- 响应式界面设计
- 表单验证

## 技术栈

- Python 3.x
- Flask
- SQLAlchemy
- Bootstrap 5
- JavaScript

## 安装说明

1. 克隆项目到本地：
```bash
git clone [项目地址]
cd clothing-management
```

2. 创建并激活虚拟环境：
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 初始化数据库：
```bash
flask db upgrade
```

## 运行说明

1. 启动应用：
```bash
python app/app.py
```

2. 访问系统：
打开浏览器访问 http://127.0.0.1:5000

3. 默认管理员账户：
- 用户名：admin
- 密码：admin123

## 测试

运行测试用例：
```bash
pytest app/test_app.py -v
```

## 项目结构

```
clothing-management/
├── app/
│   ├── __init__.py
│   ├── app.py          # 主应用文件
│   ├── models.py       # 数据模型
│   ├── test_app.py     # 测试用例
│   ├── static/         # 静态文件
│   │   ├── css/
│   │   └── js/
│   └── templates/      # HTML模板
├── venv/               # 虚拟环境
├── requirements.txt    # 项目依赖
└── README.md          # 项目说明
```

## 开发说明

- 使用 SQLite 作为数据库
- 使用 Flask-SQLAlchemy 进行数据库操作
- 使用 Flask-Login 处理用户认证
- 使用 Bootstrap 5 构建响应式界面
- 使用 JavaScript 进行表单验证

## 注意事项

- 首次运行需要初始化数据库
- 请及时修改默认管理员密码
- 建议在生产环境中使用更安全的数据库配置 