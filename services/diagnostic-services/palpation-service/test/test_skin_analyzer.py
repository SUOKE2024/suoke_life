"""
test_skin_analyzer - 索克生活项目模块
"""

from internal.signal.skin_analyzer import SkinAnalyzer
from pathlib import Path
import sys
import unittest

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
皮肤分析器测试
"""


# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestSkinAnalyzer(unittest.TestCase):
    """测试皮肤分析器"""
    
    def setUp(self):
        """设置测试环境"""
        # 测试配置
        self.config = {
            'region_mappings': [
                {
                    'id': 'face',
                    'name': '面部',
                    'related_organs': ['lung', 'heart', 'spleen']
                },
                {
                    'id': 'chest',
                    'name': '胸部',
                    'related_organs': ['lung', 'heart']
                },
                {
                    'id': 'abdomen',
                    'name': '腹部',
                    'related_organs': ['spleen', 'stomach', 'liver']
                },
                {
                    'id': 'arm',
                    'name': '手臂',
                    'related_organs': ['lung', 'large_intestine']
                },
                {
                    'id': 'leg',
                    'name': '腿部',
                    'related_organs': ['liver', 'gallbladder', 'spleen']
                }
            ],
            'moisture_thresholds': {
                'dry': 0.3,
                'normal': 0.6,
                'moist': 1.0
            },
            'elasticity_thresholds': {
                'poor': 0.3,
                'normal': 0.7,
                'good': 1.0
            },
            'confidence_threshold': 0.7
        }
        
        self.analyzer = SkinAnalyzer(self.config)
        
        # 测试数据
        self.test_region_data_dry = {
            'region_id': 'face',
            'region_name': '面部',
            'moisture_level': 0.2,
            'elasticity': 0.5,
            'texture': '粗糙',
            'temperature': 36.5,
            'color': '偏白'
        }
        
        self.test_region_data_moist = {
            'region_id': 'chest',
            'region_name': '胸部',
            'moisture_level': 0.8,
            'elasticity': 0.3,
            'texture': '湿滑',
            'temperature': 37.2,
            'color': '偏红'
        }
        
        self.test_regions = [
            self.test_region_data_dry,
            self.test_region_data_moist
        ]
    
    def test_analyze_region_dry(self):
        """测试分析单个区域的干燥皮肤"""
        result = self.analyzer.analyze_region(self.test_region_data_dry)
        
        # 验证结果
        self.assertEqual(result['region_id'], 'face')
        self.assertEqual(result['region_name'], '面部')
        
        # 验证发现
        self.assertTrue(len(result['findings']) > 0)
        
        # 至少有一个与水分相关的发现
        moisture_findings = [f for f in result['findings'] if 'dry' in f['description'].lower()]
        self.assertTrue(len(moisture_findings) > 0)
    
    def test_analyze_region_moist(self):
        """测试分析单个区域的湿润皮肤"""
        result = self.analyzer.analyze_region(self.test_region_data_moist)
        
        # 验证结果
        self.assertEqual(result['region_id'], 'chest')
        
        # 验证发现
        self.assertTrue(len(result['findings']) > 0)
        
        # 至少有一个与水分相关的发现
        moisture_findings = [f for f in result['findings'] if 'moist' in f['description'].lower()]
        self.assertTrue(len(moisture_findings) > 0)
        
        # 至少有一个与弹性相关的发现
        elasticity_findings = [f for f in result['findings'] if 'elasticity' in f['finding_type'].lower()]
        self.assertTrue(len(elasticity_findings) > 0)
    
    def test_analyze_regions(self):
        """测试分析多个区域"""
        result = self.analyzer.analyze_regions(self.test_regions)
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertTrue(len(result['findings']) > 0)
        self.assertNotEqual(result['analysis_summary'], '')
    
    def test_get_overall_skin_condition(self):
        """测试获取整体皮肤状况"""
        # 先分析区域
        regions_analyses = []
        for region in self.test_regions:
            region_analysis = self.analyzer.analyze_region(region)
            regions_analyses.append(region_analysis)
        
        # 获取整体皮肤状况
        overall = self.analyzer.get_overall_skin_condition(regions_analyses)
        
        # 验证结果
        self.assertIn('moisture', overall)
        self.assertIn('elasticity', overall)
        self.assertIn('temperature', overall)
        self.assertIn('notable_features', overall)

if __name__ == '__main__':
    unittest.main() 