from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 创建数据库实例
db = SQLAlchemy()  # 初始化SQLAlchemy，创建db对象用于管理数据库操作

# 定义用户模型
class User(db.Model):
    # 定义表名
    __tablename__ = 'users'
    
    # 定义字段
    id = db.Column(db.Integer, primary_key=True)  # 用户ID，主键，自增
    username = db.Column(db.String(64), unique=True, nullable=False)  # 用户名，唯一，不能为空
    password_hash = db.Column(db.String(128))  # 密码哈希值，不存储明文密码
    
    # 设置密码的方法
    def set_password(self, password):
        """
        设置用户密码，将明文密码转换为哈希存储
        :param password: 明文密码
        """
        self.password_hash = generate_password_hash(password)  # 生成密码哈希并存储
    
    # 验证密码的方法
    def check_password(self, password):
        """
        验证用户密码是否正确
        :param password: 待验证的明文密码
        :return: 密码是否匹配
        """
        return check_password_hash(self.password_hash, password)  # 比对密码哈希

# 定义服装模型
class Clothing(db.Model):
    # 定义表名
    __tablename__ = 'clothing'
    
    # 定义字段
    id = db.Column(db.String(64), primary_key=True)  # 服装ID，使用字符串类型，作为主键
    category = db.Column(db.String(64), nullable=False)  # 服装类别，不能为空
    style = db.Column(db.String(64), nullable=False)  # 服装款式，不能为空
    color = db.Column(db.String(64), nullable=False)  # 服装颜色，不能为空
    size = db.Column(db.String(16), nullable=False)  # 服装尺码，不能为空
    material = db.Column(db.String(64), nullable=False)  # 服装材质，不能为空
    entry_time = db.Column(db.DateTime, default=datetime.now)  # 入库时间，默认为当前时间
    cost_price = db.Column(db.Float, nullable=False)  # 成本价，浮点数，不能为空
    retail_price = db.Column(db.Float, nullable=False)  # 零售价，浮点数，不能为空
    
    def __repr__(self):
        """
        模型的字符串表示方法
        :return: 服装对象的字符串表示
        """
        return f'<Clothing {self.id} - {self.category} {self.style}>'
