import 'package:equatable/equatable.dart';

abstract class LifeEvent extends Equatable {
  const LifeEvent();

  @override
  List<Object?> get props => [];
}

class LoadLifeEvent extends LifeEvent {
  const LoadLifeEvent();
}

class RefreshLifeEvent extends LifeEvent {
  const RefreshLifeEvent();
}

class UpdateLifeEvent extends LifeEvent {
  final String data;
  const UpdateLifeEvent(this.data);

  @override
  List<Object?> get props => [data];
} 