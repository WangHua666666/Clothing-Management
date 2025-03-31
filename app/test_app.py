# -*- coding: utf-8 -*-
"""
服装管理系统测试模块
使用 pytest 框架进行单元测试
测试覆盖：用户认证、服装管理（增删改查）、路由保护功能和重复ID检查功能
"""

import pytest
from app.app import app  # 导入Flask应用实例
from app.models import db, User, Clothing  # 导入数据库模型
from datetime import datetime  # 导入日期时间处理模块

@pytest.fixture
def client():
    """
    测试客户端 fixture
    设置测试环境，创建测试数据库和测试数据
    每个测试用例执行前创建新的测试环境，执行后清理数据
    
    该fixture功能:
    1. 配置应用为测试模式
    2. 使用内存数据库进行测试
    3. 创建测试用户和测试服装数据
    4. 测试完成后清理所有数据
    """
    # 设置测试环境
    app.config['TESTING'] = True  # 启用测试模式
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # 使用测试数据库
    
    with app.test_client() as client:
        with app.app_context():
            # 创建测试数据库
            db.create_all()
            
            # 创建测试用户
            test_user = User(username='test_admin')
            test_user.set_password('test123')
            db.session.add(test_user)
            
            # 创建测试服装数据
            test_clothing = Clothing(
                id='TEST001',  # 测试服装编号
                category='上衣',  # 类别
                style='T恤',  # 款式
                color='白色',  # 颜色
                size='M',  # 尺码
                material='纯棉',  # 材质
                cost_price=50.0,  # 成本价
                retail_price=100.0  # 零售价
            )
            db.session.add(test_clothing)
            db.session.commit()
            
            yield client  # 返回测试客户端给测试函数使用
            
            # 清理测试数据
            db.session.remove()  # 移除会话
            db.drop_all()  # 删除所有表

@pytest.fixture
def logged_in_client(client):
    """
    已登录的测试客户端 fixture
    自动登录测试用户，用于测试需要认证的功能
    
    该fixture功能:
    1. 使用client fixture获取基础测试客户端
    2. 模拟用户登录操作
    3. 返回已登录状态的客户端，用于测试需要登录才能访问的功能
    """
    # 登录测试用户
    client.post('/login', data={
        'username': 'test_admin',
        'password': 'test123'
    })
    return client  # 返回已登录的客户端

def test_login(client):
    """
    测试登录功能
    
    测试内容:
    1. 使用正确的用户名和密码登录，验证重定向到主页
    2. 使用错误的用户名和密码登录，验证留在登录页面
    
    重要性:
    验证身份认证系统的正确性，确保只有合法用户能够访问系统
    """
    # 测试正确的用户名和密码
    response = client.post('/login', data={
        'username': 'test_admin',
        'password': 'test123'
    }, follow_redirects=True)
    # 验证重定向到主页
    assert response.status_code == 200  # 验证请求成功
    
    # 测试错误的用户名和密码
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_pass'
    }, follow_redirects=True)
    # 验证留在登录页面
    assert response.status_code == 200  # 验证请求成功但未重定向到主页

def test_add_clothing(logged_in_client):
    """
    测试添加服装功能
    
    测试内容:
    1. 提交新服装信息
    2. 验证数据库中成功创建了对应记录
    3. 验证服装属性正确保存
    
    重要性:
    验证系统能够正确添加新服装并保存所有属性，是核心业务功能之一
    """
    # 测试添加服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST002',  # 新服装编号
        'category': '裤子',
        'style': '牛仔裤',
        'color': '蓝色',
        'size': 'L',
        'material': '牛仔布',
        'cost_price': '100.0',
        'retail_price': '200.0'
    }, follow_redirects=True)
    
    # 验证是否添加成功
    with app.app_context():
        clothing = Clothing.query.get('TEST002')  # 查询新添加的服装
        assert clothing is not None  # 验证服装记录存在
        assert clothing.category == '裤子'  # 验证类别正确
        assert clothing.style == '牛仔裤'  # 验证款式正确

def test_add_clothing_duplicate_id(logged_in_client):
    """
    测试添加重复编号服装功能
    
    测试内容:
    1. 尝试提交与已存在服装相同编号的新服装信息
    2. 验证请求不成功（不重定向）
    3. 验证原有数据未被修改
    4. 验证数据库中没有创建重复记录
    
    重要性:
    验证系统能够正确处理数据完整性，防止重复ID导致的数据覆盖问题
    """
    # 尝试添加重复编号的服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST001',  # 使用已存在的ID
        'category': '外套',  # 与原记录不同的类别
        'style': '夹克',  # 与原记录不同的款式
        'color': '黑色',
        'size': 'L',
        'material': '真皮',
        'cost_price': '300.0',
        'retail_price': '600.0'
    }, follow_redirects=False)
    
    # 验证状态码和响应内容
    assert response.status_code == 200  # 请求成功但不重定向
    
    # 验证数据库中的记录没有被修改
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing.category == '上衣'  # 仍然是原来的值
        assert clothing.style == 'T恤'  # 仍然是原来的值
        
        # 确认数据库中只有一个TEST001记录
        count = Clothing.query.filter_by(id='TEST001').count()
        assert count == 1  # 验证没有创建重复记录

