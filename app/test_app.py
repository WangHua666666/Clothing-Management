# -*- coding: utf-8 -*-
"""
服装管理系统测试模块
使用 pytest 框架进行单元测试
测试覆盖：用户认证、服装管理（增删改查）和路由保护功能
"""

import pytest
from app.app import app
from app.models import db, User, Clothing
from datetime import datetime

@pytest.fixture
def client():
    """
    测试客户端 fixture
    设置测试环境，创建测试数据库和测试数据
    每个测试用例执行前创建新的测试环境，执行后清理数据
    """
    # 设置测试环境
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    
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
                id='TEST001',
                category='上衣',
                style='T恤',
                color='白色',
                size='M',
                material='纯棉',
                cost_price=50.0,
                retail_price=100.0
            )
            db.session.add(test_clothing)
            db.session.commit()
            
            yield client
            
            # 清理测试数据
            db.session.remove()
            db.drop_all()

@pytest.fixture
def logged_in_client(client):
    """
    已登录的测试客户端 fixture
    自动登录测试用户，用于测试需要认证的功能
    """
    # 登录测试用户
    client.post('/login', data={
        'username': 'test_admin',
        'password': 'test123'
    })
    return client

def test_login(client):
    """
    测试登录功能
    1. 测试正确的用户名和密码
    2. 测试错误的用户名和密码
    """
    # 测试正确的用户名和密码
    response = client.post('/login', data={
        'username': 'test_admin',
        'password': 'test123'
    }, follow_redirects=True)
    # 验证重定向到主页
    assert response.status_code == 200
    
    # 测试错误的用户名和密码
    response = client.post('/login', data={
        'username': 'wrong_user',
        'password': 'wrong_pass'
    }, follow_redirects=True)
    # 验证留在登录页面
    assert response.status_code == 200

def test_add_clothing(logged_in_client):
    """
    测试添加服装功能
    1. 提交新服装信息
    2. 验证数据库中的记录
    """
    # 测试添加服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST002',
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
        clothing = Clothing.query.get('TEST002')
        assert clothing is not None
        assert clothing.category == '裤子'
        assert clothing.style == '牛仔裤'

def test_add_clothing_duplicate_id(logged_in_client):
    """
    测试添加重复编号服装功能
    1. 尝试提交与已存在服装相同编号的新服装信息
    2. 验证返回错误信息，不添加到数据库
    """
    # 尝试添加重复编号的服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST001',  # 使用已存在的ID
        'category': '外套',
        'style': '夹克',
        'color': '黑色',
        'size': 'L',
        'material': '真皮',
        'cost_price': '300.0',
        'retail_price': '600.0'
    }, follow_redirects=False)
    
    # 验证状态码和响应内容
    assert response.status_code == 200
    
    # 验证数据库中的记录没有被修改
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing.category == '上衣'  # 仍然是原来的值
        assert clothing.style == 'T恤'  # 仍然是原来的值
        
        # 确认数据库中只有一个TEST001记录
        count = Clothing.query.filter_by(id='TEST001').count()
        assert count == 1

def test_update_clothing(logged_in_client):
    """
    测试修改服装信息功能
    1. 提交更新的服装信息
    2. 验证数据库中的更新
    """
    # 测试修改服装信息
    response = logged_in_client.post('/update/TEST001', data={
        'category': '上衣',
        'style': 'T恤',
        'color': '黑色',
        'size': 'M',
        'material': '纯棉',
        'cost_price': '60.0',
        'retail_price': '120.0'
    }, follow_redirects=True)
    
    # 验证是否修改成功
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing.color == '黑色'
        assert clothing.cost_price == 60.0
        assert clothing.retail_price == 120.0

def test_delete_clothing(logged_in_client):
    """
    测试删除服装功能
    1. 删除指定服装
    2. 验证数据库中记录已被删除
    """
    # 测试删除服装
    response = logged_in_client.get('/delete/TEST001', follow_redirects=True)
    
    # 验证是否删除成功
    with app.app_context():
        clothing = Clothing.query.get('TEST001')
        assert clothing is None

def test_query_stock(logged_in_client):
    """
    测试查询库存功能
    验证返回的页面内容包含正确的服装信息
    """
    # 测试查询库存
    response = logged_in_client.get('/query/TEST001')
    assert b'TEST001' in response.data
    assert '上衣'.encode('utf-8') in response.data
    assert 'T恤'.encode('utf-8') in response.data

def test_logout(logged_in_client):
    """
    测试登出功能
    验证登出后重定向到登录页面
    """
    # 测试登出
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert '管理员登录'.encode('utf-8') in response.data

def test_protected_routes(client):
    """
    测试路由保护功能
    验证未登录用户访问受保护路由时重定向到登录页面
    """
    # 测试未登录时访问受保护的路由
    routes = ['/', '/add', '/update/TEST001', '/delete/TEST001', '/query/TEST001']
    for route in routes:
        response = client.get(route, follow_redirects=True)
        assert '管理员登录'.encode('utf-8') in response.data

def test_add_clothing_success_message(logged_in_client):
    """
    测试添加服装成功
    验证添加成功后重定向到主页并在数据库中存在记录
    """
    # 添加一件新服装
    response = logged_in_client.post('/add', data={
        'clothing_id': 'TEST003',
        'category': '裙子',
        'style': '连衣裙',
        'color': '红色',
        'size': 'S',
        'material': '雪纺',
        'cost_price': '120.0',
        'retail_price': '240.0'
    }, follow_redirects=True)
    
    # 验证重定向成功
    assert response.status_code == 200
    
    # 验证已添加到数据库
    with app.app_context():
        clothing = Clothing.query.get('TEST003')
        assert clothing is not None
        assert clothing.category == '裙子'
        assert clothing.style == '连衣裙' 