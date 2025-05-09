import 'package:shared_preferences/shared_preferences.dart';
import 'package:suoke_life/domain/models/agent_model.dart';
import 'package:suoke_life/domain/repositories/agent_repository.dart';
import 'package:suoke_life/domain/services/agent_service.dart';
import 'package:suoke_life/ai_agents/llm_manager.dart';
import 'package:suoke_life/ai_agents/models/llm_model.dart';

/// 智能体服务实现类
class AgentServiceImpl implements AgentService {
  /// 智能体仓库
  final AgentRepository _agentRepository;
  
  /// SharedPreferences实例
  final SharedPreferences _prefs;
  
  /// 最近活跃智能体ID的键
  static const String _lastActiveAgentKey = 'last_active_agent_id';
  
  /// 默认智能体类型
  static const AgentType _defaultAgentType = AgentType.xiaoAi;
  
  /// LLM管理器
  final LLMManager _llmManager = LLMManager();

  /// 构造函数
  AgentServiceImpl(this._agentRepository, this._prefs);

  @override
  Future<void> initializeAgentSystem() async {
    // 初始化大模型服务
    await _llmManager.initialize();
    
    // 这里可以进行一些初始化操作，如加载配置、预热模型等
    // 对于MVP阶段，我们简单地确保可以获取到所有智能体
    await _agentRepository.getAgents();
    
    // 如果没有设置默认智能体，则设置小艾为默认智能体
    if (!_prefs.containsKey(_lastActiveAgentKey)) {
      final defaultAgent = await getAgentByType(_defaultAgentType);
      if (defaultAgent != null) {
        _prefs.setString(_lastActiveAgentKey, defaultAgent.id);
      }
    }
  }

  @override
  Future<Agent> switchActiveAgent(AgentType type) async {
    final agent = await getAgentByType(type);
    if (agent != null) {
      _prefs.setString(_lastActiveAgentKey, agent.id);
      return agent;
    } else {
      throw Exception('找不到指定类型的智能体: $type');
    }
  }

  @override
  Future<Agent> getDefaultAgent() async {
    return await getAgentByType(_defaultAgentType) ?? 
        (await _agentRepository.getAgents()).first;
  }

  @override
  Future<Agent?> getLastActiveAgent() async {
    final lastActiveAgentId = _prefs.getString(_lastActiveAgentKey);
    if (lastActiveAgentId != null) {
      return await _agentRepository.getAgentById(lastActiveAgentId);
    }
    return await getDefaultAgent();
  }

  @override
  Future<Agent> recommendAgentForMessage(String message) async {
    // 使用LLM进行智能推荐（如果可用）
    try {
      final systemPrompt = '''
你是索克生活APP中的智能体分发服务。你的任务是根据用户的输入，判断应该由哪个智能体来处理这个问题。
可选的智能体有：
1. 小艾(xiaoAi): 通用型助手，负责回答用户关于APP使用、基础健康咨询等问题
2. 小克(xiaoKe): 产品与服务专家，负责推荐和介绍中医健康产品与服务
3. 老克(laoKe): 中医理论专家，负责回答中医理论、知识和专业问题
4. 索儿(suoEr): 健康生活顾问，负责提供个性化的健康生活方案和建议

分析用户的问题后，只返回推荐的智能体类型代码(xiaoAi/xiaoKe/laoKe/suoEr)，不要返回其他内容。
''';

      final response = await _llmManager.chat(
        message: message,
        systemPrompt: systemPrompt,
        temperature: 0.1, // 低温度以获得更确定的回答
      );
      
      // 解析响应
      final lowercaseResponse = response.toLowerCase().trim();
      
      Agent? agent;
      if (lowercaseResponse.contains('xiaoai')) {
        agent = await getAgentByType(AgentType.xiaoAi);
      } else if (lowercaseResponse.contains('xiaoke')) {
        agent = await getAgentByType(AgentType.xiaoKe);
      } else if (lowercaseResponse.contains('laoke')) {
        agent = await getAgentByType(AgentType.laoKe);
      } else if (lowercaseResponse.contains('suoer')) {
        agent = await getAgentByType(AgentType.suoEr);
      }
      
      if (agent != null) {
        return agent;
      }
    } catch (e) {
      // 如果LLM推荐失败，回退到关键词匹配
      print('LLM推荐失败，回退到关键词匹配: $e');
    }
    
    // 简单的关键词匹配推荐逻辑（作为备份）
    final lowerMessage = message.toLowerCase();
    
    // 服务和产品相关关键词，推荐小克
    if (lowerMessage.contains('服务') || 
        lowerMessage.contains('产品') || 
        lowerMessage.contains('预约') || 
        lowerMessage.contains('购买') ||
        lowerMessage.contains('推荐')) {
      final agent = await getAgentByType(AgentType.xiaoKe);
      if (agent != null) return agent;
    }
    
    // 知识和理论相关关键词，推荐老克
    else if (lowerMessage.contains('知识') || 
             lowerMessage.contains('理论') || 
             lowerMessage.contains('概念') || 
             lowerMessage.contains('经络') ||
             lowerMessage.contains('穴位') ||
             lowerMessage.contains('中医')) {
      final agent = await getAgentByType(AgentType.laoKe);
      if (agent != null) return agent;
    }
    
    // 生活和健康数据相关关键词，推荐索儿
    else if (lowerMessage.contains('生活') || 
             lowerMessage.contains('习惯') || 
             lowerMessage.contains('睡眠') || 
             lowerMessage.contains('饮食') ||
             lowerMessage.contains('运动')) {
      final agent = await getAgentByType(AgentType.suoEr);
      if (agent != null) return agent;
    }
    
    // 默认推荐小艾
    final defaultAgent = await getAgentByType(AgentType.xiaoAi);
    if (defaultAgent != null) {
      return defaultAgent;
    }
    
    // 如果所有方法都失败，抛出异常
    throw Exception('无法找到合适的智能体');
  }

