#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
腹诊分析器测试
"""

import unittest
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from internal.signal.abdominal_analyzer import AbdominalAnalyzer

class TestAbdominalAnalyzer(unittest.TestCase):
    """测试腹诊分析器"""
    
    def setUp(self):
        """设置测试环境"""
        # 测试配置
        self.config = {
            'region_mappings': [
                {
                    'id': 'left_top',
                    'name': '左上腹',
                    'organs': ['liver', 'stomach']
                },
                {
                    'id': 'right_top',
                    'name': '右上腹',
                    'organs': ['liver', 'gallbladder']
                },
                {
                    'id': 'middle',
                    'name': '中腹',
                    'organs': ['small_intestine']
                },
                {
                    'id': 'left_lower',
                    'name': '左下腹',
                    'organs': ['large_intestine']
                },
                {
                    'id': 'right_lower',
                    'name': '右下腹',
                    'organs': ['large_intestine']
                },
                {
                    'id': 'lower',
                    'name': '下腹',
                    'organs': ['bladder', 'uterus']
                }
            ],
            'confidence_threshold': 0.7
        }
        
        self.analyzer = AbdominalAnalyzer(self.config)
        
        # 测试数据
        self.test_region_data_tenderness = {
            'region_id': 'right_top',
            'region_name': '右上腹',
            'tenderness_level': 0.8,
            'tension_level': 0.3,
            'has_mass': False,
            'texture_description': '稍硬'
        }
        
        self.test_region_data_mass = {
            'region_id': 'left_lower',
            'region_name': '左下腹',
            'tenderness_level': 0.3,
            'tension_level': 0.3,
            'has_mass': True,
            'texture_description': '有硬块'
        }
        
        self.test_regions = [
            self.test_region_data_tenderness,
            self.test_region_data_mass
        ]
    
    def test_analyze_region_tenderness(self):
        """测试分析单个区域的压痛"""
        result = self.analyzer.analyze_region(self.test_region_data_tenderness)
        
        # 验证结果
        self.assertEqual(result['region_id'], 'right_top')
        self.assertEqual(result['region_name'], '右上腹')
        
        # 验证发现
        self.assertTrue(len(result['findings']) > 0)
        
        # 至少有一个压痛发现
        tenderness_findings = [f for f in result['findings'] if f['finding_type'] == 'tenderness']
        self.assertTrue(len(tenderness_findings) > 0)
        
        # 验证相关器官
        self.assertIn('liver', result['related_organs'])
        self.assertIn('gallbladder', result['related_organs'])
    
    def test_analyze_region_mass(self):
        """测试分析单个区域的肿块"""
        result = self.analyzer.analyze_region(self.test_region_data_mass)
        
        # 验证结果
        self.assertEqual(result['region_id'], 'left_lower')
        
        # 验证发现
        self.assertTrue(len(result['findings']) > 0)
        
        # 至少有一个肿块发现
        mass_findings = [f for f in result['findings'] if f['finding_type'] == 'mass']
        self.assertTrue(len(mass_findings) > 0)
        
        # 验证相关器官
        self.assertIn('large_intestine', result['related_organs'])
    
    def test_analyze_regions(self):
        """测试分析多个区域"""
        result = self.analyzer.analyze_regions(self.test_regions)
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertTrue(len(result['findings']) > 0)
        self.assertNotEqual(result['analysis_summary'], '')
    
    def test_map_to_tcm_patterns(self):
        """测试映射到中医证型"""
        # 先分析区域
        regions_analyses = []
        for region in self.test_regions:
            region_analysis = self.analyzer.analyze_region(region)
            regions_analyses.append(region_analysis)
        
        # 映射到中医证型
        patterns = self.analyzer.map_to_tcm_patterns(regions_analyses)
        
        # 验证结果
        self.assertTrue(len(patterns) > 0)
        
        # 验证证型结构
        for pattern in patterns:
            self.assertIn('pattern_name', pattern)
            self.assertIn('confidence', pattern)
            self.assertIn('description', pattern)

if __name__ == '__main__':
    unittest.main() 