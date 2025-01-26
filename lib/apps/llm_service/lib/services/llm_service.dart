import 'dart:math';
import 'dart:async';
import 'dart:convert'; // 导入 json

import 'package:http/http.dart' as http; // 导入 http 包
import 'package:injectable/injectable.dart'; // 假设您使用 injectable
import 'package:suoke_life/core/config/app_config.dart';
import 'package:suoke_life/core/models/conversation_turn.dart'; // 导入 ConversationTurn 模型
import 'package:suoke_life/core/services/agent_memory_service.dart'; // 导入 AgentMemoryService
import 'package:suoke_life/core/network/knowledge_graph_client.dart'; // 导入 KnowledgeGraphClient
import 'package:suoke_life/core/services/health_profile_service.dart'; // 导入 HealthProfileService
import 'package:suoke_life/core/services/rag/context_compression_strategy.dart'; // 导入 ContextCompressionStrategy
import 'package:crypto/crypto.dart'; // 导入 crypto 包用于哈希
import 'package:suoke_life/core/services/rag/re_ranking_strategy.dart'; // 导入 ReRankingStrategy

enum QueryExpansionStrategy {
  none, // 不进行查询扩展
  synonym_replacement, // 同义词替换
  intent_recognition, // 意图识别
  // 可以根据需要添加更多策略
}

enum ContextCompressionType {
  no_compression,
  summary,
  keyword_extraction,
}

enum ReRankingStrategy {
  none, // 不进行重排序
  semantic_similarity, // 语义相似度模型
  context_relevance, // 上下文相关性模型
  // 可以根据需要添加更多策略
}

enum PromptStrategy {
  standard_rag, // 标准 RAG Prompt 策略
  chain_of_thought_rag, // Chain-of-Thought RAG Prompt 策略
  // 可以根据需要添加更多 Prompt 策略
}

@LazySingleton() // 使用 injectable 的 @LazySingleton 注解
class LLMService {
  final QueryExpansionStrategy queryExpansionStrategy; // 查询扩展策略配置
  final ContextCompressionType contextCompressionType; // 上下文压缩策略配置
  final ReRankingStrategy reRankingStrategy; // 重排序策略配置
  final double compressionRatio; // 压缩率
  final int keywordsNum; // 关键词提取数量
  final String summaryModelName; // 摘要模型名称
  final String reRankingModelName; // 重排序模型名称
  final PromptStrategy promptStrategy; // Prompt 策略
  final Map<String, dynamic> promptStrategyOptions; // Prompt 策略选项
  final AppConfig appConfig;
  final String defaultLocalDataRetentionPeriod; //  默认本地数据保留期限
  final AgentMemoryService _agentMemoryService; // 声明 AgentMemoryService
  final ContextCompressionStrategy
      _contextCompressionStrategy; // 声明 ContextCompressionStrategy
  final ReRankingStrategy _reRankingStrategy; // 声明 ReRankingStrategy

  @injectable // 使用 injectable 的 @injectable 注解，如果不是 injectable 请替换为您的 DI 方案
  LLMService({
    required this.queryExpansionStrategy, // 构造函数中需要传入查询扩展策略
    required this.contextCompressionType, // 上下文压缩策略配置
    required this.reRankingStrategy, // 重排序策略配置
    required this.promptStrategy, // Prompt 策略
    this.compressionRatio = 0.5, // 默认压缩率
    this.keywordsNum = 10, // 默认关键词提取数量
    this.summaryModelName = 'bart-large-cnn', // 默认摘要模型名称
    this.reRankingModelName =
        'sentence-transformers/all-mpnet-base-v2', // 默认重排序模型名称
    this.promptStrategyOptions = const {}, // 默认 Prompt 策略选项为空
    required this.appConfig,
    String? defaultLocalDataRetentionPeriod, //  默认本地数据保留期限
    this.defaultLocalDataRetentionPeriod = '30d', //  默认保留 30 天
    required AgentMemoryService
        agentMemoryService, // 构造函数中需要传入 AgentMemoryService
    required ContextCompressionStrategy
        contextCompressionStrategy, //  接收 ContextCompressionStrategy 实例
    required ReRankingStrategy reRankingStrategy, // 接收 ReRankingStrategy 实例
  })  : _agentMemoryService = agentMemoryService,
        _contextCompressionStrategy = contextCompressionStrategy,
        _reRankingStrategy = reRankingStrategy;

