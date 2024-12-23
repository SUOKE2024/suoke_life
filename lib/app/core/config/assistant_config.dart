class AssistantConfig {
  // 助手配置
  static const xiaoai = {
    'name': '小艾',
    'model': 'doubao-pro-128k',
    'embedding_model': 'doubao-embedding',
    'avatar': 'assets/images/xiaoai_avatar.png',
    'description': '生活助理',
    'role': '用户互动与数据分析专家',
    'features': [
      '语音交互',
      '意图识别',
      '数据分析',
      'LIFE频道管理',
    ],
    'capabilities': {
      'data_processing': [
        '数据预处理',
        '特征提取',
        '隐私保护',
        '数据可视化',
      ],
      'realtime_analysis': [
        '行为分析',
        '场景识别',
        '异常检测',
        '个性化建议',
      ],
    },
    'collaboration': {
      'with_laoke': '知识支持请求',
      'with_xiaoke': '商业信息咨询',
    },
    'prompt': '''你是小艾，一个专业的生活助理，负责用户互动和数据分析。
主要职责：
1. 提供日常生活建议和解决方案
2. 采集和分析用户多维数据
3. 进行实时行为分析和场景识别
4. 管理LIFE频道的数据和服务

工作原则：
1. 注��数据隐私保护
2. 提供个性化建议
3. 进行异常行为检测
4. 与其他助手协作处理专业问题

请以专业、友善、耐心的态度为用户服务。需要专业知识支持时请协调老克，需要商业信息时请协调小克。''',
    'api_integrations': {
      'weather': {
        'provider': 'OpenWeather',
        'endpoints': ['forecast', 'current', 'alerts'],
        'update_frequency': 'hourly',
      },
      'calendar': {
        'provider': 'Google Calendar',
        'scopes': ['read', 'write', 'manage'],
        'sync_frequency': 'realtime',
      },
      'health': {
        'provider': 'Apple HealthKit',
        'data_types': ['activity', 'vitals', 'sleep'],
        'sync_frequency': '15min',
      },
    },
    'service_management': {
      'api_gateway': {
        'monitoring': true,
        'auto_scaling': true,
        'rate_limiting': true,
      },
      'updates': {
        'auto_check': true,
        'frequency': 'daily',
        'notification': true,
      },
      'security': {
        'api_key_rotation': true,
        'access_control': true,
        'audit_logging': true,
      },
    },
    'data_channels': {
      'life': {
        'health_tracking': true,
        'schedule_management': true,
        'habit_monitoring': true,
      },
      'social': {
        'community_updates': true,
        'event_notifications': true,
        'group_activities': true,
      },
      'service': {
        'booking_system': true,
        'feedback_collection': true,
        'support_tickets': true,
      },
    },
  };

  static const laoke = {
    'name': '老克',
    'model': 'doubao-pro-128k',
    'embedding_model': 'doubao-embedding',
    'avatar': 'assets/images/laoke_avatar.png',
    'description': '知识助理',
    'role': '技术架构与知识服务专家',
    'features': [
      '架构管理',
      '知识库管理',
      '数据集管理',
      '算法优化',
    ],
    'capabilities': {
      'knowledge_management': [
        '知识图谱构建',
        '专业文献解读',
        '技术方案评估',
        '架构设计审查',
      ],
      'technical_support': [
        '算法优化建议',
        '技术难点攻关',
        '最佳实践推荐',
        '技术趋势分析',
      ],
    },
    'collaboration': {
      'with_xiaoai': '用户数据分析',
      'with_xiaoke': '商业可行性评估',
    },
    'prompt': '''你是老克，一个专业的知识助理，负责技术架构和知识服务。
主要职责：
1. 提供技术架构建议
2. 管理专业知识库
3. 优化算法和模型
4. 解答专业技术问题

工作原则：
1. 保持技术严谨性
2. 注重方案可行性
3. 持续知识更新
4. 跨领域协作支持

请以严谨、专业、深入的方式回答问题。需要用户数据支持时请���调小艾，需要商业评估时请协调小克。''',
    'knowledge_management': {
      'repositories': {
        'technical_docs': {
          'type': 'git',
          'auto_sync': true,
          'review_required': true,
        },
        'research_papers': {
          'type': 'document_db',
          'auto_index': true,
          'version_control': true,
        },
        'code_samples': {
          'type': 'code_repo',
          'lint_check': true,
          'security_scan': true,
        },
      },
      'datasets': {
        'training_data': {
          'format': 'parquet',
          'validation': true,
          'versioning': true,
        },
        'test_cases': {
          'format': 'json',
          'auto_generation': true,
          'coverage_check': true,
        },
        'benchmarks': {
          'format': 'csv',
          'periodic_update': true,
          'performance_tracking': true,
        },
      },
      'updates': {
        'knowledge_base': {
          'frequency': 'weekly',
          'review_workflow': true,
          'notification': true,
        },
        'algorithms': {
          'auto_optimization': true,
          'a_b_testing': true,
          'rollback_support': true,
        },
      },
    },
  };

  static const xiaoke = {
    'name': '小克',
    'model': 'doubao-pro-32k',
    'avatar': 'assets/images/xiaoke_avatar.png',
    'description': '商务助理',
    'role': '商业决策与市场分析专家',
    'features': [
      '供应链管理',
      '市场分析',
      '商业决策',
      '商业推广',
    ],
    'capabilities': {
      'business_analysis': [
        '市场趋势分析',
        '竞争对手分析',
        '商业模式评估',
        '风险评估',
      ],
      'operation_management': [
        '供应链优化',
        '成本控制',
        '资源调配',
        '绩效分析',
      ],
    },
    'collaboration': {
      'with_xiaoai': '用户需求分析',
      'with_laoke': '技术可行性评估',
    },
    'prompt': '''你是小克，一个专业的商务助理，负责商业决策和市场分析。
主要职责：
1. 进行市场趋势分析
2. 优化供应链管理
3. 提供商业决策建议
4. 协助商业推广策略

工作原则：
1. 数据驱动决策
2. 注重实施效果
3. 平衡成本收益
4. 跨部门协作

请以专业、高效、务实的态度处理商务问题。需要用户洞察时请协调小艾，需要技术支持时请协调老克。''',
    'supply_chain': {
      'agriculture': {
        'product_preparation': {
          'seasonal_planning': true,
          'inventory_forecast': true,
          'quality_control': true,
        },
        'farming_activities': {
          'schedule_optimization': true,
          'resource_allocation': true,
          'weather_integration': true,
        },
        'monitoring': {
          'growth_tracking': true,
          'pest_detection': true,
          'yield_prediction': true,
        },
      },
      'marketplace': {
        'product_listing': {
          'auto_categorization': true,
          'price_optimization': true,
          'stock_management': true,
        },
        'service_management': {
          'provider_verification': true,
          'quality_assurance': true,
          'feedback_system': true,
        },
        'promotions': {
          'campaign_scheduling': true,
          'target_audience': true,
          'performance_tracking': true,
        },
      },
      'notifications': {
        'product_updates': {
          'new_arrivals': true,
          'price_changes': true,
          'stock_alerts': true,
        },
        'service_updates': {
          'availability_changes': true,
          'policy_updates': true,
          'maintenance_notices': true,
        },
        'market_insights': {
          'trend_alerts': true,
          'competitor_updates': true,
          'demand_forecasts': true,
        },
      },
    },
    'workflow_templates': {
      'product_launch': [
        {'step': 'market_research', 'duration': '2w'},
        {'step': 'supplier_selection', 'duration': '1w'},
        {'step': 'quality_check', 'duration': '1w'},
        {'step': 'pricing_strategy', 'duration': '3d'},
        {'step': 'launch_campaign', 'duration': '1w'},
      ],
      'service_onboarding': [
        {'step': 'provider_verification', 'duration': '5d'},
        {'step': 'service_review', 'duration': '3d'},
        {'step': 'documentation_check', 'duration': '2d'},
        {'step': 'trial_period', 'duration': '2w'},
        {'step': 'full_activation', 'duration': '1d'},
      ],
    },
  };

  // 协作场景配置
  static const collaborationScenarios = {
    'product_development': {
      'leader': 'xiaoke',  // 商务主导
      'workflow': [
        {'assistant': 'xiaoai', 'task': '用户需求分析'},
        {'assistant': 'laoke', 'task': '技术方案设计'},
        {'assistant': 'xiaoke', 'task': '商业可行性评估'},
      ],
    },
    'technical_consulting': {
      'leader': 'laoke',  // 技术主导
      'workflow': [
        {'assistant': 'laoke', 'task': '技术问题诊断'},
        {'assistant': 'xiaoai', 'task': '用户场景分析'},
        {'assistant': 'xiaoke', 'task': '解决方案成本评估'},
      ],
    },
    'user_service': {
      'leader': 'xiaoai',  // 服务主导
      'workflow': [
        {'assistant': 'xiaoai', 'task': '需求识别与分类'},
        {'assistant': 'laoke', 'task': '专业知识支持'},
        {'assistant': 'xiaoke', 'task': '增值服务推荐'},
      ],
    },
    'agricultural_product_launch': {
      'leader': 'xiaoke',
      'workflow': [
        {'assistant': 'xiaoai', 'task': '消费者需求分析'},
        {'assistant': 'laoke', 'task': '农业技术指导'},
        {'assistant': 'xiaoke', 'task': '供应链规划'},
        {'assistant': 'xiaoai', 'task': '用户反馈收集'},
        {'assistant': 'xiaoke', 'task': '市场投放策略'},
      ],
    },
    'knowledge_base_update': {
      'leader': 'laoke',
      'workflow': [
        {'assistant': 'laoke', 'task': '知识更新审核'},
        {'assistant': 'xiaoai', 'task': '用户理解度评估'},
        {'assistant': 'xiaoke', 'task': '商业价值评估'},
        {'assistant': 'laoke', 'task': '知识整合发布'},
      ],
    },
  };
} 