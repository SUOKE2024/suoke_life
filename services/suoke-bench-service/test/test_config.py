"""
配置模块测试
"""

import os
import unittest
from pathlib import Path

from internal.suokebench.config import BenchConfig, create_default_config, load_config


class TestConfig(unittest.TestCase):
    """配置模块测试"""
    
    def setUp(self):
        """测试准备"""
        # 创建临时配置目录
        self.test_dir = Path("./test_config")
        self.test_dir.mkdir(exist_ok=True)
        
        # 创建测试配置文件
        self.config_path = self.test_dir / "test_config.yaml"
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("""service_name: "test-service"
version: "0.1.0"
data_root: "./test_data"
cache_dir: "./test_cache"

datasets:
  test_dataset:
    name: "测试数据集"
    path: "./test_data/test_dataset"
    type: "text"
    format: "json"
    size: 10
    description: "测试用数据集"
    tags: ["测试"]

metrics:
  accuracy:
    name: "准确率"
    type: "classification"
    description: "分类准确率"
    threshold: 0.8
    unit: "%"

tasks:
  test_task:
    id: "test_task"
    name: "测试任务"
    type: "TCM_DIAGNOSIS"
    description: "测试用任务"
    datasets: ["test_dataset"]
    metrics: ["accuracy"]

report:
  template_dir: "./test_templates"
  output_dir: "./test_reports"
""")
        
    def tearDown(self):
        """测试清理"""
        # 删除测试文件和目录
        if self.config_path.exists():
            self.config_path.unlink()
            
        if self.test_dir.exists():
            self.test_dir.rmdir()
            
    def test_load_config(self):
        """测试加载配置"""
        config = load_config(str(self.config_path))
        
        # 验证配置内容
        self.assertEqual(config.service_name, "test-service")
        self.assertEqual(config.version, "0.1.0")
        self.assertEqual(config.data_root, "./test_data")
        self.assertEqual(config.cache_dir, "./test_cache")
        
        # 验证数据集配置
        self.assertIn("test_dataset", config.datasets)
        self.assertEqual(config.datasets["test_dataset"].name, "测试数据集")
        self.assertEqual(config.datasets["test_dataset"].size, 10)
        
        # 验证指标配置
        self.assertIn("accuracy", config.metrics)
        self.assertEqual(config.metrics["accuracy"].name, "准确率")
        self.assertEqual(config.metrics["accuracy"].threshold, 0.8)
        
        # 验证任务配置
        self.assertIn("test_task", config.tasks)
        self.assertEqual(config.tasks["test_task"].name, "测试任务")
        self.assertEqual(config.tasks["test_task"].type, "TCM_DIAGNOSIS")
        
    def test_create_default_config(self):
        """测试创建默认配置"""
        config = create_default_config()
        
        # 验证默认配置
        self.assertEqual(config.service_name, "suoke-bench-service")
        self.assertIsInstance(config.version, str)
        self.assertTrue(os.path.isabs(config.data_root))
        self.assertTrue(os.path.isabs(config.cache_dir))
        
        # 验证默认数据集
        self.assertGreaterEqual(len(config.datasets), 1)
        
        # 验证默认指标
        self.assertIn("accuracy", config.metrics)
        
        # 验证默认任务
        self.assertGreaterEqual(len(config.tasks), 1)


if __name__ == "__main__":
    unittest.main()