  // 查询扩展的占位符方法 (待实现)
  Future<String> _expandQueryWithSynonyms(String query) async {
    print('使用同义词扩展查询 (占位符), Query: $query'); // 添加日志
    // TODO: 在这里集成真实的同义词查询扩展逻辑
    //       例如：使用 WordNet, ConceptNet 等知识库，或者使用预训练的语言模型
    await Future.delayed(const Duration(seconds: 1)); // 模拟查询扩展延迟
    return '$query (同义词扩展)'; // 占位符扩展结果
  }

  // 意图识别的占位符方法 (待实现)
  Future<String> _expandQueryWithIntentRecognition(String query) async {
    print('使用意图识别扩展查询 (占位符), Query: $query'); // 添加日志
    // TODO: 在这里集成真实的意图识别逻辑
    //       例如：使用预训练的意图识别模型，或者使用规则和关键词匹配
    await Future.delayed(const Duration(seconds: 1)); // 模拟意图识别延迟
    return '$query (意图识别扩展)'; // 占位符扩展结果
  }

  // 上下文压缩的占位符方法 (待实现)
  String _compressContext(String context) {
    print('压缩上下文 (占位符), Context length: ${context.length}'); // 添加日志
    // TODO: 在这里集成真实的上下文压缩逻辑
    //       例如：关键词提取、摘要生成、信息重排序和过滤等
    //       可以根据 contextCompressionType 选择不同的压缩策略
    switch (contextCompressionType) {
      case ContextCompressionType.summary:
        // TODO: 实现摘要生成压缩策略
        print('使用摘要生成压缩策略, 模型名称: $summaryModelName');
        break;
      default:
        print('不进行上下文压缩');
    }
    return context.substring(
        0, min(100, context.length)); // 占位符压缩结果，截取前 100 个字符
  }

  // 上下文重排序的占位符方法 (待实现)
  Future<String> _reRankContext(String query, String context) async {
    print('重排序上下文 (占位符), Context length: ${context.length}'); // 添加日志
    // TODO: 在这里集成真实的上下文重排序逻辑
    //       例如：使用语义相似度模型或上下文相关性模型对检索到的上下文进行重排序
    //       可以根据 reRankingStrategy 选择不同的重排序策略
    switch (reRankingStrategy) {
      case ReRankingStrategy.semantic_similarity:
        // TODO: 使用语义相似度模型进行重排序
        print('使用语义相似度模型重排序, 模型名称: $reRankingModelName');
        break;
      case ReRankingStrategy.context_relevance:
        // TODO: 使用上下文相关性模型进行重排序
        print('使用上下文相关性模型重排序');
        break;
      default:
        print('不进行上下文重排序');
    }
    await Future.delayed(const Duration(seconds: 1)); // 模拟重排序延迟
    return context; // 占位符重排序结果，返回原始上下文
  }

  // 构建 Chain-of-Thought Prompt 的占位符方法 (待实现)
  String _buildCoTPrompt(String query, String context) {
    print('构建 Chain-of-Thought Prompt (占位符)'); // 添加日志
    // TODO: 在这里根据 promptStrategyOptions 构建真实的 Chain-of-Thought Prompt
    //       例如：从 promptStrategyOptions 中获取 CoT 示例，并将其拼接到 Prompt 中
    final cotPromptTemplate =
        promptStrategyOptions['cot_prompt_template'] as String? ??
            '请一步步思考，并给出最终答案。'; // 从配置中获取 CoT Prompt 模板，如果没有则使用默认模板
    final fewShotExamplesPath = promptStrategyOptions['few_shot_examples_path']
        as String?; // 从配置中获取 Few-shot 示例文件路径

    String fewShotExamples = '';
    if (fewShotExamplesPath != null) {
      // TODO: 从文件中读取 Few-shot 示例
      fewShotExamples = 'Few-shot 示例：[从 $fewShotExamplesPath 读取的示例]';
    }

    return '用户查询: $query\n检索到的上下文: $context\n$cotPromptTemplate\n$fewShotExamples'; // 占位符 Prompt
  }

