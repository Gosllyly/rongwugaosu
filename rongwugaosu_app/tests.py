import os

from django.test import TestCase

from rongwugaosu_app.sumo_simulate import simulate



# 确保你的环境变量 DJANGO_SETTINGS_MODULE 指向 Django 项目的配置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rongwugaosu_web.settings")

# Create your tests here.
class MyAppTests(TestCase):

  # 测试仿真程序
  def test_sumo_simulate(self):
    simulate(step=3600)
