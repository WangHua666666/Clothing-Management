# 导入Flask框架相关模块，包括Flask主类、模板渲染、请求处理等
from flask import Flask, render_template, request, redirect, url_for, flash, session
# 导入数据库模型，包括数据库对象和服装、用户模型类
from models import db, Clothing, User
# 导入functools库中的wraps函数，用于保留装饰器函数的原始信息
from functools import wraps

# 创建Flask应用实例
app = Flask(__name__)
# 配置SQLite数据库URI，指定数据库文件位置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothing.db'
# 设置不追踪数据库修改，减少内存使用
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 设置应用密钥，用于会话加密和CSRF保护
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于session加密
# 初始化数据库，将app与SQLAlchemy绑定
db.init_app(app)

# 创建数据库表
with app.app_context():  # 创建应用上下文
    # 根据模型创建所有数据库表
    db.create_all()
    # 创建默认管理员账户（如果不存在）
    admin = User.query.filter_by(username='admin').first()
    if not admin:  # 如果admin用户不存在
        # 创建新的admin用户
        admin = User(username='admin')
        # 设置密码（会自动加密）
        admin.set_password('admin123')
        # 添加到数据库会话
        db.session.add(admin)
        # 提交更改到数据库
        db.session.commit()

# 登录验证装饰器，用于保护需要登录才能访问的路由
def login_required(f):
    # 使用wraps保留原始函数信息
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查用户是否已登录（session中是否有user_id）
        if 'user_id' not in session:
            # 未登录时显示提示消息
            flash('请先登录')
            # 重定向到登录页面
            return redirect(url_for('login'))
        # 已登录时执行原始函数
        return f(*args, **kwargs)
    # 返回装饰后的函数
    return decorated_function

# 登录路由，支持GET和POST请求
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已登录，直接重定向到主页
    if 'user_id' in session:
        # 重定向到首页
        return redirect(url_for('index'))
    
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        # 获取表单中的用户名
        username = request.form.get('username')
        # 获取表单中的密码
        password = request.form.get('password')
        # 根据用户名查询用户
        user = User.query.filter_by(username=username).first()
        
        # 检查用户是否存在且密码是否正确
        if user and user.check_password(password):
            # 将用户ID存入会话，标记为已登录
            session['user_id'] = user.id
            # 显示登录成功消息
            flash('登录成功')
            # 重定向到首页
            return redirect(url_for('index'))
        else:
            # 显示登录失败消息
            flash('用户名或密码错误')
    # 返回登录页面模板
    return render_template('login.html')

# 登出路由
@app.route('/logout')
def logout():
    # 从会话中移除用户ID，注销用户
    session.pop('user_id', None)
    # 显示登出成功消息
    flash('已退出登录')
    # 重定向到登录页面
    return redirect(url_for('login'))

# 主页路由
@app.route('/')
@login_required  # 需要登录才能访问
def index():
    # 查询所有服装信息
    clothes = Clothing.query.all()
    # 渲染主页模板，传入服装列表数据
    return render_template('index.html', clothes=clothes)

# 服装入库路由，支持GET和POST请求
@app.route('/add', methods=['GET', 'POST'])
@login_required  # 需要登录才能访问
def add_clothing():
    # 初始化错误消息为空
    error_message = None
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        # 获取表单中的服装编号
        clothing_id = request.form.get('clothing_id')
        
        # 检查编号是否已存在 - 重要功能：防止重复ID导致数据覆盖
        existing_clothing = Clothing.query.get(clothing_id)
        # 如果服装编号已存在
        if existing_clothing:
            # 设置错误消息
            error_message = '服装编号已存在，请使用其他编号'
            # 返回入库页面，保留用户输入的数据
            return render_template('add_clothing.html', error_message=error_message, 
                                category=request.form.get('category'),
                                style=request.form.get('style'),
                                color=request.form.get('color'),
                                size=request.form.get('size'),
                                material=request.form.get('material'),
                                cost_price=request.form.get('cost_price'),
                                retail_price=request.form.get('retail_price'))
        
        # 获取表单中的各项服装信息
        category = request.form.get('category')
        style = request.form.get('style')
        color = request.form.get('color')
        size = request.form.get('size')
        material = request.form.get('material')
        # 转换成本价为浮点数
        cost_price = float(request.form.get('cost_price'))
        # 转换零售价为浮点数
        retail_price = float(request.form.get('retail_price'))

        # 创建新的服装对象
        new_clothing = Clothing(
            id=clothing_id,
            category=category,
            style=style,
            color=color,
            size=size,
            material=material,
            cost_price=cost_price,
            retail_price=retail_price
        )
        # 添加到数据库会话
        db.session.add(new_clothing)
        # 提交更改到数据库
        db.session.commit()
        # 显示添加成功消息
        flash('服装添加成功')
        # 重定向到首页
        return redirect(url_for('index'))
    # 返回入库页面模板
    return render_template('add_clothing.html', error_message=error_message)

# 服装出库（删除）路由
@app.route('/delete/<string:clothing_id>')
@login_required  # 需要登录才能访问
def delete_clothing(clothing_id):
    # 根据ID查询服装
    clothing = Clothing.query.get(clothing_id)
    # 如果找到服装
    if clothing:
        # 从数据库会话中删除
        db.session.delete(clothing)
        # 提交更改到数据库
        db.session.commit()
    # 重定向到首页
    return redirect(url_for('index'))

# 服装信息修改路由，支持GET和POST请求
@app.route('/update/<string:clothing_id>', methods=['GET', 'POST'])
@login_required  # 需要登录才能访问
def update_clothing(clothing_id):
    # 根据ID查询服装
    clothing = Clothing.query.get(clothing_id)
    # 处理POST请求（表单提交）
    if request.method == 'POST':
        # 更新服装类别
        clothing.category = request.form.get('category')
        # 更新服装款式
        clothing.style = request.form.get('style')
        # 更新服装颜色
        clothing.color = request.form.get('color')
        # 更新服装尺码
        clothing.size = request.form.get('size')
        # 更新服装材质
        clothing.material = request.form.get('material')
        # 更新成本价为浮点数
        clothing.cost_price = float(request.form.get('cost_price'))
        # 更新零售价为浮点数
        clothing.retail_price = float(request.form.get('retail_price'))
        # 提交更改到数据库
        db.session.commit()
        # 重定向到首页
        return redirect(url_for('index'))
    # 返回修改页面模板，传入服装数据
    return render_template('update_clothing.html', clothing=clothing)

# 查询服装信息及库存路由
@app.route('/query/<string:clothing_id>')
@login_required  # 需要登录才能访问
def query_stock(clothing_id):
    # 根据ID查询服装
    clothing = Clothing.query.get(clothing_id)
    # 如果找到服装
    if clothing:
        # 查询具有相同属性的服装数量（库存数）
        stock_count = Clothing.query.filter_by(
            category=clothing.category,
            style=clothing.style,
            color=clothing.color,
            size=clothing.size,
            material=clothing.material
        ).count()
        # 返回查询结果页面，传入服装数据和库存数
        return render_template('query_stock.html', clothing=clothing, stock_count=stock_count)
    # 如果未找到服装，返回错误信息
    return "未找到该服装信息"

# 创建一个入口点函数，用于启动应用
def create_app():
    """
    创建并配置Flask应用实例
    :return: 配置好的Flask应用实例
    """
    return app

# 当直接运行此文件时执行的代码
if __name__ == '__main__':
    # 启动Flask应用，开启调试模式，仅监听本地地址
    app.run(debug=True, host='127.0.0.1', port=5000)