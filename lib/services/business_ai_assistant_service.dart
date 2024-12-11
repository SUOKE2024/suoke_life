import 'package:flutter/material.dart';
import '../core/di/service_locator.dart';
import '../services/coze_service.dart';

class BusinessAIAssistantService {
  final CozeService _cozeService = serviceLocator<CozeService>();

  // 处理供应商咨询
  Future<String> handleSupplierInquiry(String inquiry) async {
    final response = await _cozeService.chat(
      messages: [
        {
          'role': 'system',
          'content': '''
你是一位专业的商务助理，负责帮助供应商了解平台规则、入驻流程和产品管理。
你需要：
1. 解答供应商关于平台入驻、资质要求的问题
2. 指导供应商完成注册和认证流程
3. 协助供应商进行产品录入和管理
4. 解释平台的运营规则和政策
请用专业、友好的语气回答问题。
'''
        },
        {
          'role': 'user',
          'content': inquiry,
        }
      ],
    );

    return response;
  }

  // 引导供应商入驻
  Future<String> guideSupplierOnboarding() async {
    final response = await _cozeService.chat(
      messages: [
        {
          'role': 'system',
          'content': '''
作为入驻引导助手，请介绍平台的入驻流程：
1. 基本要求：
- 合法经营资质
- 相关行业经验
- 产品质量保证

2. 入驻步骤：
- 提交企业信息
- 上传资质证明
- 签署合作协议
- 等待审核通过

3. 重点提示：
- 诚信经营
- 产品质量
- 服务保障
'''
        }
      ],
    );

    return response;
  }

  // 产品录入指导
  Future<String> guideProductEntry() async {
    final response = await _cozeService.chat(
      messages: [
        {
          'role': 'system',
          'content': '''
作为产品录入助手，请指导供应商完成产品信息录入：
1. 产品基本信息：
- 名称、描述
- 价格、库存
- 规格参数

2. 特殊类目要求：
- 优质农产品溯源信息
- 预定制产品定制选项
- 养生产品功效说明

3. 图片要求：
- 主图要求
- 细节图要求
- 资质证明
'''
        }
      ],
    );

    return response;
  }

  // 政策解读
  Future<String> explainPolicies(String topic) async {
    final response = await _cozeService.chat(
      messages: [
        {
          'role': 'system',
          'content': '''
作为政策解读助手，请解释平台相关政策：
1. 平台规则：
- 商品管理规范
- 定价规则
- 物流要求

2. 质量标准：
- 产品质量要求
- 包装规范
- 储运标准

3. 售后服务：
- 退换货政策
- 客户服务标准
- 争议处理流程
'''
        },
        {
          'role': 'user',
          'content': topic,
        }
      ],
    );

    return response;
  }
} 