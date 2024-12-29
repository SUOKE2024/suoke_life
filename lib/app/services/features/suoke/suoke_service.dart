import 'package:get/get.dart';
import '../../../data/models/chat_message.dart';
import '../../../data/models/user.dart';
import '../../../data/models/expert.dart';
import '../../../data/models/service.dart';
import '../../../data/models/health_survey.dart';
import '../../../data/models/topic.dart';
import '../../../data/models/health_advice.dart';

abstract class SuokeService {
  // 基础功能
  Future<void> init();
  Future<void> initializeServices();
  
  // 聊天相关
  Future<List<ChatMessage>> getMessages(String roomId);
  Future<void> sendMessage(String roomId, String content, String type);
  
  // 用户相关
  Future<User?> getCurrentUser();
  Future<void> registerUser(Map<String, dynamic> userData);
  Future<void> registerExpert(Map<String, dynamic> expertData);
  Future<List<Expert>> getExperts();
  
  // SUOKE服务
  Future<List<Service>> getHealthServices();
  Future<List<Service>> getAgriServices();
  Future<List<HealthSurvey>> getSurveys();
  Future<void> submitSurvey(HealthSurvey survey);
  
  // 探索功能
  Future<Map<String, dynamic>> getKnowledgeGraph(String topic);
  Future<Map<String, dynamic>> getGraphRAGAnalysis(String query);
  
  // 生活记录
  Future<Map<String, dynamic>> getUserProfile();
  Future<List<Map<String, dynamic>>> getHealthAdvice();
  Future<void> addLifeRecord(Map<String, dynamic> record);
  Future<List<Map<String, dynamic>>> getLifeRecords();
  
  // 管理功能
  Future<void> reviewExpert(String expertId, bool approved);
  Future<void> reviewService(String serviceId, bool approved);
  Future<void> reviewProduct(String productId, bool approved);
  Future<void> integrateAPI(Map<String, dynamic> apiConfig);
  
  // AI助手相关
  Future<void> initializeAIAssistants();
  Future<String> chatWithXiaoI(String message);
  Future<String> chatWithLaoKe(String message);
  Future<String> chatWithXiaoKe(String message);

  // 无障碍支持
  Future<void> enableAccessibility(Map<String, dynamic> config);
  Future<void> textToSpeech(String text);
  Future<String> speechToText();

  // 数据采集与分析
  Future<void> collectUserData(String type, Map<String, dynamic> data);
  Future<Map<String, dynamic>> analyzeUserBehavior();
  Future<Map<String, dynamic>> generateUserInsights();
} 