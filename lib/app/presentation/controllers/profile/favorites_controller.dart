import 'package:get/get.dart';
import '../../../services/features/suoke/suoke_service.dart';
import '../../../data/models/service.dart';
import '../../../data/models/topic.dart';
import '../../../data/models/article.dart';

class FavoritesController extends GetxController {
  final SuokeService suokeService;
  
  final isLoadingServices = false.obs;
  final isLoadingTopics = false.obs;
  final isLoadingArticles = false.obs;
  
  final services = <Service>[].obs;
  final topics = <Topic>[].obs;
  final articles = <Article>[].obs;

  FavoritesController(this.suokeService);

  @override
  void onInit() {
    super.onInit();
    loadAllFavorites();
  }

  Future<void> loadAllFavorites() async {
    await Future.wait([
      loadFavoriteServices(),
      loadFavoriteTopics(),
      loadFavoriteArticles(),
    ]);
  }

  Future<void> loadFavoriteServices() async {
    try {
      isLoadingServices.value = true;
      final result = await suokeService.getFavoriteServices();
      services.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载收藏服务失败');
    } finally {
      isLoadingServices.value = false;
    }
  }

  Future<void> loadFavoriteTopics() async {
    try {
      isLoadingTopics.value = true;
      final result = await suokeService.getFavoriteTopics();
      topics.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载收藏话题失败');
    } finally {
      isLoadingTopics.value = false;
    }
  }

  Future<void> loadFavoriteArticles() async {
    try {
      isLoadingArticles.value = true;
      final result = await suokeService.getFavoriteArticles();
      articles.value = result;
    } catch (e) {
      Get.snackbar('错误', '加载收藏文章失败');
    } finally {
      isLoadingArticles.value = false;
    }
  }

  Future<void> unfavoriteService(Service service) async {
    try {
      await suokeService.unfavoriteService(service.id);
      services.remove(service);
      Get.snackbar('成功', '已取消收藏');
    } catch (e) {
      Get.snackbar('错误', '取消收藏失败');
    }
  }

  Future<void> unfavoriteTopic(Topic topic) async {
    try {
      await suokeService.unfavoriteTopic(topic.id);
      topics.remove(topic);
      Get.snackbar('成功', '已取消收藏');
    } catch (e) {
      Get.snackbar('错误', '取消收藏失败');
    }
  }

  Future<void> unfavoriteArticle(Article article) async {
    try {
      await suokeService.unfavoriteArticle(article.id);
      articles.remove(article);
      Get.snackbar('成功', '已取消收藏');
    } catch (e) {
      Get.snackbar('错误', '取消收藏失败');
    }
  }

  void openService(Service service) {
    Get.toNamed('/suoke/service/${service.id}', arguments: service);
  }

  void openTopic(Topic topic) {
    Get.toNamed('/explore/topic/${topic.id}', arguments: topic);
  }

  void openArticle(Article article) {
    Get.toNamed('/explore/article/${article.id}', arguments: article);
  }
} 