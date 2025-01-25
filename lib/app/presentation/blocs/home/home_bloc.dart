import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/chat_repository.dart';
import 'home_event.dart';
import 'home_state.dart';

class HomeBloc extends Bloc<HomeEvent, HomeState> {
  final ChatRepository chatRepository;

  HomeBloc({required this.chatRepository}) : super(HomeInitial()) {
    on<LoadHomeEvent>(_onLoadHome);
    on<RefreshHomeEvent>(_onRefreshHome);
    on<SearchHomeEvent>(_onSearchHome);
  }

  Future<void> _onLoadHome(LoadHomeEvent event, Emitter<HomeState> emit) async {
    emit(HomeLoading());
    try {
      final chats = await chatRepository.getChats();
      emit(HomeLoaded(chats));
    } catch (e) {
      emit(HomeError(e.toString()));
    }
  }

  Future<void> _onRefreshHome(RefreshHomeEvent event, Emitter<HomeState> emit) async {
    try {
      final chats = await chatRepository.getChats();
      emit(HomeLoaded(chats));
    } catch (e) {
      emit(HomeError(e.toString()));
    }
  }

  Future<void> _onSearchHome(SearchHomeEvent event, Emitter<HomeState> emit) async {
    emit(HomeLoading());
    try {
      final chats = await chatRepository.searchChats(event.query);
      emit(HomeLoaded(chats));
    } catch (e) {
      emit(HomeError(e.toString()));
    }
  }
} 