class SendMessageUseCase implements UseCase<void, SendMessageParams> {
  final ChatRepository repository;
  final NetworkInfo networkInfo;
  
  Future<Either<Failure, void>> call(SendMessageParams params) async {
    if (await networkInfo.isConnected) {
      try {
        await repository.sendMessage(params.message);
        return const Right(null);
      } catch (e) {
        return Left(ServerFailure());
      }
    } else {
      return Left(NetworkFailure());
    }
  }
} 