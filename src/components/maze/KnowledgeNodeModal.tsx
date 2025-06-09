import React, { useState } from 'react';
import {import Icon from 'react-native-vector-icons/MaterialIcons';
import { KnowledgeNode } from '../../types/maze';
/**
* 知识节点模态框组件
* Knowledge Node Modal Component;
*/
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Image,
  Alert;
} from 'react-native';
interface KnowledgeNodeModalProps {
  knowledgeNode: KnowledgeNode;,
  visible: boolean;,
  onClose: () => void;
}
const { width: screenWidth, height: screenHeight } = Dimensions.get('window');
const KnowledgeNodeModal: React.FC<KnowledgeNodeModalProps> = ({
  knowledgeNode,
  visible,
  onClose;
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showFullImage, setShowFullImage] = useState(false);
  /**
  * 处理图片点击
  */
  const handleImagePress = (index: number) => {setCurrentImageIndex(index);
    setShowFullImage(true);
  };
  /**
  * 渲染多媒体内容
  */
  const renderMultimedia = () => {if (!knowledgeNode.multimedia) return null;
    const { images, videos, audio } = knowledgeNode.multimedia;
    return (
  <View style={styles.multimediaContainer}>
        {// 图片展示}
        {images && images.length > 0  && <View style={styles.imageSection}>
            <Text style={styles.sectionTitle}>相关图片</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {images.map(imageUrl, index) => ())
                <TouchableOpacity;
                  key={index}
                  style={styles.imageContainer}
                  onPress={() => handleImagePress(index)}
                >
                  <Image source={ uri: imageUrl }}
                    style={styles.thumbnailImage}
                    resizeMode="cover"
                  / loading="lazy" decoding="async" />
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
        {// 视频展示}
        {videos && videos.length > 0  && <View style={styles.videoSection}>
            <Text style={styles.sectionTitle}>相关视频</Text>
            {videos.map(videoUrl, index) => ())
              <TouchableOpacity;
                key={index}
                style={styles.videoItem}
                onPress={() => Alert.alert("提示", "视频播放功能开发中...')}
              >
                <Icon name="play-circle-filled" size={24} color="#4CAF50" />
                <Text style={styles.videoTitle}>健康知识视频 {index + 1}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
        {// 音频展示}
        {audio && audio.length > 0 && (;)
          <View style={styles.audioSection}>;
            <Text style={styles.sectionTitle}>相关音频</Text>;
            {audio.map(audioUrl, index) => (;))
              <TouchableOpacity;
                key={index};
                style={styles.audioItem};
                onPress={() => Alert.alert("提示", "音频播放功能开发中...')};
              >;
                <Icon name="volume-up" size={24} color="#FF9800" />;
                <Text style={styles.audioTitle}>健康知识音频 {index + 1}</Text>;
              </TouchableOpacity>;
            ))};
          </View>;
        )};
      </View>;
    );
  };
  /**
  * 渲染标签
  */
  const renderTags = () => {if (!knowledgeNode.relatedTags || knowledgeNode.relatedTags.length === 0) {return null;
    }
    return (;)
      <View style={styles.tagsContainer}>;
        <Text style={styles.tagsTitle}>相关标签</Text>;
        <View style={styles.tagsWrapper}>;
          {knowledgeNode.relatedTags.map(tag, index) => (;))
            <View key={index} style={styles.tag}>;
              <Text style={styles.tagText}>{tag}</Text>;
            </View>;
          ))};
        </View>;
      </View>;
    );
  };
  return (
  <>
      {// 主模态框}
      <Modal;
        visible={visible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={onClose}
      >
        <View style={styles.container}>
          {// 头部}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <Icon name="school" size={24} color="#4CAF50" />
              <Text style={styles.headerTitle}>健康知识</Text>
            </View>
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Icon name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>
          {// 内容区域}
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
            {// 知识标题}
            <View style={styles.titleSection}>
              <Text style={styles.knowledgeTitle}>{knowledgeNode.title}</Text>
              <View style={styles.metaInfo}>
                <View style={styles.metaItem}>
                  <Icon name="category" size={16} color="#81C784" />
                  <Text style={styles.metaText}>{knowledgeNode.category}</Text>
                </View>
                <View style={styles.metaItem}>
                  <Icon name="signal-cellular-alt" size={16} color="#FFB74D" />
                  <Text style={styles.metaText}>{knowledgeNode.difficultyLevel}</Text>
                </View>
                {knowledgeNode.estimatedReadTime  && <View style={styles.metaItem}>
                    <Icon name="access-time" size={16} color="#64B5F6" />
                    <Text style={styles.metaText}>{knowledgeNode.estimatedReadTime}分钟</Text>
                  </View>
                )}
              </View>
            </View>
            {// 知识内容}
            <View style={styles.contentSection}>
              <Text style={styles.knowledgeContent}>{knowledgeNode.content}</Text>
            </View>
            {// 多媒体内容}
            {renderMultimedia()}
            {// 标签}
            {renderTags()}
            {// 交互元素}
            {knowledgeNode.interactiveElements && knowledgeNode.interactiveElements.length > 0  && <View style={styles.interactiveSection}>
                <Text style={styles.sectionTitle}>互动内容</Text>
                <TouchableOpacity;
                  style={styles.interactiveButton}
                  onPress={() => Alert.alert("提示", "互动功能开发中...')}
                >
                  <Icon name="touch-app" size={20} color="#FFFFFF" />
                  <Text style={styles.interactiveButtonText}>开始互动学习</Text>
                </TouchableOpacity>
              </View>
            )}
            {// 底部间距}
            <View style={styles.bottomSpacing}>
          </ScrollView>
          {// 底部操作栏}
          <View style={styles.footer}>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => Alert.alert("提示", "收藏功能开发中...')}
            >
              <Icon name="bookmark-border" size={20} color="#4CAF50" />
              <Text style={styles.actionButtonText}>收藏</Text>
            </TouchableOpacity>
            <TouchableOpacity;
              style={styles.actionButton}
              onPress={() => Alert.alert("提示", "分享功能开发中...')}
            >
              <Icon name="share" size={20} color="#4CAF50" />
              <Text style={styles.actionButtonText}>分享</Text>
            </TouchableOpacity>
            <TouchableOpacity;
              style={[styles.actionButton, styles.primaryButton]}
              onPress={onClose}
            >
              <Icon name="check" size={20} color="#FFFFFF" />
              <Text style={[styles.actionButtonText, styles.primaryButtonText]}>
                已学习
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
      {// 全屏图片查看模态框}
      {showFullImage && knowledgeNode.multimedia?.images  && <Modal;
          visible={showFullImage}
          animationType="fade"
          presentationStyle="overFullScreen"
          onRequestClose={() => setShowFullImage(false)}
        >
          <View style={styles.fullImageContainer}>;
            <TouchableOpacity;
              style={styles.fullImageCloseButton};
              onPress={() => setShowFullImage(false)};
            >;
              <Icon name="close" size={30} color="#FFFFFF" />;
            </TouchableOpacity>;
            <Image;
              source={ uri: knowledgeNode.multimedia.images[currentImageIndex] }};
              style={styles.fullImage};
              resizeMode="contain";
            />;
          </View>;
        </Modal>;
      )};
    </>;
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#FFFFFF'
  },
  header: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    backgroundColor: '#F8F9FA'
  },
  headerLeft: {,
  flexDirection: 'row',
    alignItems: 'center'
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginLeft: 8;
  },
  closeButton: {,
  padding: 8;
  },
  content: {,
  flex: 1,
    paddingHorizontal: 16;
  },
  titleSection: {,
  paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0'
  },
  knowledgeTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#1B5E20',
    marginBottom: 8,
    lineHeight: 28;
  },
  metaInfo: {,
  flexDirection: 'row',
    flexWrap: 'wrap'
  },
  metaItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
    marginBottom: 4;
  },
  metaText: {,
  fontSize: 14,
    color: '#666',
    marginLeft: 4;
  },
  contentSection: {,
  paddingVertical: 16;
  },
  knowledgeContent: {,
  fontSize: 16,
    lineHeight: 24,
    color: '#333',
    textAlign: 'justify'
  },
  multimediaContainer: {,
  marginVertical: 16;
  },
  sectionTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 12;
  },
  imageSection: {,
  marginBottom: 16;
  },
  imageContainer: {,
  marginRight: 12;
  },
  thumbnailImage: {,
  width: 120,
    height: 80,
    borderRadius: 8;
  },
  videoSection: {,
  marginBottom: 16;
  },
  videoItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#F1F8E9',
    borderRadius: 8,
    marginBottom: 8;
  },
  videoTitle: {,
  fontSize: 14,
    color: '#2E7D32',
    marginLeft: 8;
  },
  audioSection: {,
  marginBottom: 16;
  },
  audioItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#FFF3E0',
    borderRadius: 8,
    marginBottom: 8;
  },
  audioTitle: {,
  fontSize: 14,
    color: '#E65100',
    marginLeft: 8;
  },
  tagsContainer: {,
  marginVertical: 16;
  },
  tagsTitle: {,
  fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 8;
  },
  tagsWrapper: {,
  flexDirection: 'row',
    flexWrap: 'wrap'
  },
  tag: {,
  backgroundColor: '#E8F5E8',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8;
  },
  tagText: {,
  fontSize: 12,
    color: '#2E7D32',
    fontWeight: '500'
  },
  interactiveSection: {,
  marginVertical: 16;
  },
  interactiveButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#4CAF50',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8;
  },
  interactiveButtonText: {,
  color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8;
  },
  bottomSpacing: {,
  height: 20;
  },
  footer: {,
  flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    backgroundColor: '#F8F9FA'
  },
  actionButton: {,
  flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#4CAF50'
  },
  actionButtonText: {,
  fontSize: 14,
    color: '#4CAF50',
    marginLeft: 4,
    fontWeight: '500'
  },
  primaryButton: {,
  backgroundColor: '#4CAF50'
  },
  primaryButtonText: {,
  color: '#FFFFFF'
  },
  fullImageContainer: {,
  flex: 1,backgroundColor: 'rgba(0, 0, 0, 0.9)',justifyContent: 'center',alignItems: 'center';
  },fullImageCloseButton: {,
  position: "absolute",
      top: 50,right: 20,zIndex: 1,padding: 10;
  },fullImage: {width: screenWidth,height: screenHeight * 0.8;
  };
});
export default KnowledgeNodeModal;