  @override
  Future<List<String>> getAgentSuggestedResponses(AgentType type) async {
    // 使用LLM生成个性化的建议回复
    try {
      final systemPrompt = '''
你是索克生活APP中的${agentTypeToChineseName(type)}智能体。请根据你的角色和专长，生成4条用户可能想问你的问题或请求。
这些问题将以建议回复的形式呈现给用户，用户可以点击这些建议来快速与你交流。
请确保这些问题代表性强，能体现你的专业领域。
直接列出四个问题，每个问题不超过20个字，不要有编号或其他额外文字。
''';

      final response = await _llmManager.chat(
        message: "请生成${agentTypeToChineseName(type)}的4条建议回复",
        systemPrompt: systemPrompt,
        temperature: 0.7,
      );
      
      // 解析响应为列表
      final suggestions = response
          .split('\n')
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .take(4)
          .toList();
      
      if (suggestions.length == 4) {
        return suggestions;
      }
    } catch (e) {
      print('LLM生成建议回复失败: $e');
    }
    
    // 如果LLM生成失败，使用预设的建议回复
    switch (type) {
      case AgentType.xiaoAi:
        return [
          '我想了解一下中医四诊是什么？',
          '如何判断自己的体质类型？',
          '我最近有些乏力，可能是什么原因？',
          '请帮我做一次健康评估。',
        ];
      case AgentType.xiaoKe:
        return [
          '有哪些适合我体质的产品推荐？',
          '我想预约一次线上健康咨询。',
          '如何购买正宗的药食同源产品？',
          '有什么健康监测设备可以推荐？',
        ];
      case AgentType.laoKe:
        return [
          '请介绍一下中医体质理论。',
          '什么是阴阳五行学说？',
          '十二经络的作用是什么？',
          '中医如何看待亚健康状态？',
        ];
      case AgentType.suoEr:
        return [
          '我晚上总是睡不好，有什么建议？',
          '适合我体质的日常饮食有哪些？',
          '如何培养健康的生活习惯？',
          '请帮我制定一份健康计划。',
        ];
    }
  }

