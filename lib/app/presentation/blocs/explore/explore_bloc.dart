import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../domain/repositories/explore_repository.dart';
import 'explore_event.dart';
import 'explore_state.dart';

class ExploreBloc extends Bloc<ExploreEvent, ExploreState> {
  final ExploreRepository exploreRepository;

  ExploreBloc({required this.exploreRepository}) : super(ExploreInitial()) {
    on<LoadExploreEvent>(_onLoadExplore);
    on<RefreshExploreEvent>(_onRefreshExplore);
    on<SearchExploreEvent>(_onSearchExplore);
  }

  Future<void> _onLoadExplore(LoadExploreEvent event, Emitter<ExploreState> emit) async {
    emit(ExploreLoading());
    try {
      final items = await exploreRepository.getExploreItems();
      emit(ExploreLoaded(items));
    } catch (e) {
      emit(ExploreError(e.toString()));
    }
  }

  Future<void> _onRefreshExplore(RefreshExploreEvent event, Emitter<ExploreState> emit) async {
    try {
      final items = await exploreRepository.getExploreItems();
      emit(ExploreLoaded(items));
    } catch (e) {
      emit(ExploreError(e.toString()));
    }
  }

  Future<void> _onSearchExplore(SearchExploreEvent event, Emitter<ExploreState> emit) async {
    emit(ExploreLoading());
    try {
      final items = await exploreRepository.searchExploreItems(event.query);
      emit(ExploreLoaded(items));
    } catch (e) {
      emit(ExploreError(e.toString()));
    }
  }
} 