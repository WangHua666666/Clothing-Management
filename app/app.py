from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, Clothing, User
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于session加密
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()
    # 创建默认管理员账户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('登录成功')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')
    return render_template('login.html')

# 登出路由
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('已退出登录')
    return redirect(url_for('login'))

# 主页
@app.route('/')
@login_required
def index():
    clothes = Clothing.query.all()
    return render_template('index.html', clothes=clothes)

# 服装入库
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_clothing():
    if request.method == 'POST':
        clothing_id = request.form.get('clothing_id')
        category = request.form.get('category')
        style = request.form.get('style')
        color = request.form.get('color')
        size = request.form.get('size')
        material = request.form.get('material')
        cost_price = float(request.form.get('cost_price'))
        retail_price = float(request.form.get('retail_price'))

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
        db.session.add(new_clothing)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_clothing.html')

# 服装出库（已售出删除）
@app.route('/delete/<string:clothing_id>')
@login_required
def delete_clothing(clothing_id):
    clothing = Clothing.query.get(clothing_id)
    if clothing:
        db.session.delete(clothing)
        db.session.commit()
    return redirect(url_for('index'))

# 服装信息修改
@app.route('/update/<string:clothing_id>', methods=['GET', 'POST'])
@login_required
def update_clothing(clothing_id):
    clothing = Clothing.query.get(clothing_id)
    if request.method == 'POST':
        clothing.category = request.form.get('category')
        clothing.style = request.form.get('style')
        clothing.color = request.form.get('color')
        clothing.size = request.form.get('size')
        clothing.material = request.form.get('material')
        clothing.cost_price = float(request.form.get('cost_price'))
        clothing.retail_price = float(request.form.get('retail_price'))
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_clothing.html', clothing=clothing)

# 查询服装信息及库存
@app.route('/query/<string:clothing_id>')
@login_required
def query_stock(clothing_id):
    clothing = Clothing.query.get(clothing_id)
    if clothing:
        stock_count = Clothing.query.filter_by(
            category=clothing.category,
            style=clothing.style,
            color=clothing.color,
            size=clothing.size,
            material=clothing.material
        ).count()
        return render_template('query_stock.html', clothing=clothing, stock_count=stock_count)
    return "未找到该服装信息"

if __name__ == '__main__':
    app.run(debug=True)