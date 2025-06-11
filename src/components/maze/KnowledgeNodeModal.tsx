import React, { useState } from "react"
import {import Icon from "react-native-vector-icons/MaterialIcons";} frommport { KnowledgeNode } from "../../types/maze";
/* ; */
*/
View,
Text,
StyleSheet,
Modal,
ScrollView,
TouchableOpacity,
Dimensions,"
Image,
Alert;
} from "react-native;
interface KnowledgeNodeModalProps {knowledgeNode: KnowledgeNode}visible: boolean,
}
}
  onClose: () => void}
}
const { width: screenWidth, height: screenHeight ;} = Dimensions.get('window');
const  KnowledgeNodeModal: React.FC<KnowledgeNodeModalProps> = ({)knowledgeNode,)visible,);
}
  onClose;)}
}) => {const [currentImageIndex, setCurrentImageIndex] = useState(0)const [showFullImage, setShowFullImage] = useState(false);
  /* 击 */
  */
const handleImagePress = useCallback((index: number) => {setCurrentImageIndex(index)}
    setShowFullImage(true)}
  };
  /* 容 */
  */
const renderMultimedia = useCallback(() => {if (!knowledgeNode.multimedia) return null}
    const { images, videos, audio } = knowledgeNode.multimedia;
return (<View style={styles.multimediaContainer}>;)        {// 图片展示}
        {images && images.length > 0  && <View style={styles.imageSection}>);
            <Text style={styles.sectionTitle}>相关图片</Text>)
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>);
              {images.map(imageUrl, index) => ())}
                <TouchableOpacity;}  />
key={index}
                  style={styles.imageContainer}
                  onPress={() => handleImagePress(index)}
                >;
                  <Image source={ uri: imageUrl ;}}'  />/,'/g'/;
style={styles.thumbnailImage}
resizeMode="cover;
                  / loading="lazy" decoding="async" />"/;"/g"/;
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        )}
        {// 视频展示}
        {videos && videos.length > 0  && <View style={styles.videoSection}>;
            <Text style={styles.sectionTitle}>相关视频</Text>
            {videos.map(videoUrl, index) => ())}
              <TouchableOpacity;}  />
key={index}
                style={styles.videoItem}
              >
                <Icon name="play-circle-filled" size={24} color="#4CAF50"  />"/;"/g"/;
                <Text style={styles.videoTitle}>健康知识视频 {index + 1}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}
        {// 音频展示}
        {audio && audio.length > 0 && (;)}
          <View style={styles.audioSection}>;
            <Text style={styles.sectionTitle}>相关音频</Text>;
            {audio.map(audioUrl, index) => (;))}
              <TouchableOpacity;}  />
key={index};
style={styles.audioItem};
              >;
                <Icon name="volume-up" size={24} color="#FF9800"  />;"/;"/g"/;
                <Text style={styles.audioTitle}>健康知识音频 {index + 1}</Text>;
              </TouchableOpacity>;
            ))};
          </View>;
        )};
      </View>;
    );
  };
  /* 签 */
  */
const renderTags = useCallback(() => {if (!knowledgeNode.relatedTags || knowledgeNode.relatedTags.length === 0) {return null}
    }
    return (;);
      <View style={styles.tagsContainer}>;
        <Text style={styles.tagsTitle}>相关标签</Text>;
        <View style={styles.tagsWrapper}>;
          {knowledgeNode.relatedTags.map(tag, index) => (;))}
            <View key={index} style={styles.tag}>;
              <Text style={styles.tagText}>{tag}</Text>;
            </View>;
          ))};
        </View>;
      </View>;
    );
  };