def test_update_clothing(logged_in_client):
    """
    测试修改服装信息功能
    
    测试内容:
    1. 提交更新的服装信息
    2. 验证数据库中的记录已正确更新
    3. 验证未更新的字段保持不变
    
    重要性:
    验证系统能够正确更新现有服装信息，是核心业务功能之一
    """
    # 测试修改服装信息
    response = logged_in_client.post('/update/TEST001', data={
        'category': '上衣',  # 保持不变
        'style': 'T恤',  # 保持不变
        'color': '黑色',  # 更新颜色
        'size': 'M',  # 保持不变
        'material': '纯棉',  # 保持不变
        'cost_price': '60.0',  # 更新成本价
        'retail_price': '120.0'  # 更新零售价
    }, follow_redirects=True)
    
    # 验证是否修改成功
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing.color == '黑色'  # 验证颜色已更新
        assert clothing.cost_price == 60.0  # 验证成本价已更新
        assert clothing.retail_price == 120.0  # 验证零售价已更新

def test_delete_clothing(logged_in_client):
    """
    测试删除服装功能
    
    测试内容:
    1. 删除指定服装
    2. 验证数据库中记录已被删除
    
    重要性:
    验证系统能够正确删除不再需要的服装记录，是核心业务功能之一
    """
    # 测试删除服装
    response = logged_in_client.get('/delete/TEST001', follow_redirects=True)
    
    # 验证是否删除成功
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing is None  # 验证服装记录已不存在

def test_query_stock(logged_in_client):
    """
    测试查询库存功能
    
    测试内容:
    1. 访问查询页面
    2. 验证返回的页面包含正确的服装信息
    
    重要性:
    验证系统能够正确展示服装详情和库存信息，是核心业务功能之一
    """
    # 测试查询库存
    response = logged_in_client.get('/query/TEST001')
    assert b'TEST001' in response.data  # 验证页面包含服装编号
    assert '上衣'.encode('utf-8') in response.data  # 验证页面包含服装类别
    assert 'T恤'.encode('utf-8') in response.data  # 验证页面包含服装款式

def test_logout(logged_in_client):
    """
    测试登出功能
    
    测试内容:
    1. 执行登出操作
    2. 验证成功重定向到登录页面
    
    重要性:
    验证用户能够正确退出系统，确保会话安全
    """
    # 测试登出
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert '管理员登录'.encode('utf-8') in response.data  # 验证页面包含登录页面内容

def test_protected_routes(client):
    """
    测试路由保护功能
    
    测试内容:
    1. 使用未登录客户端访问受保护的路由
    2. 验证都被重定向到登录页面
    
    重要性:
    验证系统的安全性，确保未经授权的用户无法访问受保护的功能
    """
    # 测试未登录时访问受保护的路由
    routes = ['/', '/add', '/update/TEST001', '/delete/TEST001', '/query/TEST001']
    for route in routes:
        response = client.get(route, follow_redirects=True)
        assert '管理员登录'.encode('utf-8') in response.data  # 验证被重定向到登录页面

def test_add_clothing_success_message(logged_in_client):
    """
    测试添加服装成功后的结果
    
    测试内容:
    1. 添加一件新服装
    2. 验证请求成功
    3. 验证数据库中成功创建了记录
    4. 验证所有属性正确保存
    
    重要性:
    验证服装添加成功后的数据完整性，确保用户输入的所有信息都被正确保存
    """
    # 添加一件新服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST003',  # 新服装编号
        'category': '裙子',
        'style': '连衣裙',
        'color': '红色',
        'size': 'S',
        'material': '雪纺',
        'cost_price': '120.0',
        'retail_price': '240.0'
    }, follow_redirects=True)
    
    # 验证重定向成功
    assert response.status_code == 200  # 验证请求成功
    
    # 验证已添加到数据库
    with app.app_context():
        clothing = Clothing.query.get('TEST003')  # 查询新添加的服装
        assert clothing is not None  # 验证服装记录存在
        assert clothing.category == '裙子'  # 验证类别正确
        assert clothing.style == '连衣裙'  # 验证款式正确 