  // 构建标准 Prompt 的占位符方法 (待实现)
  String _buildStandardPrompt(String query, String context) {
    print('构建标准 Prompt (占位符)'); // 添加日志
    // TODO: 在这里构建真实的标准 Prompt
    return '用户查询: $query\n检索到的上下文: $context\n请直接给出答案。'; // 占位符 Prompt
  }

  // 生成回复的占位符方法 (待实现)
  Future<String> _generateResponse({
    required String query,
    required String context,
    required PromptStrategy promptStrategy, // 添加 promptStrategy 参数
  }) async {
    print('生成回复 (占位符), Prompt Strategy: $promptStrategy'); // 添加日志
    // TODO: 在这里集成真实的 LLM 调用逻辑
    //       例如：调用 OpenAI API, Azure OpenAI API, 或其他 LLM API
    //       根据 promptStrategy 选择不同的 Prompt 构建方法
    String prompt = '';
    switch (promptStrategy) {
      case PromptStrategy.standard_rag:
        prompt = _buildStandardPrompt(query, context); // 构建标准 Prompt
        break;
      case PromptStrategy.chain_of_thought_rag:
        prompt = _buildCoTPrompt(query, context); // 构建 Chain-of-Thought Prompt
        break;
      default:
        prompt = _buildStandardPrompt(query, context); // 默认使用标准 Prompt
    }

    print('Prompt: $prompt'); // 打印 Prompt (用于调试)

    await Future.delayed(const Duration(seconds: 2)); // 模拟 LLM 调用延迟
    return 'AI 回复： 这是基于查询 "$query" 和上下文信息生成的回复。 [LLM 模型的实际回复内容]'; // 占位符回复
  }

  // 执行 RAG (Retrieval-Augmented Generation) 流程
  Future<String> _performRAG(
      String query, String userId, String agentId) async {
    print('执行 RAG 流程, Query: $query'); // 添加日志

    // 1. 查询扩展 (Query Expansion)
    String expandedQuery = query; // 默认不扩展，使用原始查询
    switch (queryExpansionStrategy) {
      case QueryExpansionStrategy.synonym_replacement:
        expandedQuery = await _expandQueryWithSynonyms(query); // 使用同义词扩展查询
        break;
      case QueryExpansionStrategy.intent_recognition:
        expandedQuery =
            await _expandQueryWithIntentRecognition(query); // 使用意图识别扩展查询
        break;
      default:
        print('不进行查询扩展');
    }
    print('扩展后的查询: $expandedQuery'); // 打印扩展后的查询

    // 2. 上下文检索 (Context Retrieval)
    // 从知识库检索上下文
    final retrievedContext = await _retrieveContextFromKnowledgeBase(
        userId: userId, query: expandedQuery);

    // 3. 上下文压缩 (Context Compression)
    String compressedContext =
        retrievedContext; // 默认不压缩，使用原始上下文 (这里仍然使用知识库上下文进行压缩，可以根据需要修改)

    switch (contextCompressionType) {
      case ContextCompressionType.summary:
        compressedContext = _compressContext(retrievedContext); // 执行上下文压缩
        break;
      default:
        print('不进行上下文压缩');
    }
    print(
        '压缩后的上下文 (前 100 字): ${compressedContext.substring(0, min(100, compressedContext.length))}...'); // 打印压缩后的上下文 (前 100 字)

    // 4. 上下文重排序 (Context Re-ranking)
    String reRankedContext = compressedContext; // 默认不重排序，使用压缩后的上下文
    switch (reRankingStrategy) {
      case ReRankingStrategy.semantic_similarity:
      case ReRankingStrategy.context_relevance:
        reRankedContext =
            await _reRankContext(query, compressedContext); // 执行上下文重排序
        break;
      default:
        print('不进行上下文重排序');
    }
    print(
        '重排序后的上下文 (前 100 字): ${reRankedContext.substring(0, min(100, reRankedContext.length))}...'); // 打印重排序后的上下文 (前 100 字)

    // 5. 生成回复 (Response Generation)
    // 使用 Prompt Strategy 和 LLM 生成最终回复
    return _generateResponse(
      query: expandedQuery,
      context: reRankedContext,
      promptStrategy: promptStrategy, // 传递 promptStrategy 参数
    ); // 使用重排序后的上下文
  }

