import 'package:equatable/equatable.dart';

abstract class LifeState extends Equatable {
  const LifeState();

  @override
  List<Object?> get props => [];
}

class LifeInitial extends LifeState {
  const LifeInitial();
}

class LifeLoading extends LifeState {
  const LifeLoading();
}

class LifeLoaded extends LifeState {
  final List<dynamic> data;
  
  const LifeLoaded(this.data);

  @override
  List<Object?> get props => [data];
}

class LifeError extends LifeState {
  final String message;
  
  const LifeError(this.message);

  @override
  List<Object?> get props => [message];
} 