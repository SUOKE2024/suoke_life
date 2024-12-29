import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/services/features/suoke/suoke_service.dart';

class MockSuokeService extends Mock implements SuokeService {
  @override
  Future<Map<String, dynamic>> getUserProfile() async {
    return {
      'id': 'test_id',
      'name': 'Test User',
      'avatar': 'test_avatar.png',
      'healthScore': 85,
    };
  }

  @override
  Future<List<Map<String, dynamic>>> getHealthAdvice() async {
    return [
      {
        'id': '1',
        'title': 'Test Advice',
        'content': 'Test Content',
        'type': 'health',
        'created_at': DateTime.now().millisecondsSinceEpoch,
      }
    ];
  }

  @override
  Future<List<Map<String, dynamic>>> getLifeRecords() async {
    return [
      {
        'id': '1',
        'title': 'Test Record',
        'content': 'Test Content',
        'type': 'daily',
        'created_at': DateTime.now().millisecondsSinceEpoch,
      }
    ];
  }

  @override
  Future<void> init() async {
    // 初始化测试数据
    await Future.delayed(Duration.zero);
  }
} 