import 'package:flutter_bloc/flutter_bloc.dart';
import 'life_event.dart';
import 'life_state.dart';

class LifeBloc extends Bloc<LifeEvent, LifeState> {
  LifeBloc() : super(const LifeInitial()) {
    on<LoadLifeEvent>(_onLoadLife);
    on<RefreshLifeEvent>(_onRefreshLife);
    on<UpdateLifeEvent>(_onUpdateLife);
  }

  Future<void> _onLoadLife(LoadLifeEvent event, Emitter<LifeState> emit) async {
    emit(const LifeLoading());
    try {
      await Future.delayed(const Duration(seconds: 1)); // 模拟加载
      emit(const LifeLoaded([]));
    } catch (e) {
      emit(LifeError(e.toString()));
    }
  }

  Future<void> _onRefreshLife(
      RefreshLifeEvent event, Emitter<LifeState> emit) async {
    try {
      await Future.delayed(const Duration(seconds: 1)); // 模拟刷新
      emit(const LifeLoaded([]));
    } catch (e) {
      emit(LifeError(e.toString()));
    }
  }

  Future<void> _onUpdateLife(
      UpdateLifeEvent event, Emitter<LifeState> emit) async {
    if (state is LifeLoaded) {
      final currentData = (state as LifeLoaded).data;
      emit(LifeLoaded([...currentData, event.data]));
    }
  }
}
