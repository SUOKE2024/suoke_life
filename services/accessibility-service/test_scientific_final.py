#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
索克生活无障碍服务 - 科学计算库支持最终验证
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print('🔬 索克生活无障碍服务 - 科学计算库支持验证')
    print('=' * 60)

    try:
        # 导入科学计算服务
        from internal.service.scientific_computing import get_scientific_computing_service
        import numpy as np

        # 获取服务实例
        service = get_scientific_computing_service()

        # 检查服务状态
        status = service.get_service_status()
        print(f'📊 服务状态: {status["status"]}')
        print(f'📦 可用库数量: {status["library_count"]}/{status["total_libraries"]}')
        print(f'📈 覆盖率: {status["coverage_percentage"]:.1f}%')

        # 测试核心功能
        print('\n🧪 测试核心功能:')

        # 1. 数据分析
        test_data = [1.0, 2.0, 3.0, 4.0, 5.0, 4.0, 3.0, 2.0, 1.0]
        analysis_result = service.process_data(test_data, 'analyze')
        print(f'✅ 数据分析: {analysis_result["status"]}')

        # 2. 异常检测
        anomaly_result = service.process_data(test_data, 'detect_anomalies', threshold=2.0)
        print(f'✅ 异常检测: {anomaly_result["status"]}')

        # 3. 信号滤波
        filter_result = service.process_data(test_data, 'filter', filter_type='lowpass', cutoff=0.2)
        print(f'✅ 信号滤波: {filter_result["status"]}')

        # 4. 频谱分析
        spectrum_result = service.process_data(test_data, 'spectrum', sample_rate=10.0)
        print(f'✅ 频谱分析: {spectrum_result["status"]}')

        # 5. 数据聚类
        cluster_result = service.process_data(test_data, 'cluster', n_clusters=2)
        print(f'✅ 数据聚类: {cluster_result["status"]}')

        # 6. 可视化数据
        plot_result = service.process_data(test_data, 'plot', plot_type='line')
        print(f'✅ 可视化数据: {plot_result["status"]}')

        # 显示详细统计
        print('\n📈 详细统计:')
        if analysis_result['status'] == 'success':
            stats = analysis_result['statistics']
            print(f'   - 平均值: {stats["mean"]:.3f}')
            print(f'   - 标准差: {stats["std"]:.3f}')
            print(f'   - 数据范围: [{stats["min"]:.3f}, {stats["max"]:.3f}]')

        if anomaly_result['status'] == 'success':
            anomaly_stats = anomaly_result['results']
            print(f'   - 异常点数量: {anomaly_stats["anomaly_count"]}')
            print(f'   - 异常比例: {anomaly_stats["anomaly_percentage"]:.1f}%')

        print('\n🎉 科学计算库支持验证完成！')
        return True

    except Exception as e:
        print(f'❌ 验证失败: {e}')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 