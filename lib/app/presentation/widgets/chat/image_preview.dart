import 'package:flutter/material.dart';
import 'package:photo_view/photo_view.dart';
import 'package:photo_view/photo_view_gallery.dart';

class ImagePreview extends StatelessWidget {
  final List<String> imageUrls;
  final int initialIndex;
  final PageController pageController;
  final Function(int)? onPageChanged;

  ImagePreview({
    Key? key,
    required this.imageUrls,
    this.initialIndex = 0,
    this.onPageChanged,
  })  : pageController = PageController(initialPage: initialIndex),
        super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 图片浏览器
          PhotoViewGallery.builder(
            scrollPhysics: const BouncingScrollPhysics(),
            builder: (BuildContext context, int index) {
              return PhotoViewGalleryPageOptions(
                imageProvider: NetworkImage(imageUrls[index]),
                initialScale: PhotoViewComputedScale.contained,
                minScale: PhotoViewComputedScale.contained,
                maxScale: PhotoViewComputedScale.covered * 2,
              );
            },
            itemCount: imageUrls.length,
            loadingBuilder: (context, event) => Center(
              child: SizedBox(
                width: 20.0,
                height: 20.0,
                child: CircularProgressIndicator(
                  value: event == null
                      ? 0
                      : event.cumulativeBytesLoaded / event.expectedTotalBytes!,
                ),
              ),
            ),
            backgroundDecoration: const BoxDecoration(color: Colors.black),
            pageController: pageController,
            onPageChanged: onPageChanged,
          ),
          // 顶部操作栏
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => Navigator.pop(context),
                  ),
                  Row(
                    children: [
                      IconButton(
                        icon: const Icon(Icons.share, color: Colors.white),
                        onPressed: () {
                          // 实现分享功能
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.download, color: Colors.white),
                        onPressed: () {
                          // 实现下载功能
                        },
                      ),
                      IconButton(
                        icon: const Icon(Icons.more_vert, color: Colors.white),
                        onPressed: () {
                          // 显示更多选项
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
} 