  @override
  Future<Agent?> checkAndHandleAgentSwitchRequest({
    required AgentType currentAgentType,
    required String message,
  }) async {
    try {
      // 使用LLM判断是否需要转交给其他智能体
      final systemPrompt = '''
你是索克生活APP中的智能体协调服务。你的任务是判断用户的问题是否应该由当前的智能体回答，或者转交给更合适的智能体。

当前智能体: ${agentTypeToChineseName(currentAgentType)}

可选的智能体有：
1. 小艾(xiaoAi): 通用型助手，负责回答用户关于APP使用、基础健康咨询等问题
2. 小克(xiaoKe): 产品与服务专家，负责推荐和介绍中医健康产品与服务
3. 老克(laoKe): 中医理论专家，负责回答中医理论、知识和专业问题
4. 索儿(suoEr): 健康生活顾问，负责提供个性化的健康生活方案和建议

分析用户的问题后，如果当前智能体适合回答，返回"current"；如果应该由其他智能体回答，则返回推荐的智能体类型代码(xiaoAi/xiaoKe/laoKe/suoEr)。只返回一个代码，不要返回其他内容。
''';

      final response = await _llmManager.chat(
        message: message,
        systemPrompt: systemPrompt,
        temperature: 0.2,
      );
      
      // 解析响应
      final lowercaseResponse = response.toLowerCase().trim();
      if (lowercaseResponse == "current") {
        return null; // 当前智能体适合回答
      } else if (lowercaseResponse.contains('xiaoai') && currentAgentType != AgentType.xiaoAi) {
        return await getAgentByType(AgentType.xiaoAi);
      } else if (lowercaseResponse.contains('xiaoke') && currentAgentType != AgentType.xiaoKe) {
        return await getAgentByType(AgentType.xiaoKe);
      } else if (lowercaseResponse.contains('laoke') && currentAgentType != AgentType.laoKe) {
        return await getAgentByType(AgentType.laoKe);
      } else if (lowercaseResponse.contains('suoer') && currentAgentType != AgentType.suoEr) {
        return await getAgentByType(AgentType.suoEr);
      }
    } catch (e) {
      print('LLM智能体切换判断失败: $e');
      // 失败时不切换智能体
    }
    
    // 如果LLM判断失败或判断为当前智能体适合回答，返回null
    return null;
  }

  @override
  Future<List<String>> generateDiagnosisQuestions(AgentType agentType) async {
    try {
      // 使用LLM生成针对性的诊断问题
      final systemPrompt = '''
你是索克生活APP中的${agentTypeToChineseName(agentType)}智能体。请生成4个针对用户的诊断性问题，用于了解用户的健康状况。
请根据你的专业领域生成这些问题：

- 小艾: 问诊类基础问题
- 老克: 中医理论相关的体质辨识问题
- 索儿: 生活习惯和健康行为相关问题
- 小克: 健康产品需求相关问题

直接列出四个问题，不要有编号或其他额外文字。保持问题简洁、专业且有针对性。
''';

      final response = await _llmManager.chat(
        message: "请生成${agentTypeToChineseName(agentType)}的4个诊断问题",
        systemPrompt: systemPrompt,
        temperature: 0.7,
      );
      
      // 解析响应为列表
      final questions = response
          .split('\n')
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .take(4)
          .toList();
      
      if (questions.length == 4) {
        return questions;
      }
    } catch (e) {
      print('LLM生成诊断问题失败: $e');
    }
    
    // 备用预设问题
    switch (agentType) {
      case AgentType.xiaoAi:
        // 问诊类问题
        return [
          '您最近的睡眠质量如何？',
          '有没有感到特别疲劳或乏力？',
          '胃口和消化状况怎么样？',
          '有没有特别容易出汗的情况？',
        ];
      case AgentType.laoKe:
        // 体质辨识问题
        return [
          '您平时怕冷还是怕热？',
          '您的舌头颜色偏淡还是偏红？',
          '您容易感到口干舌燥吗？',
          '您的大便是干燥还是稀溏？',
        ];
      case AgentType.suoEr:
        // 生活习惯问题
        return [
          '您平均每天睡几个小时？',
          '您的饮食规律吗？一天几餐？',
          '您每周运动几次？每次多长时间？',
          '您平时喝水量大概多少？',
        ];
      case AgentType.xiaoKe:
        // 产品需求问题
        return [
          '您关注哪些方面的健康问题？',
          '您目前正在使用什么保健产品吗？',
          '您喜欢什么味道的中药产品？',
          '您对中医理疗设备感兴趣吗？',
        ];
    }
  }