return (<>;)      {// 主模态框}
      <Modal;"  />"
visible={visible}","
animationType="slide
presentationStyle="pageSheet";
onRequestClose={onClose}
      >;
        <View style={styles.container}>;
          {// 头部}
          <View style={styles.header}>
            <View style={styles.headerLeft}>
              <Icon name="school" size={24} color="#4CAF50"  />"/;"/g"/;
              <Text style={styles.headerTitle}>健康知识</Text>"
            </View>"/;"/g"/;
            <TouchableOpacity style={styles.closeButton} onPress={onClose}>
              <Icon name="close" size={24} color="#666"  />"/;"/g"/;
            </TouchableOpacity>
          </View>
          {// 内容区域}
          <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>;
            {// 知识标题}
            <View style={styles.titleSection}>;
              <Text style={styles.knowledgeTitle}>{knowledgeNode.title}</Text>"
              <View style={styles.metaInfo}>
                <View style={styles.metaItem}>
                  <Icon name="category" size={16} color="#81C784"  />"/;"/g"/;
                  <Text style={styles.metaText}>{knowledgeNode.category}</Text>"
                </View>"/;"/g"/;
                <View style={styles.metaItem}>
                  <Icon name="signal-cellular-alt" size={16} color="#FFB74D"  />"/;"/g"/;
                  <Text style={styles.metaText}>{knowledgeNode.difficultyLevel}</Text>"
                </View>"/;"/g"/;
                {knowledgeNode.estimatedReadTime  && <View style={styles.metaItem}>
                    <Icon name="access-time" size={16} color="#64B5F6"  />")
                    <Text style={styles.metaText}>{knowledgeNode.estimatedReadTime}分钟</Text>)
                  </View>)
                )}
              </View>
            </View>
            {// 知识内容}
            <View style={styles.contentSection}>;
              <Text style={styles.knowledgeContent}>{knowledgeNode.content}</Text>
            </View>
            {// 多媒体内容}
            {renderMultimedia()}
            {// 标签}
            {renderTags()}
            {// 交互元素}
            {knowledgeNode.interactiveElements && knowledgeNode.interactiveElements.length > 0  && <View style={styles.interactiveSection}>;
                <Text style={styles.sectionTitle}>互动内容</Text>
                <TouchableOpacity;  />
style={styles.interactiveButton}
                >
                  <Icon name="touch-app" size={20} color="#FFFFFF"  />"/;"/g"/;
                  <Text style={styles.interactiveButtonText}>开始互动学习</Text>
                </TouchableOpacity>
              </View>
            )}
            {// 底部间距}
            <View style={styles.bottomSpacing}>;
          </ScrollView>
          {// 底部操作栏}
          <View style={styles.footer}>;
            <TouchableOpacity;  />
style={styles.actionButton}
            >
              <Icon name="bookmark-border" size={20} color="#4CAF50"  />"/;"/g"/;
              <Text style={styles.actionButtonText}>收藏</Text>
            </TouchableOpacity>
            <TouchableOpacity;  />
style={styles.actionButton}
            >
              <Icon name="share" size={20} color="#4CAF50"  />"/;"/g"/;
              <Text style={styles.actionButtonText}>分享</Text>
            </TouchableOpacity>
            <TouchableOpacity;  />
style={[styles.actionButton, styles.primaryButton]}
              onPress={onClose}
            >
              <Icon name="check" size={20} color="#FFFFFF"  />"/;"/g"/;
              <Text style={[styles.actionButtonText, styles.primaryButtonText]}>;
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
      {// 全屏图片查看模态框}
      {showFullImage && knowledgeNode.multimedia?.images  && <Modal;}"  />"
visible={showFullImage}","
animationType="fade
presentationStyle="overFullScreen";
onRequestClose={() => setShowFullImage(false)}
        >;
          <View style={styles.fullImageContainer}>;
            <TouchableOpacity;  />
style={styles.fullImageCloseButton};
onPress={() => setShowFullImage(false)};
            >;
              <Icon name="close" size={30} color="#FFFFFF"  />;"/;"/g"/;
            </TouchableOpacity>;
            <Image;  />"
source={ uri: knowledgeNode.multimedia.images[currentImageIndex] ;}};","
style={styles.fullImage};","
resizeMode="contain;"";
            />;
          </View>;
        </Modal>;
      )};
    < />;
  );
};
const  styles = StyleSheet.create({)container: {,"flex: 1,";
}
    const backgroundColor = '#FFFFFF'}
  ;},'
header: {,'flexDirection: 'row,'
justifyContent: 'space-between,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,
borderBottomWidth: 1,'
borderBottomColor: '#E0E0E0,'
}
    const backgroundColor = '#F8F9FA'}
  ;},'
headerLeft: {,'flexDirection: 'row,'
}
    const alignItems = 'center'}
  }
headerTitle: {,'fontSize: 18,'
fontWeight: 'bold,'
color: '#2E7D32,'
}
    const marginLeft = 8}
  }
closeButton: {,}
  const padding = 8}
  }
content: {flex: 1,
}
    const paddingHorizontal = 16}
  }
