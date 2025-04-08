import 'package:dartz/dartz.dart';
import 'package:equatable/equatable.dart';
import 'package:suoke_life/core/error/failures.dart';
import 'package:suoke_life/core/usecases/usecase.dart';
import 'package:suoke_life/domain/repositories/laoke_repository.dart';

/// 文字转语音用例
class TextToSpeech implements UseCase<String, TextToSpeechParams> {
  final LaokeRepository repository;

  TextToSpeech(this.repository);

  @override
  Future<Either<Failure, String>> call(TextToSpeechParams params) {
    return repository.textToSpeech(
      params.text,
      voiceId: params.voiceId,
      options: params.options,
    );
  }
}

/// 文字转语音参数
class TextToSpeechParams extends Equatable {
  final String text;
  final String? voiceId;
  final Map<String, dynamic>? options;

  const TextToSpeechParams({
    required this.text,
    this.voiceId,
    this.options,
  });

  @override
  List<Object?> get props => [text, voiceId, options];
} 