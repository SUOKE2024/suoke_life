import 'package:bloc_test/bloc_test.dart';
import 'package:suoke_app/app/presentation/blocs/chat/chat_detail_bloc.dart';
import 'package:suoke_app/app/presentation/blocs/chat/chat_detail_event.dart';
import 'package:suoke_app/app/presentation/blocs/chat/chat_detail_state.dart';

class MockChatDetailBloc extends MockBloc<ChatDetailEvent, ChatDetailState> implements ChatDetailBloc {
  @override
  String get chatId => 'test-id';
} 