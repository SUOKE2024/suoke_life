import 'package:flutter/material.dart';

class CommunityPage extends StatefulWidget {
  const CommunityPage({super.key});

  @override
  State<CommunityPage> createState() => _CommunityPageState();
}

class _CommunityPageState extends State<CommunityPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康社区'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () {
              _showPostOptions(context);
            },
          ),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(96),
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: SearchBar(
                  controller: _searchController,
                  hintText: '搜索健康话题、经验分享',
                  leading: const Icon(Icons.search),
                  padding: const MaterialStatePropertyAll(
                    EdgeInsets.symmetric(horizontal: 16.0),
                  ),
                  onTap: () {
                    // TODO: 实现搜索功能
                  },
                ),
              ),
              TabBar(
                controller: _tabController,
                isScrollable: true,
                tabs: const [
                  Tab(text: '推荐'),
                  Tab(text: '健康话题'),
                  Tab(text: '经验分享'),
                  Tab(text: '专家观点'),
                ],
              ),
            ],
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildRecommendedTab(),
          _buildTopicsTab(),
          _buildExperienceTab(),
          _buildExpertTab(),
        ],
      ),
    );
  }

  Widget _buildRecommendedTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 10,
      itemBuilder: (context, index) {
        return _buildPostCard(
          title: '健康生活小技巧 #${index + 1}',
          author: '健康达人',
          content: '保持健康的生活方式对于我们的身心都非常重要...',
          likes: 128,
          comments: 32,
          imageUrl: 'https://picsum.photos/seed/$index/300/200',
        );
      },
    );
  }

  Widget _buildTopicsTab() {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
        childAspectRatio: 1.5,
      ),
      itemCount: 10,
      itemBuilder: (context, index) {
        return _buildTopicCard(
          title: '# 健康生活话题${index + 1}',
          participants: 1234,
          posts: 567,
          imageUrl: 'https://picsum.photos/seed/topic$index/300/200',
        );
      },
    );
  }

  Widget _buildExperienceTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 10,
      itemBuilder: (context, index) {
        return _buildExperienceCard(
          title: '我的健康生活经验分享',
          author: '生活达人',
          content: '通过调整作息时间和饮食习惯，我成功改善了...',
          likes: 256,
          comments: 64,
          imageUrls: [
            'https://picsum.photos/seed/exp${index}1/300/200',
            'https://picsum.photos/seed/exp${index}2/300/200',
            'https://picsum.photos/seed/exp${index}3/300/200',
          ],
        );
      },
    );
  }

  Widget _buildExpertTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 10,
      itemBuilder: (context, index) {
        return _buildExpertCard(
          name: '张医生',
          title: '主任医师',
          hospital: '某三甲医院',
          content: '关于保持健康的专业建议...',
          likes: 512,
          comments: 128,
          avatarUrl: 'https://picsum.photos/seed/expert$index/100/100',
        );
      },
    );
  }

  Widget _buildPostCard({
    required String title,
    required String author,
    required String content,
    required int likes,
    required int comments,
    required String imageUrl,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.person),
            ),
            title: Text(author),
            subtitle: const Text('2小时前'),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(content),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.network(
                    imageUrl,
                    height: 200,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    TextButton.icon(
                      icon: const Icon(Icons.thumb_up_outlined),
                      label: Text('$likes'),
                      onPressed: () {},
                    ),
                    TextButton.icon(
                      icon: const Icon(Icons.comment_outlined),
                      label: Text('$comments'),
                      onPressed: () {},
                    ),
                    TextButton.icon(
                      icon: const Icon(Icons.share_outlined),
                      label: const Text('分享'),
                      onPressed: () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopicCard({
    required String title,
    required int participants,
    required int posts,
    required String imageUrl,
  }) {
    return Card(
      child: Container(
        decoration: BoxDecoration(
          image: DecorationImage(
            image: NetworkImage(imageUrl),
            fit: BoxFit.cover,
            colorFilter: ColorFilter.mode(
              Colors.black.withOpacity(0.4),
              BlendMode.darken,
            ),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const Spacer(),
              Text(
                '$participants 参与 · $posts 帖子',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildExperienceCard({
    required String title,
    required String author,
    required String content,
    required int likes,
    required int comments,
    required List<String> imageUrls,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ListTile(
            leading: const CircleAvatar(
              child: Icon(Icons.person),
            ),
            title: Text(author),
            subtitle: const Text('3小时前'),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(content),
                const SizedBox(height: 8),
                SizedBox(
                  height: 100,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: imageUrls.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            imageUrls[index],
                            width: 100,
                            height: 100,
                            fit: BoxFit.cover,
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    TextButton.icon(
                      icon: const Icon(Icons.thumb_up_outlined),
                      label: Text('$likes'),
                      onPressed: () {},
                    ),
                    TextButton.icon(
                      icon: const Icon(Icons.comment_outlined),
                      label: Text('$comments'),
                      onPressed: () {},
                    ),
                    TextButton.icon(
                      icon: const Icon(Icons.share_outlined),
                      label: const Text('分享'),
                      onPressed: () {},
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpertCard({
    required String name,
    required String title,
    required String hospital,
    required String content,
    required int likes,
    required int comments,
    required String avatarUrl,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ListTile(
            leading: CircleAvatar(
              backgroundImage: NetworkImage(avatarUrl),
            ),
            title: Text(name),
            subtitle: Text('$title · $hospital'),
            trailing: ElevatedButton(
              onPressed: () {},
              child: const Text('关注'),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(content),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                TextButton.icon(
                  icon: const Icon(Icons.thumb_up_outlined),
                  label: Text('$likes'),
                  onPressed: () {},
                ),
                TextButton.icon(
                  icon: const Icon(Icons.comment_outlined),
                  label: Text('$comments'),
                  onPressed: () {},
                ),
                TextButton.icon(
                  icon: const Icon(Icons.share_outlined),
                  label: const Text('分享'),
                  onPressed: () {},
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showPostOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.article_outlined),
                title: const Text('发布帖子'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 跳转到发帖页面
                },
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt_outlined),
                title: const Text('图文动态'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 跳转到图文发布页面
                },
              ),
              ListTile(
                leading: const Icon(Icons.question_answer_outlined),
                title: const Text('提问'),
                onTap: () {
                  Navigator.pop(context);
                  // TODO: 跳转到提问页面
                },
              ),
            ],
          ),
        );
      },
    );
  }
} 