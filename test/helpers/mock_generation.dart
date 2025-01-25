import 'package:mockito/annotations.dart';
import 'package:suoke_life_app_app_app/features/home/services/chat_service.dart';
import 'package:suoke_life_app_app_app/features/home/services/ai_service.dart';
import 'package:suoke_life_app_app_app/features/home/services/data_sync_service.dart';

@GenerateNiceMocks([
  MockSpec<ChatService>(),
  MockSpec<AIService>(),
  MockSpec<DataSyncService>(),
])
import 'package:mockito/annotations.dart';
import 'package:suoke_life_app_app_app/features/home/services/chat_service.dart';
import 'package:suoke_life_app_app_app/features/home/services/ai_service.dart';
import 'package:suoke_life_app_app_app/features/home/services/data_sync_service.dart';

@GenerateMocks([
  ChatService,
  AIService,
  DataSyncService,
])
part 'mock_generation.mocks.dart';
