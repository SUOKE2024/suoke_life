class BaseRepositoryImpl<T> implements BaseRepository<T> {
  final RemoteDataSource remoteDataSource;
  final LocalDataSource localDataSource;
  final NetworkInfo networkInfo;
  
  Future<Either<Failure, T>> get(String id) async {
    if (await networkInfo.isConnected) {
      try {
        final remoteData = await remoteDataSource.get(id);
        await localDataSource.cache(remoteData);
        return Right(remoteData);
      } catch (e) {
        final localData = await localDataSource.get(id);
        return localData != null ? Right(localData) : Left(ServerFailure());
      }
    } else {
      final localData = await localDataSource.get(id);
      return localData != null ? Right(localData) : Left(NetworkFailure());
    }
  }
} 