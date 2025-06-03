#!/usr/bin/env python3
"""
索克生活APP通信矩阵实施自动化脚本
基于 services/COMMUNICATION_MATRIX_IMPLEMENTATION_PLAN.md
"""

import sys
import yaml
import json
import subprocess
import time
from pathlib import Path

class CommunicationMatrixImplementer:
    """通信矩阵实施器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.services_dir = self.project_root / "services"
        self.config_backup_dir = self.project_root / "config_backup"

        # 新端口分配方案
        self.port_allocation = {
            'core_services': {
                'user-service': 50051,
                'auth-service': 50052,
                'accessibility-service': 50053,
                'health-data-service': 50054,
                'blockchain-service': 50055,
                'rag-service': 50056
            },
            'agent_services': {
                'xiaoai-service': 50061,
                'xiaoke-service': 50062,
                'laoke-service': 50063,
                'soer-service': 50064
            },
            'diagnosis_services': {
                'look-service': 50071,
                'listen-service': 50072,
                'inquiry-service': 50073,
                'palpation-service': 50074
            },
            'support_services': {
                'api-gateway': 8080,
                'message-bus': 8085
            },
            'monitoring_ports': {
                'xiaoai-metrics': 51061,
                'xiaoke-metrics': 51062,
                'gateway-metrics': 51080
            }
        }

    def backup_configs(self):
        """备份现有配置"""
        print("🔄 备份现有配置文件...")

        if not self.config_backup_dir.exists():
            self.config_backup_dir.mkdir(parents=True)

        # 备份关键配置文件
        config_files = [
            "services/agent-services/xiaoai-service/config/config.yaml",
            "services/api-gateway/config/config.yaml",
            "services/message-bus/config/default.yaml"
        ]

        for config_file in config_files:
            src = self.project_root / config_file
            if src.exists():
                dst = self.config_backup_dir / f"{src.name}.backup"
                subprocess.run(['cp', str(src), str(dst)], check=True)
                print(f"✅ 已备份: {config_file}")

    def update_port_configurations(self):
        """更新端口配置"""
        print("🔧 更新服务端口配置...")

        # 更新小艾服务配置
        xiaoai_config_path = self.services_dir / "agent-services/xiaoai-service/config/config.yaml"
        if xiaoai_config_path.exists():
            self._update_yaml_port(xiaoai_config_path, 50061, 51061)
            print("✅ 小艾服务端口已更新")

        # 更新API网关服务发现配置
        self._update_api_gateway_service_discovery()
        print("✅ API网关服务发现配置已更新")

    def _update_yaml_port(self, config_path: Path, service_port: int, metrics_port: int):
        """更新YAML配置文件中的端口"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 更新服务端口
        if 'service' in config:
            config['service']['port'] = service_port

        # 更新监控端口
        if 'monitoring' in config and 'prometheus' in config['monitoring']:
            config['monitoring']['prometheus']['port'] = metrics_port

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    def _update_api_gateway_service_discovery(self):
        """更新API网关服务发现配置"""
        gateway_config_dir = self.services_dir / "api-gateway/config"
        gateway_config_dir.mkdir(parents=True, exist_ok=True)

        service_discovery_config = {
            'services': {
                'user-service': {
                    'endpoints': [f"localhost:{self.port_allocation['core_services']['user-service']}"]
                },
                'auth-service': {
                    'endpoints': [f"localhost:{self.port_allocation['core_services']['auth-service']}"]
                },
                'xiaoai-service': {
                    'endpoints': [f"localhost:{self.port_allocation['agent_services']['xiaoai-service']}"]
                },
                'xiaoke-service': {
                    'endpoints': [f"localhost:{self.port_allocation['agent_services']['xiaoke-service']}"]
                },
                'look-service': {
                    'endpoints': [f"localhost:{self.port_allocation['diagnosis_services']['look-service']}"]
                },
                'listen-service': {
                    'endpoints': [f"localhost:{self.port_allocation['diagnosis_services']['listen-service']}"]
                }
            }
        }

        config_path = gateway_config_dir / "service_discovery.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(service_discovery_config, f, default_flow_style=False)

    def optimize_database_config(self):
        """优化数据库配置"""
        print("🗄️ 优化数据库连接配置...")

        optimized_config = {
            'postgresql': {
                'primary': {
                    'pool_size': 25,
                    'max_overflow': 50,
                    'timeout': 60,
                    'recycle': 7200,
                    'pre_ping': True
                },
                'replicas': [
                    {'host': 'postgres-replica-1', 'pool_size': 15},
                    {'host': 'postgres-replica-2', 'pool_size': 15}
                ]
            },
            'redis': {
                'cluster_nodes': [
                    'redis-1:6379', 'redis-2:6379', 'redis-3:6379'
                ],
                'max_connections': 100,
                'socket_keepalive': True,
                'health_check_interval': 30
            }
        }

        # 创建通用数据库配置目录
        common_config_dir = self.services_dir / "common/config"
        common_config_dir.mkdir(parents=True, exist_ok=True)

        config_path = common_config_dir / "database.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(optimized_config, f, default_flow_style=False)

        print("✅ 数据库配置优化完成")

    def optimize_message_bus_config(self):
        """优化消息总线配置"""
        print("📨 优化消息总线配置...")

        message_bus_config_path = self.services_dir / "message-bus/config/default.yaml"
        if message_bus_config_path.exists():
            with open(message_bus_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 优化服务器配置
            config['server']['workers'] = 16
            config['server']['max_connections'] = 2000

            # 优化Kafka配置
            config['kafka']['num_partitions'] = 6
            config['kafka']['replication_factor'] = 3
            config['kafka']['batch_size'] = 16384
            config['kafka']['compression_type'] = 'snappy'

            # 优化Redis配置
            config['redis']['pool']['max_active'] = 200
            config['redis']['pool']['max_idle'] = 100

            # 优化容错配置
            config['resilience']['retry']['max_attempts'] = 5
            config['resilience']['retry']['max_backoff_ms'] = 5000
            config['resilience']['circuit_breaker']['failure_threshold'] = 10
            config['resilience']['circuit_breaker']['reset_timeout_ms'] = 60000

            with open(message_bus_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

            print("✅ 消息总线配置优化完成")

    def generate_monitoring_config(self):
        """生成监控配置"""
        print("📊 生成监控配置...")

        # 创建监控配置目录
        monitoring_dir = self.project_root / "deploy/monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)

        # Prometheus配置
        prometheus_config = {
            'global': {
                'scrape_interval': '15s',
                'evaluation_interval': '15s'
            },
            'scrape_configs': [
                {
                    'job_name': 'api-gateway',
                    'static_configs': [{'targets': ['api-gateway:51080']}],
                    'scrape_interval': '10s'
                },
                {
                    'job_name': 'xiaoai-service',
                    'static_configs': [{'targets': ['xiaoai-service:51061']}],
                    'scrape_interval': '15s'
                },
                {
                    'job_name': 'message-bus',
                    'static_configs': [{'targets': ['message-bus:9090']}],
                    'scrape_interval': '10s'
                }
            ],
            'rule_files': ['alert_rules.yml'],
            'alerting': {
                'alertmanagers': [
                    {'static_configs': [{'targets': ['alertmanager:9093']}]}
                ]
            }
        }

        with open(monitoring_dir / "prometheus.yml", 'w', encoding='utf-8') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        # 告警规则配置
        alert_rules = {
            'groups': [
                {
                    'name': 'suoke_life_alerts',
                    'rules': [
                        {
                            'alert': 'HighResponseTime',
                            'expr': 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5',
                            'for': '2m',
                            'labels': {'severity': 'warning'},
                            'annotations': {'summary': '响应时间过高: {{ $labels.instance }}'}
                        },
                        {
                            'alert': 'ServiceDown',
                            'expr': 'up == 0',
                            'for': '1m',
                            'labels': {'severity': 'critical'},
                            'annotations': {'summary': '服务下线: {{ $labels.instance }}'}
                        }
                    ]
                }
            ]
        }

        with open(monitoring_dir / "alert_rules.yml", 'w', encoding='utf-8') as f:
            yaml.dump(alert_rules, f, default_flow_style=False)

        print("✅ 监控配置生成完成")

    def validate_configuration(self) -> bool:
        """验证配置正确性"""
        print("🔍 验证配置正确性...")

        validation_results = []

        # 检查端口冲突
        used_ports = set()
        for category in self.port_allocation.values():
            for service, port in category.items():
                if port in used_ports:
                    validation_results.append(f"❌ 端口冲突: {port} 被多个服务使用")
                    return False
                used_ports.add(port)

        validation_results.append("✅ 端口分配无冲突")

        # 检查配置文件存在性
        critical_configs = [
            "services/agent-services/xiaoai-service/config/config.yaml",
            "services/api-gateway/config/service_discovery.yaml",
            "services/common/config/database.yaml"
        ]

        for config_file in critical_configs:
            config_path = self.project_root / config_file
            if config_path.exists():
                validation_results.append(f"✅ 配置文件存在: {config_file}")
            else:
                validation_results.append(f"❌ 配置文件缺失: {config_file}")
                return False

        # 打印验证结果
        for result in validation_results:
            print(result)

        return True

    def run_performance_test(self):
        """运行性能测试"""
        print("⚡ 运行性能测试...")

        # 简单的健康检查测试
        test_endpoints = [
            "http://localhost:8080/health",
            "http://localhost:50061/health",
            "http://localhost:8085/health"
        ]

        for endpoint in test_endpoints:
            try:
                result = subprocess.run(
                    ['curl', '-s', '-w', '%{http_code}', '-o', '/dev/null', endpoint],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0 and result.stdout == '200':
                    print(f"✅ {endpoint} 响应正常")
                else:
                    print(f"⚠️ {endpoint} 响应异常")
            except subprocess.TimeoutExpired:
                print(f"⚠️ {endpoint} 响应超时")
            except Exception as e:
                print(f"❌ {endpoint} 测试失败: {e}")

    def generate_implementation_report(self):
        """生成实施报告"""
        print("📋 生成实施报告...")

        report = {
            'implementation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'port_allocation': self.port_allocation,
            'optimizations_applied': [
                '端口冲突解决',
                '数据库连接池优化',
                '消息总线性能优化',
                '监控配置完善'
            ],
            'expected_improvements': {
                'response_time': '37.5%',
                'throughput': '50%',
                'error_rate_reduction': '75%',
                'monitoring_coverage': '95%'
            }
        }

        report_path = self.project_root / "IMPLEMENTATION_REPORT.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ 实施报告已生成: {report_path}")

    def run_full_implementation(self):
        """执行完整实施流程"""
        print("🚀 开始执行索克生活APP通信矩阵优化实施...")
        print("=" * 60)

        try:
            # 第一阶段：基础配置优化
            print("\n📍 第一阶段：基础配置优化")
            self.backup_configs()
            self.update_port_configurations()
            self.optimize_database_config()

            # 第二阶段：性能优化
            print("\n📍 第二阶段：性能优化")
            self.optimize_message_bus_config()

            # 第三阶段：监控完善
            print("\n📍 第三阶段：监控完善")
            self.generate_monitoring_config()

            # 验证和测试
            print("\n📍 验证和测试")
            if self.validate_configuration():
                print("✅ 配置验证通过")
                self.run_performance_test()
                self.generate_implementation_report()

                print("\n🎉 通信矩阵优化实施完成！")
                print("预期性能提升：")
                print("  • API响应时间提升 37.5%")
                print("  • 系统吞吐量提升 50%")
                print("  • 错误率降低 75%")
                print("  • 监控覆盖率达到 95%")
            else:
                print("❌ 配置验证失败，请检查配置文件")
                return False

        except Exception as e:
            print(f"❌ 实施过程中发生错误: {e}")
            return False

        return True

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--validate-only':
        # 仅验证模式
        implementer = CommunicationMatrixImplementer()
        implementer.validate_configuration()
    else:
        # 完整实施模式
        implementer = CommunicationMatrixImplementer()
        success = implementer.run_full_implementation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()