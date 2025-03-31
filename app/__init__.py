# 这个文件使app目录成为一个Python包
from app.app import app, create_app

__all__ = ['app', 'create_app'] 