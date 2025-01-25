import 'package:equatable/equatable.dart';

abstract class ExploreEvent extends Equatable {
  const ExploreEvent();

  @override
  List<Object?> get props => [];
}

class LoadExploreEvent extends ExploreEvent {
  const LoadExploreEvent();
}

class RefreshExploreEvent extends ExploreEvent {
  const RefreshExploreEvent();
}

class SearchExploreEvent extends ExploreEvent {
  final String query;
  const SearchExploreEvent(this.query);

  @override
  List<Object?> get props => [query];
} 