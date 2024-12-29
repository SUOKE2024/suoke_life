import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/core/services/network/network_service.dart';
import 'package:suoke_app/app/services/features/ai/assistants/xiaoi_service.dart';

import 'ai_service_test.mocks.dart';

@GenerateMocks([NetworkService])
void main() {
  late XiaoiService xiaoiService;
  late MockNetworkService mockNetwork;

  setUp(() {
    mockNetwork = MockNetworkService();
    xiaoiService = XiaoiService(mockNetwork);
  });

  group('XiaoiService', () {
    test('should send chat message and get response', () async {
      // arrange
      final testMessage = 'Hello';
      final testResponse = {'reply': 'Hi there!'};
      
      when(mockNetwork.post(
        any,
        data: anyNamed('data'),
      )).thenAnswer((_) async => testResponse);

      // act
      final result = await xiaoiService.chat(testMessage);

      // assert
      expect(result, equals('Hi there!'));
      verify(mockNetwork.post(
        'https://api.xiaoi.com/chat',
        data: {'message': testMessage},
      )).called(1);
    });

    test('should handle error when chat fails', () async {
      // arrange
      final testMessage = 'Hello';
      
      when(mockNetwork.post(
        any,
        data: anyNamed('data'),
      )).thenThrow(Exception('Network error'));

      // act & assert
      expect(
        () => xiaoiService.chat(testMessage),
        throwsException,
      );
    });
  });
} 