  @override
  Future<String> generateConversationSummary(String conversationId) async {
    // 获取会话消息
    final messages = await _agentRepository.getMessages(conversationId);
    
    try {
      // 使用LLM生成对话摘要
      // 准备消息历史
      final messagesText = messages.map((msg) {
        final roleStr = msg.messageType == MessageType.user ? "用户" : "智能体";
        return "$roleStr: ${msg.content}";
      }).join("\n");
      
      final systemPrompt = '''
你是索克生活APP中的对话摘要生成服务。你的任务是分析用户与智能体之间的对话内容，并生成一个简短的摘要。
摘要应当包含：
1. 用户关注的主要话题或问题
2. 对话的整体内容概述
3. 对话中提及的关键健康信息（如有）

请生成一句不超过30个字的简洁摘要。
''';

      final response = await _llmManager.chat(
        message: "请为以下对话生成摘要：\n$messagesText",
        systemPrompt: systemPrompt,
        temperature: 0.3,
      );
      
      return response.trim();
    } catch (e) {
      print('LLM生成对话摘要失败: $e');
      
      // 如果LLM生成失败，回退到简单摘要方法
      if (messages.length < 3) {
        return '这是一个新的对话，还没有太多内容。';
      }
      
      // 简单提取用户关注的主题
      final userMessages = messages
          .where((msg) => msg.messageType == MessageType.user)
          .map((msg) => msg.content.toLowerCase())
          .toList();
      
      // 关键词计数
      final keywordCount = <String, int>{
        '睡眠': 0,
        '饮食': 0,
        '运动': 0,
        '体质': 0,
        '中医': 0,
        '症状': 0,
        '产品': 0,
        '服务': 0,
      };
      
      for (final message in userMessages) {
        for (final keyword in keywordCount.keys) {
          if (message.contains(keyword)) {
            keywordCount[keyword] = (keywordCount[keyword] ?? 0) + 1;
          }
        }
      }
      
      // 找出最关注的主题
      final topKeywords = keywordCount.entries
          .where((entry) => entry.value > 0)
          .toList()
          ..sort((a, b) => b.value.compareTo(a.value));
      
      if (topKeywords.isEmpty) {
        return '这是一个一般性交流的对话。';
      }
      
      final mainTopic = topKeywords.first.key;
      return '这是一个关于$mainTopic的对话，共包含${messages.length}条消息。';
    }
  }