  Future<String> _performKnowledgeGraphQuery(String query) async {
    print('执行知识图谱查询 (占位符), Query: $query'); // 添加日志
    // TODO: 在这里集成真实的知识图谱查询逻辑
    //       例如：调用知识图谱 API，并处理 API 响应
    await Future.delayed(const Duration(seconds: 1)); // 模拟知识图谱查询延迟
    return '知识图谱检索结果： 找到了关于 "$query" 的一些知识图谱信息，内容概要如下： [知识图谱检索结果]'; // 占位符知识图谱检索结果
  }

  // 获取健康画像上下文的占位符方法 (待实现)
  Future<String> _retrieveContextFromHealthProfile(String userId) async {
    print('获取健康画像上下文 (占位符), User ID: $userId'); // 添加日志
    // TODO: 在这里集成真实的健康画像 API 调用逻辑
    //       例如：调用健康画像 API，根据 userId 获取用户健康画像数据
    //       final healthProfileApiUrl = '${appConfig.healthProfileApiEndpoint}/$userId'; // 从配置中获取健康画像 API 端点
    //       final response = await http.get(Uri.parse(healthProfileApiUrl));
    //       if (response.statusCode == 200) {
    //         final jsonResponse = json.decode(response.body);
    //         final healthProfileContext = _parseHealthProfileResponse(jsonResponse); // 解析健康画像 API 响应
    //         return healthProfileContext;
    //       } else {
    //         return '健康画像检索失败';
    //       }
    await Future.delayed(const Duration(seconds: 1)); // 模拟健康画像检索延迟
    return '健康画像上下文： 这是用户的健康画像信息，可以用于个性化健康建议。 [健康画像信息]'; // 占位符健康画像上下文
  }

  // 解析健康画像 API 响应的占位符方法 (待实现)
  String _parseHealthProfileResponse(Map<String, dynamic> jsonResponse) {
    print('解析健康画像 API 响应 (占位符)'); // 添加日志
    // TODO: 在这里实现真实的健康画像 API 响应解析逻辑
    //       根据健康画像 API 返回的 JSON 格式，提取相关的健康画像信息
    //       并将其转换为 RAG 可以使用的文本上下文
    //       示例：提取用户年龄、性别、健康指标等信息
    //       final age = jsonResponse['age'];
    //       final gender = jsonResponse['gender'];
    //       return '用户年龄：$age\n用户性别：$gender'; // 将年龄和性别拼接成字符串
    return '解析后的健康画像上下文： [解析后的健康画像信息]'; // 占位符健康画像上下文
  }