titleSection: {paddingVertical: 16,
borderBottomWidth: 1,
}
    const borderBottomColor = '#F0F0F0'}
  }
knowledgeTitle: {,'fontSize: 20,'
fontWeight: 'bold,'
color: '#1B5E20,'';
marginBottom: 8,
}
    const lineHeight = 28}
  },'
metaInfo: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
metaItem: {,'flexDirection: 'row,'
alignItems: 'center,'';
marginRight: 16,
}
    const marginBottom = 4}
  }
metaText: {,'fontSize: 14,'
color: '#666,'
}
    const marginLeft = 4}
  }
contentSection: {,}
  const paddingVertical = 16}
  }
knowledgeContent: {fontSize: 16,
lineHeight: 24,'
color: '#333,'
}
    const textAlign = 'justify'}
  }
multimediaContainer: {,}
  const marginVertical = 16}
  }
sectionTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#2E7D32,'
}
    const marginBottom = 12}
  }
imageSection: {,}
  const marginBottom = 16}
  }
imageContainer: {,}
  const marginRight = 12}
  }
thumbnailImage: {width: 120,
height: 80,
}
    const borderRadius = 8}
  }
videoSection: {,}
  const marginBottom = 16}
  },'
videoItem: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
paddingHorizontal: 16,'
backgroundColor: '#F1F8E9,'';
borderRadius: 8,
}
    const marginBottom = 8}
  }
videoTitle: {,'fontSize: 14,'
color: '#2E7D32,'
}
    const marginLeft = 8}
  }
audioSection: {,}
  const marginBottom = 16}
  },'
audioItem: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 12,
paddingHorizontal: 16,'
backgroundColor: '#FFF3E0,'';
borderRadius: 8,
}
    const marginBottom = 8}
  }
audioTitle: {,'fontSize: 14,'
color: '#E65100,'
}
    const marginLeft = 8}
  }
tagsContainer: {,}
  const marginVertical = 16}
  }
tagsTitle: {,'fontSize: 16,'
fontWeight: 'bold,'
color: '#2E7D32,'
}
    const marginBottom = 8}
  },'
tagsWrapper: {,'flexDirection: 'row,'
}
    const flexWrap = 'wrap'}
  ;},'
tag: {,'backgroundColor: '#E8F5E8,'';
paddingHorizontal: 12,
paddingVertical: 6,
borderRadius: 16,
marginRight: 8,
}
    const marginBottom = 8}
  }
tagText: {,'fontSize: 12,'
color: '#2E7D32,'
}
    const fontWeight = '500'}
  }
interactiveSection: {,}
  const marginVertical = 16}
  },'
interactiveButton: {,'flexDirection: 'row,'
alignItems: 'center,'
justifyContent: 'center,'
backgroundColor: '#4CAF50,'';
paddingVertical: 12,
paddingHorizontal: 24,
}
    const borderRadius = 8}
  },'
interactiveButtonText: {,'color: '#FFFFFF,'';
fontSize: 16,'
fontWeight: 'bold,'
}
    const marginLeft = 8}
  }
bottomSpacing: {,}
  const height = 20}
  },'
footer: {,'flexDirection: 'row,'
justifyContent: 'space-around,'
alignItems: 'center,'';
paddingHorizontal: 16,
paddingVertical: 12,
borderTopWidth: 1,'
borderTopColor: '#E0E0E0,'
}
    const backgroundColor = '#F8F9FA'}
  ;},'
actionButton: {,'flexDirection: 'row,'
alignItems: 'center,'';
paddingVertical: 8,
paddingHorizontal: 16,
borderRadius: 20,
borderWidth: 1,
}
    const borderColor = '#4CAF50'}
  }
actionButtonText: {,'fontSize: 14,'
color: '#4CAF50,'';
marginLeft: 4,
}
    const fontWeight = '500'}
  ;},'
primaryButton: {,';}}
  const backgroundColor = '#4CAF50'}
  ;},'
primaryButtonText: {,';}}
  const color = '#FFFFFF')}
  ;},)'
fullImageContainer: {,)';}}
  flex: 1,backgroundColor: 'rgba(0, 0, 0, 0.9)',justifyContent: 'center',alignItems: 'center}
  },fullImageCloseButton: {,'position: "absolute,
}
      top: 50,right: 20,zIndex: 1,padding: 10}
  },fullImage: {width: screenWidth,height: screenHeight * 0.8}
  };
});","
export default KnowledgeNodeModal;""
