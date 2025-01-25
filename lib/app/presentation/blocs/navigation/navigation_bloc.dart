import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:injectable/injectable.dart';
import 'navigation_event.dart';
import 'navigation_state.dart';

@injectable
class NavigationBloc extends Bloc<NavigationEvent, NavigationState> {
  NavigationBloc() : super(const NavigationInitial()) {
    on<NavigationEvent>((event, emit) {
      if (state is! NavigationLoaded) {
        emit(const NavigationLoaded());
        return;
      }

      final currentState = state as NavigationLoaded;

      if (event is NavigationTabChanged) {
        emit(currentState.copyWith(currentTab: event.index));
      } else if (event is NavigationPushRoute) {
        final newHistory = List<String>.from(currentState.history)
          ..add(event.route);
        emit(currentState.copyWith(
          currentRoute: event.route,
          history: newHistory,
        ));
      } else if (event is NavigationPopRoute) {
        if (currentState.history.isEmpty) return;
        
        final newHistory = List<String>.from(currentState.history)..removeLast();
        final previousRoute = newHistory.isEmpty 
            ? '/' 
            : newHistory.last;
            
        emit(currentState.copyWith(
          currentRoute: previousRoute,
          history: newHistory,
        ));
      }
    });
  }
} 