  // 从知识库检索上下文 (融合知识图谱和健康画像)
  Future<String> _retrieveContextFromKnowledgeBase(
      {required String userId, required String query}) async {
    print('从知识库检索上下文 (占位符), Query: $query'); // 添加日志
    // TODO: 在这里集成真实的知识库检索逻辑，例如知识图谱查询
    //       示例：假设知识图谱 API 端点为 /api/knowledge_graph/query
    //       并接受 keywords 参数进行查询

    //  集成健康画像查询
    final healthProfileContext = await _retrieveContextFromHealthProfile(
        userId); //  调用 _retrieveContextFromHealthProfile 获取健康画像上下文
    print('健康画像上下文: $healthProfileContext'); // 打印健康画像上下文

    String knowledgeGraphContext = ''; // 初始化知识图谱上下文为空字符串
    //  知识图谱查询 (如果启用)
    if (appConfig.enableKnowledgeGraph) {
      //  从 AppConfig 中读取是否启用知识图谱
      print('执行知识图谱查询, Query: $query'); // 添加日志
      //  示例：假设知识图谱 API 端点为 /api/knowledge_graph/query
      //  并接受 keywords 参数进行查询
      //       final knowledgeGraphApiUrl = '${appConfig.knowledgeGraphApiEndpoint}/query?keywords=$query'; // 从配置中获取知识图谱 API 端点
      //       final response = await http.get(Uri.parse(knowledgeGraphApiUrl));
      //       if (response.statusCode == 200) {
      //         final jsonResponse = json.decode(response.body);
      //         knowledgeGraphContext = _parseKnowledgeGraphResponse(jsonResponse); // 解析知识图谱 API 响应
      //         print('知识图谱上下文: $knowledgeGraphContext'); // 打印知识图谱上下文
      //       } else {
      //         return '知识库检索失败';
      //       }
      knowledgeGraphContext = await _performKnowledgeGraphQuery(
          query); //  调用 _performKnowledgeGraphQuery 获取知识图谱上下文 (占位符方法)
    } else {
      print('知识图谱已禁用'); //  打印日志，提示知识图谱已禁用
    }

    //  融合知识图谱上下文和健康画像上下文
    final finalContext =
        '$knowledgeGraphContext\n\n$healthProfileContext'; //  简单拼接，可以根据需要调整融合策略

    await Future.delayed(const Duration(seconds: 1)); // 模拟知识库检索延迟
    return finalContext; //  返回融合后的上下文
  }

  // 获取文件内容描述的占位符方法 (待实现)
  Future<String> _getFileContentDescription(String filePath) async {
    print('获取文件内容描述 (占位符), File Path: $filePath'); // 添加日志
    // TODO: 在这里集成真实的文件内容提取和描述逻辑
    //       例如：根据文件类型 (txt, pdf, docx 等) 选择不同的文件解析库
    //       提取文件中的文本内容，并进行内容概要或描述
    //       可以使用第三方库，例如：pdf_text, docx_parser 等
    await Future.delayed(const Duration(seconds: 1)); // 模拟文件处理延迟
    return '文件内容描述： 这是用户上传的文件，文件路径为：$filePath，文件内容概要如下： [文件内容概要]'; // 占位符文件内容描述
  }

  // 图像描述的占位符方法 (待实现)
  Future<String> _getImageDescription(String imageUrl) async {
    print('获取图像描述 (占位符), Image URL: $imageUrl'); // 添加日志
    // TODO: 在这里集成真实的图像描述模型或服务
    //       例如：调用图像描述 API，或使用本地图像描述模型
    //       示例：使用 http 包下载图像，然后调用图像描述 API
    //       final response = await http.get(Uri.parse(imageUrl));
    //       if (response.statusCode == 200) {
    //         // 调用图像描述 API，传递图像数据 (response.bodyBytes)
    //         // ...
    //         return '图像的文本描述'; // 返回图像描述文本
    //       } else {
    //         return '无法获取图像描述';
    //       }
    await Future.delayed(const Duration(seconds: 1)); // 模拟网络请求延迟
    return '这是一张关于 [图像内容描述] 的图片'; // 占位符图像描述
  }

