import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:suoke_app/app/core/network/network_service.dart';
import 'package:suoke_app/app/data/services/ai_service_impl.dart';
import 'package:suoke_app/app/domain/services/ai_service.dart';

class MockNetworkService extends Mock implements NetworkService {}

void main() {
  late AIService aiService;
  late MockNetworkService mockNetwork;

  setUp(() {
    mockNetwork = MockNetworkService();
    aiService = AIServiceImpl(mockNetwork);
  });

  test('should send message to AI and get response', () async {
    // Arrange
    const message = 'Hi';
    const response = {'response': 'Hello!'};
    
    when(() => mockNetwork.post(
      any(),
      any(),
    )).thenAnswer((_) async => response);

    // Act
    final result = await aiService.sendMessage(message);

    // Assert
    expect(result, response['response']);
    verify(() => mockNetwork.post(
      any(),
      any(),
    )).called(1);
  });
} 