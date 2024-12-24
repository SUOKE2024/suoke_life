import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:suoke_app/app/services/ai/ai_service.dart';
import 'package:suoke_app/app/services/doubao_service.dart';
import '../../helpers/test_helper.dart';

@GenerateMocks([DouBaoService])
import 'ai_service_test.mocks.dart';

void main() {
  late AiService aiService;
  late MockDouBaoService mockDouBaoService;

  setUpAll(() {
    TestHelper.setupTest();
  });

  setUp(() {
    mockDouBaoService = MockDouBaoService();
    aiService = AiService(douBaoService: mockDouBaoService);
  });

  test('chat should throw exception when chat fails', () async {
    const message = 'test message';
    const model = 'test_model';

    when(mockDouBaoService.chat(message, model))
        .thenThrow(Exception('Chat failed'));

    expect(() => aiService.chat(message, model: model), throwsException);
    verify(mockDouBaoService.chat(message, model)).called(1);
  });

  tearDown(() {
    reset(mockDouBaoService);
  });

  tearDownAll(() {
    TestHelper.clearTest();
  });
} 