  // 网络搜索的占位符方法 (待实现)
  Future<String> _performWebSearch(String query) async {
    print('执行网络搜索 (占位符), Query: $query'); // 添加日志
    // TODO: 在这里集成真实的网络搜索 API 调用逻辑
    //       例如：使用 Google Custom Search API 或 Bing Web Search API
    //       示例：使用 Google Custom Search API
    //       final apiKey = appConfig.googleCustomSearchApiKey; // 从配置中获取 API 密钥
    //       final searchEngineId = appConfig.googleCustomSearchEngineId; // 从配置中获取搜索引擎 ID
    //       final apiUrl = 'https://www.googleapis.com/customsearch/v1'
    //           '?key=$apiKey&cx=$searchEngineId&q=$query';
    //       final response = await http.get(Uri.parse(apiUrl));
    //       if (response.statusCode == 200) {
    //         final jsonResponse = json.decode(response.body);
    //         final items = jsonResponse['items'];
    //         if (items != null && items is List) {
    //           final searchResults = items.map((item) => item['snippet'] as String).toList(); // 提取搜索结果摘要
    //           return searchResults.join('\n'); // 将搜索结果摘要拼接成字符串
    //         } else {
    //           return '未找到网络搜索结果';
    //         }
    //       } else {
    //         return '网络搜索失败';
    //       }
    await Future.delayed(const Duration(seconds: 2)); // 模拟网络搜索延迟
    return '网络搜索结果： 找到了关于 "$query" 的一些网络信息，内容概要如下： [网络搜索结果摘要]'; // 占位符网络搜索结果
  }

  // 主消息处理方法
  Future<String> sendMessage({
    // 修改 sendMessage 方法，使用命名参数
    required String userId,
    required String agentId,
    String? textMessage,
    String? imageUrl,
    String? voiceData,
    String? videoUrl,
    List<String> filePaths = const [], // 新增：文件路径列表，默认为空列表
  }) async {
    String query = textMessage ?? ''; // 优先使用文本消息作为查询基础
    if (imageUrl != null) {
      final imageDescription = await _getImageDescription(imageUrl); // 获取图像描述
      query += ' 图片描述: $imageDescription'; // 将图像描述添加到查询中，进行融合
    } else if (voiceData != null) {
      // TODO: 添加语音转文本逻辑，并将转换后的文本添加到 query
    } else if (videoUrl != null) {
      // TODO: 添加视频处理逻辑，提取视频信息并添加到 query
    }
    if (filePaths.isNotEmpty) {
      for (final filePath in filePaths) {
        query +=
            '\n文件内容描述: ${await _getFileContentDescription(filePath)}'; // 获取文件内容描述并添加到查询
      }
    }

    if (query.isEmpty) query = '用户输入了多模态信息'; // 如果最终查询为空，设置一个默认查询

    // 执行 RAG 流程，获取 AI 回复
    final aiResponse = await _performRAG(query, userId, agentId);

    // 保存用户消息到 Agent 内存
    await _agentMemoryService.saveConversationTurn(ConversationTurn(
      userId: userId,
      agentId: agentId,
      turnIndex: 1,
      role: 'user',
      text: query,
      timestamp: DateTime.now(),
    ));

    // 保存 AI 回复到 Agent 内存
    await _agentMemoryService.saveConversationTurn(ConversationTurn(
      userId: userId,
      agentId: agentId,
      turnIndex: 2,
      role: 'agent',
      text: aiResponse,
      timestamp: DateTime.now(),
    ));

    // TODO:  用户数据上传到系统后台 (示例 - 占位符)
    if (appConfig.enableDataContribution) {
      //  从 AppConfig 中读取是否启用数据贡献
      print('准备上传用户数据到系统后台 (匿名化处理)'); //  添加日志
      final anonymizedUserData = _anonymizeUserDataForUpload({
        'conversationHistory':
            await _agentMemoryService.getConversationHistory(userId, agentId),
        'userPreference': await _agentMemoryService.getUserPreference(userId),
        //  ... 其他需要上传的用户数据 ...
      });
      _uploadUserDataToBackend(
          anonymizedUserData); //  调用 _uploadUserDataToBackend 上传匿名化数据 (占位符方法)
    }

    return aiResponse;
  }