  @override
  Future<String> getHealthAdvice({
    required AgentType agentType,
    required String healthIssue,
  }) async {
    try {
      // 使用LLM生成健康建议
      final systemPrompt = '''
你是索克生活APP中的${agentTypeToChineseName(agentType)}智能体。请针对用户提出的健康问题，提供专业、安全且有帮助的建议。
作为${agentTypeToChineseName(agentType)}，你应该根据自己的专长领域回答：

- 小艾: 提供全面的指导和基础健康建议
- 老克: 提供基于中医理论的专业解读和建议
- 索儿: 提供生活方式和健康习惯的具体建议
- 小克: 提供适合的健康产品和服务推荐

请注意，你的建议不应替代专业医疗诊断。对于严重健康问题，应建议用户咨询医生。
回答应简洁明了，不超过150字。
''';

      final response = await _llmManager.chat(
        message: healthIssue,
        systemPrompt: systemPrompt,
        temperature: 0.7,
      );
      
      return response.trim();
    } catch (e) {
      print('LLM生成健康建议失败: $e');
      
      // 备用的预设健康建议
      final lowerIssue = healthIssue.toLowerCase();
      
      if (lowerIssue.contains('睡眠') || lowerIssue.contains('失眠')) {
        switch (agentType) {
          case AgentType.xiaoAi:
            return '从中医角度看，失眠可能与心脾两虚或肝火旺盛有关。建议您进行完整的体质辨识，以便提供更精准的建议。';
          case AgentType.laoKe:
            return '中医认为，失眠多与心、肝、脾关系密切。心主神明，肝主疏泄，脾主运化。建议从调节情志、饮食调养和作息规律三方面入手改善。';
          case AgentType.xiaoKe:
            return '对于失眠问题，可以考虑使用舒眠系列中药枕、安神茶饮或穴位贴敷产品。这些产品有助于改善睡眠质量，但最好先了解您的体质类型再选择。';
          case AgentType.suoEr:
            return '改善睡眠的生活习惯建议：固定作息时间，睡前1小时避免使用电子设备，卧室保持安静、黑暗、通风，睡前可做10分钟冥想放松，避免睡前摄入咖啡因和酒精。';
        }
      } else if (lowerIssue.contains('疲劳') || lowerIssue.contains('乏力')) {
        switch (agentType) {
          case AgentType.xiaoAi:
            return '疲劳乏力可能与多种因素有关，包括生活习惯、营养状况或潜在健康问题。建议您通过我们的体质测评了解更多，或咨询老克获取中医专业解析。';
          case AgentType.laoKe:
            return '中医视疲劳乏力多为气血不足、脾肾亏虚所致。气为血之帅，血为气之母，两者相互滋养。建议从补气养血、健脾益肾方面调理，配合适当活动和充足休息。';
          case AgentType.xiaoKe:
            return '针对疲劳乏力，推荐您尝试我们的气血双补系列产品，如人参黄芪茶、八珍糕或便携式穴位按摩器。结合您的具体体质，可提供更精准的产品推荐。';
          case AgentType.suoEr:
            return '缓解疲劳的生活建议：保证7-8小时优质睡眠，均衡饮食补充B族维生素，每天饮水2000ml，工作45分钟后休息5-10分钟，适量有氧运动提升心肺功能，可尝试午间短暂小憩。';
        }
      }
      
      // 通用回复
      switch (agentType) {
        case AgentType.xiaoAi:
          return '感谢您提出这个健康问题。为了给您提供更准确的建议，建议您完成我们的健康评估问卷，或与老克智能体深入探讨中医解析，或咨询索儿了解生活习惯调整方案。';
        case AgentType.laoKe:
          return '中医强调整体观念和辨证施治。您提到的情况需要结合望闻问切四诊进行全面分析。建议您通过我们的体质辨识功能，获得更有针对性的中医建议。';
        case AgentType.xiaoKe:
          return '索克生活提供多种适合不同体质的健康产品。建议您先完成体质测评，这样我能为您推荐最适合的产品组合，满足您的健康需求。';
        case AgentType.suoEr:
          return '健康的生活方式是预防疾病的基础。建议您保持规律作息，均衡饮食，适量运动，良好心态。结合您的具体情况，我可以为您定制更详细的健康生活方案。';
      }
    }
  }

  @override
  Future<String> getInteractionHistory(String userId, {int limit = 5}) async {
    try {
      // 获取用户最近的交互历史
      final interactions = await _agentRepository.getUserInteractions(userId, limit: limit);
      
      if (interactions.isEmpty) {
        return "用户没有历史交互记录";
      }
      
      // 格式化为文本
      return interactions.map((interaction) {
        final agentName = agentTypeToChineseName(interaction.agentType);
        final formattedTime = formatInteractionTime(interaction.timestamp);
        return "[$formattedTime] 与$agentName交流: ${interaction.topic}";
      }).join("\n");
    } catch (e) {
      print('获取交互历史失败: $e');
      return "无法获取历史交互记录";
    }
  }
  
  /// 将智能体类型转换为中文名称
  String agentTypeToChineseName(AgentType type) {
    switch (type) {
      case AgentType.xiaoAi:
        return '小艾';
      case AgentType.xiaoKe:
        return '小克';
      case AgentType.laoKe:
        return '老克';
      case AgentType.suoEr:
        return '索儿';
    }
  }
  
  /// 格式化交互时间
  String formatInteractionTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);
    
    if (difference.inDays == 0) {
      // 今天
      return '今天 ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      // 昨天
      return '昨天 ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays < 7) {
      // 本周
      final weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
      final weekday = weekdays[(time.weekday - 1) % 7];
      return '$weekday ${time.hour}:${time.minute.toString().padLeft(2, '0')}';
    } else {
      // 更早
      return '${time.month}月${time.day}日';
    }
  }
  
  /// 获取指定类型的智能体
  Future<Agent> getAgentByType(AgentType type) async {
    final agents = await _agentRepository.getAgents();
    return agents.firstWhere(
      (agent) => agent.type == type,
      orElse: () => throw Exception('找不到指定类型的智能体: $type'),
    );
  }
}