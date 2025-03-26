import unittest
from app.app import app
from app.models import db, User, Clothing
from werkzeug.security import generate_password_hash

class TestApp(unittest.TestCase):
    def setUp(self):
        # 设置测试环境
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        # 创建测试用户
        self.test_user = User(
            username='test_user',
            password_hash=generate_password_hash('test_password')
        )
        db.session.add(self.test_user)
        db.session.commit()
        
        # 登录测试用户
        self.client.post('/login', data={
            'username': 'test_user',
            'password': 'test_password'
        }, follow_redirects=True)

    def tearDown(self):
        # 清理测试环境
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        # 测试登录成功
        response = self.client.post('/login', data={
            'username': 'test_user',
            'password': 'test_password'
        }, follow_redirects=True)
        self.assertIn('服装列表', response.get_data(as_text=True))
        
        # 测试登录失败
        response = self.client.post('/login', data={
            'username': 'test_user',
            'password': 'wrong_password'
        }, follow_redirects=True)
        self.assertIn('用户名或密码错误', response.get_data(as_text=True))

    def test_logout(self):
        response = self.client.get('/logout', follow_redirects=True)
        self.assertIn('登录', response.get_data(as_text=True))

    def test_add_clothing(self):
        # 测试添加服装
        response = self.client.post('/add', data={
            'clothing_id': 'TEST001',
            'category': 'T恤',
            'style': 'A',
            'color': '红色',
            'size': 'M',
            'material': '纯棉',
            'cost_price': 50.00,
            'retail_price': 100.00
        }, follow_redirects=True)
        self.assertIn('TEST001', response.get_data(as_text=True))
        
        # 测试添加重复服装编号
        response = self.client.post('/add', data={
            'clothing_id': 'TEST002',
            'category': '牛仔裤',
            'style': 'B',
            'color': '蓝色',
            'size': 'L',
            'material': '牛仔布',
            'cost_price': 80.00,
            'retail_price': 160.00
        }, follow_redirects=True)
        self.assertIn('TEST002', response.get_data(as_text=True))

    def test_update_clothing(self):
        # 先添加一件服装
        self.client.post('/add', data={
            'clothing_id': 'TEST001',
            'category': 'T恤',
            'style': 'A',
            'color': '红色',
            'size': 'M',
            'material': '纯棉',
            'cost_price': 50.00,
            'retail_price': 100.00
        }, follow_redirects=True)
        
        # 测试修改服装
        response = self.client.post('/update/TEST001', data={
            'category': '衬衫',
            'style': 'B',
            'color': '蓝色',
            'size': 'L',
            'material': '棉质',
            'cost_price': 60.00,
            'retail_price': 120.00
        }, follow_redirects=True)
        self.assertIn('衬衫', response.get_data(as_text=True))
        self.assertIn('蓝色', response.get_data(as_text=True))
        self.assertIn('L', response.get_data(as_text=True))
        self.assertIn('棉质', response.get_data(as_text=True))

    def test_delete_clothing(self):
        # 先添加一件服装
        self.client.post('/add', data={
            'clothing_id': 'TEST001',
            'category': 'T恤',
            'style': 'A',
            'color': '红色',
            'size': 'M',
            'material': '纯棉',
            'cost_price': 50.00,
            'retail_price': 100.00
        }, follow_redirects=True)
        
        # 测试删除服装
        response = self.client.get('/delete/TEST001', follow_redirects=True)
        self.assertNotIn('TEST001', response.get_data(as_text=True))

    def test_query_stock(self):
        # 添加多件相同属性的服装
        for i in range(3):
            self.client.post('/add', data={
                'clothing_id': f'TEST00{i+1}',
                'category': 'T恤',
                'style': 'A',
                'color': '红色',
                'size': 'M',
                'material': '纯棉',
                'cost_price': 50.00,
                'retail_price': 100.00
            }, follow_redirects=True)
        
        # 测试查询库存
        response = self.client.get('/query/TEST001', follow_redirects=True)
        content = response.get_data(as_text=True)
        self.assertIn('<strong>当前库存数量：</strong>3', content)
        
        # 测试查询不存在的服装
        response = self.client.get('/query/NONEXIST', follow_redirects=True)
        self.assertIn('未找到该服装信息', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main() 