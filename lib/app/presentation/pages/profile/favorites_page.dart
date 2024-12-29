import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../controllers/profile/favorites_controller.dart';

class FavoritesPage extends GetView<FavoritesController> {
  const FavoritesPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('我的收藏'),
          bottom: const TabBar(
            tabs: [
              Tab(text: '服务'),
              Tab(text: '话题'),
              Tab(text: '文章'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildServiceList(),
            _buildTopicList(),
            _buildArticleList(),
          ],
        ),
      ),
    );
  }

  Widget _buildServiceList() {
    return Obx(() {
      if (controller.isLoadingServices.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.services.length,
        itemBuilder: (context, index) {
          final service = controller.services[index];
          return ListTile(
            leading: Icon(service.icon),
            title: Text(service.title),
            subtitle: Text(service.description),
            trailing: IconButton(
              icon: const Icon(Icons.favorite, color: Colors.red),
              onPressed: () => controller.unfavoriteService(service),
            ),
            onTap: () => controller.openService(service),
          );
        },
      );
    });
  }

  Widget _buildTopicList() {
    return Obx(() {
      if (controller.isLoadingTopics.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.topics.length,
        itemBuilder: (context, index) {
          final topic = controller.topics[index];
          return ListTile(
            leading: topic.imageUrl != null
                ? Image.network(
                    topic.imageUrl!,
                    width: 40,
                    height: 40,
                    fit: BoxFit.cover,
                  )
                : const Icon(Icons.topic),
            title: Text(topic.title),
            subtitle: Text(topic.description),
            trailing: IconButton(
              icon: const Icon(Icons.favorite, color: Colors.red),
              onPressed: () => controller.unfavoriteTopic(topic),
            ),
            onTap: () => controller.openTopic(topic),
          );
        },
      );
    });
  }

  Widget _buildArticleList() {
    return Obx(() {
      if (controller.isLoadingArticles.value) {
        return const Center(child: CircularProgressIndicator());
      }

      return ListView.builder(
        itemCount: controller.articles.length,
        itemBuilder: (context, index) {
          final article = controller.articles[index];
          return ListTile(
            leading: article.imageUrl != null
                ? Image.network(
                    article.imageUrl!,
                    width: 40,
                    height: 40,
                    fit: BoxFit.cover,
                  )
                : const Icon(Icons.article),
            title: Text(article.title),
            subtitle: Text(article.summary),
            trailing: IconButton(
              icon: const Icon(Icons.favorite, color: Colors.red),
              onPressed: () => controller.unfavoriteArticle(article),
            ),
            onTap: () => controller.openArticle(article),
          );
        },
      );
    });
  }
} 