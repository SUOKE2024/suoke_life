import 'package:equatable/equatable.dart';
import '../../../domain/models/chat_info.dart';

abstract class HomeState extends Equatable {
  const HomeState();

  @override
  List<Object?> get props => [];
}

class HomeInitial extends HomeState {}

class HomeLoading extends HomeState {}

class HomeLoaded extends HomeState {
  final List<ChatInfo> chats;
  
  const HomeLoaded(this.chats);

  @override
  List<Object?> get props => [chats];
}

class HomeError extends HomeState {
  final String message;
  
  const HomeError(this.message);

  @override
  List<Object?> get props => [message];
} 