import 'package:equatable/equatable.dart';

abstract class HomeEvent extends Equatable {
  const HomeEvent();

  @override
  List<Object?> get props => [];
}

class LoadHomeEvent extends HomeEvent {
  const LoadHomeEvent();
}

class RefreshHomeEvent extends HomeEvent {
  const RefreshHomeEvent();
}

class SearchHomeEvent extends HomeEvent {
  final String query;
  const SearchHomeEvent(this.query);

  @override
  List<Object?> get props => [query];
} 