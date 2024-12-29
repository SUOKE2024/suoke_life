import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';

@injectable
class HomeBloc extends Bloc<HomeEvent, HomeState> {
  final SuokeService _suokeService;

  HomeBloc(this._suokeService) : super(HomeInitial()) {
    on<InitializeHome>(_onInitialize);
    on<ChangePage>(_onChangePage);
  }

  Future<void> _onInitialize(
    InitializeHome event,
    Emitter<HomeState> emit,
  ) async {
    try {
      emit(HomeLoading());
      await _suokeService.init();
      final user = await _suokeService.getCurrentUser();
      
      if (user == null) {
        emit(HomeUnauthorized());
      } else {
        emit(HomeLoaded(user: user));
      }
    } catch (e) {
      emit(HomeError(message: e.toString()));
    }
  }

  void _onChangePage(
    ChangePage event,
    Emitter<HomeState> emit,
  ) {
    if (state is HomeLoaded) {
      emit((state as HomeLoaded).copyWith(currentPage: event.page));
    }
  }
} 