  // 匿名化用户数据的占位符方法 (待实现)
  Map<String, dynamic> _anonymizeUserDataForUpload(
      Map<String, dynamic> userData) {
    print('匿名化用户数据 (占位符)'); //  添加日志
    final anonymizedData = Map<String, dynamic>.from(userData); //  创建数据副本

    // 1. 用户 ID 哈希
    final userId = anonymizedData['userPreference']?.userId;
    if (userId != null) {
      final hashedUserId =
          sha256.convert(utf8.encode(userId)).toString(); // SHA256 哈希
      anonymizedData['userId'] = hashedUserId; //  替换为哈希后的用户 ID
      anonymizedData.remove('userPreference'); //  移除原始 userPreference，避免泄露用户 ID
    } else {
      anonymizedData['userId'] =
          'anonymous_user'; //  如果用户 ID 为空，使用 anonymous_user
      anonymizedData.remove('userPreference');
    }

    // 2. 对话历史匿名化 (移除对话文本中的个人信息)
    if (anonymizedData['conversationHistory'] is List) {
      anonymizedData['conversationHistory'] =
          (anonymizedData['conversationHistory'] as List).map((turn) {
        if (turn is ConversationTurn) {
          String? anonymizedText = turn.text;
          if (anonymizedText != null) {
            anonymizedText = _removePersonalInfo(anonymizedText); //  移除个人信息
          }
          return ConversationTurn(
            //  创建新的 ConversationTurn 对象，保持数据结构
            userId: anonymizedData['userId'] as String? ??
                'anonymous_user', //  使用匿名化后的用户 ID
            agentId: turn.agentId,
            turnIndex: turn.turnIndex,
            role: turn.role,
            text: anonymizedText, //  使用匿名化后的文本
            timestamp: turn.timestamp,
          );
        }
        return turn; //  如果不是 ConversationTurn 对象，则直接返回
      }).toList();
    }

    return anonymizedData; //  返回匿名化后的数据
  }

  // 上传用户数据到系统后台的占位符方法 (待实现)
  Future<void> _uploadUserDataToBackend(
      Map<String, dynamic> anonymizedUserData) async {
    print('上传匿名化用户数据到系统后台 (占位符)'); //  添加日志
    final dataContributionApiEndpoint =
        appConfig.dataContributionApiEndpoint; //  从 AppConfig 获取 API 端点
    if (dataContributionApiEndpoint.isEmpty) {
      print('数据贡献 API 端点未配置，取消上传'); //  添加日志
      return;
    }

    try {
      final response = await http.post(
        Uri.parse(dataContributionApiEndpoint),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(anonymizedUserData), //  将匿名化数据转换为 JSON 字符串
      );

      if (response.statusCode == 200) {
        print('匿名化用户数据上传成功，状态码: ${response.statusCode}'); //  添加日志
      } else {
        print('匿名化用户数据上传失败，状态码: ${response.statusCode}'); //  添加日志
        print('Response body: ${response.body}'); //  打印响应 body，方便调试
        // TODO:  可以根据需要添加重试逻辑
      }
    } catch (e) {
      print('上传用户数据到系统后台发生异常: $e'); //  添加错误日志
      // TODO:  可以根据需要添加异常处理和重试逻辑
    } finally {
      await Future.delayed(const Duration(seconds: 2)); //  模拟上传延迟 (实际上传不需要延迟)
      print('匿名化用户数据上传流程结束'); //  添加日志
    }
  }

  // 移除个人信息的简单占位符方法 (待完善)
  String _removePersonalInfo(String text) {
    // TODO:  使用更完善的个人信息移除逻辑，例如使用正则表达式或 NER 模型
    //       这里只是一个简单的示例，将文本中的 "姓名"、"电话号码"、"邮箱" 替换为 "[removed]"
    return text.replaceAll(
        RegExp(r'(姓名|电话号码|邮箱)', caseSensitive: false), '[removed]');
  }
}
