import 'package:equatable/equatable.dart';
import '../../../domain/models/explore_item.dart';

abstract class ExploreState extends Equatable {
  const ExploreState();

  @override
  List<Object?> get props => [];
}

class ExploreInitial extends ExploreState {}

class ExploreLoading extends ExploreState {}

class ExploreLoaded extends ExploreState {
  final List<ExploreItem> items;
  
  const ExploreLoaded(this.items);

  @override
  List<Object?> get props => [items];
}

class ExploreError extends ExploreState {
  final String message;
  
  const ExploreError(this.message);

  @override
  List<Object?> get props => [message];
} 