//;/g/;
//;,/g/;
import React,{ memo } from ";react";";
Text,;
StyleSheet,";,"";
TouchableOpacity,";"";
  { Animated } from "react-native;";";
interface ContentCardProps {item: ContentItem}onPress: (item: ContentItem) => void;
onBookmark?: (item: ContentItem) => void;
onLike?: (item: ContentItem) => void;
isBookmarked?: boolean;
isLiked?: boolean;
}
}
  style?: unknown;}
}
export const ContentCard = memo<ContentCardProps  />({/;)/      ite;)/;,}m,;,/g/;
onPress,;
onBookmark,;
onLike,;
isBookmarked = false,;
isLiked = false,;
}
  style;}
}) => {}
  const typeConfig = CONTENT_TYPE_CONFIG[item.typ;e;];
const difficultyConfig = DIFFICULTY_CONFIG[item.difficult;y;];";,"";
const  handlePress = useCallback() => {"}";
performanceMonitor: usePerformanceMonitor("ContentCard", {trackRender: true,trackMemory: false,warnThreshold: 100;};);";"";
    ///;,/g/;
onPress(item);
  };
const handleBookmark = useCallback(); => {}
    ///;,/g/;
e.stopPropagation();
onBookmark?.(item);
  };
const handleLike = useCallback(); => {}
    ///;,/g/;
e.stopPropagation();
onLike?.(item);
  };
performanceMonitor.recordRender();
return (;);
    <TouchableOpacity,style={[styles.container, style]};  />/;,/g/;
onPress={handlePress};";,"";
activeOpacity={0.8} />/      {///          {item.featured && (;)"}""/;"/g"/;
        <View style={styles.featuredBadge}>/          <Icon name="star" size={12} color={colors.white}  />/          <Text style={styles.featuredText}>精选</Text>/        </View>/          )};"/;"/g"/;
      {///;}/;/g/;
        <View style={styles.headerInfo}>/          <View style={styles.typeContainer}>/                <Icon;  />/;,/g/;
name={typeConfig.icon};
size={14};
color={typeConfig.color} />/            <Text style={[styles.typeText, { color: typeConfig.col;o;r   }}]}  />/                  {typeConfig.name}/;/g/;
            </Text>/          </View>//;/g/;
          <View style={styles.metaInfo}>/            <Text style={styles.author}>{item.author}</Text>/            <Text style={styles.separator}>•</Text>/            <Text style={styles.readTime}>{item.readTime}</Text>/          </View>/        </View>//;/g/;
        {///              <TouchableOpacity;}  />/;,/g/;
style={styles.actionButton}";,"";
onPress={handleBookmark} />/                <Icon;"  />/;,"/g"/;
name={isBookmarked ? "bookmark" : "bookmark-outline"}";,"";
size={20}
              color={isBookmarked ? colors.primary: colors.textSecondary;} />/          </TouchableOpacity>//;/g/;
          <TouchableOpacity;  />/;,/g/;
style={styles.actionButton}";,"";
onPress={handleLike} />/                <Icon;"  />/;,"/g"/;
name={isLiked ? "heart" : "heart-outline"}";,"";
size={20}
              color={isLiked ? colors.error: colors.textSecondary;} />/          </TouchableOpacity>/        </View>/      </View>//;/g/;
      {///              {item.title}/;/g/;
        </Text>/        <Text style={styles.subtitle} numberOfLines={2}  />/              {item.subtitle}/;/g/;
        </Text>//;/g/;
        {item.description  && <Text style={styles.description} numberOfLines={3}  />/                {item.description}/;/g/;
          </Text>/            )}/;/g/;
      </View>//;/g/;
      {///              {item.tags.slice(0, 3).map(tag, index) => ())}/;/g/;
            <View key={index} style={styles.tag}>/              <Text style={styles.tagText}>{tag}</Text>/            </View>/              ))}/;/g/;
          {item.tags.length > 3  && <Text style={styles.moreTagsText}>+{item.tags.length - 3}</Text>/              )}"/;"/g"/;
        </View>/"/;"/g"/;
        <View style={styles.stats}>/          <View style={[styles.difficultyBadge, { backgroundColor: difficultyConfig.color + 20";}}]}  />/            <Text style={[styles.difficultyText, { color: difficultyConfig.color;}}]}  />/                  {difficultyConfig.name}""/;"/g"/;
            </Text>/          </View>/"/;"/g"/;
          <View style={styles.likesContainer}>/            <Icon name="heart-outline" size={14} color={colors.textSecondary}  />/            <Text style={styles.likesText}>{item.likes}</Text>/          </View>/        </View>/      </View>/    </TouchableOpacity>/      )"/;"/g"/;
});";,"";
ContentCard.displayName = "ContentCard";
const: styles = StyleSheet.create({)container: {)}backgroundColor: colors.background,;
borderRadius: borderRadius.lg,;
padding: spacing.md,;
marginHorizontal: spacing.md,;
marginVertical: spacing.sm,;
borderWidth: 1,;
const borderColor = colors.border;
}
    ...shadows.sm;}
  },";,"";
featuredBadge: {,";,}position: "absolute";",";
top: spacing.sm,";,"";
right: spacing.sm,";,"";
flexDirection: row";",";,"";
alignItems: "center,",";,"";
backgroundColor: colors.primary,;
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: borderRadius.sm,;
}
    const zIndex = 1;}
  }
featuredText: {color: colors.white,";,"";
fontSize: fonts.size.xs,";,"";
fontWeight: "600";","";"";
}
    const marginLeft = spacing.xs;}
  },";,"";
header: {,";,}flexDirection: row";",";,"";
alignItems: "flex-start,",";"";
}
    const marginBottom = spacing.md;}
  }
imageContainer: {width: 50,;
height: 50,;
borderRadius: 25,";,"";
backgroundColor: colors.surface,";,"";
justifyContent: "center";",";
alignItems: center";","";"";
}
    const marginRight = spacing.md;}
  }
image: { fontSize: 24  ;}
headerInfo: { flex: 1  ;},";,"";
typeContainer: {,";,}flexDirection: "row,",";,"";
alignItems: "center";","";"";
}
    const marginBottom = spacing.xs;}
  }
typeText: {,";,}fontSize: fonts.size.sm,";,"";
fontWeight: 600";","";"";
}
    const marginLeft = spacing.xs;}
  },";,"";
metaInfo: {,";,}flexDirection: "row,",";"";
}
    const alignItems = "center"}"";"";
  ;}
author: {fontSize: fonts.size.sm,";,"";
color: colors.text,";"";
}
    const fontWeight = 500"}"";"";
  ;}
separator: {fontSize: fonts.size.sm,;
color: colors.textSecondary,;
}
    const marginHorizontal = spacing.xs;}
  }
readTime: {fontSize: fonts.size.sm,;
}
    const color = colors.textSecondary;}
  },";,"";
actions: {,";,}flexDirection: "row,",";"";
}
    const alignItems = "center"}"";"";
  ;}
actionButton: {padding: spacing.xs,;
}
    const marginLeft = spacing.xs;}
  }
content: { marginBottom: spacing.md  ;}
title: {,";,}fontSize: fonts.size.lg,";,"";
fontWeight: bold";",";
color: colors.text,;
lineHeight: fonts.lineHeight.lg,;
}
    const marginBottom = spacing.xs;}
  }
subtitle: {fontSize: fonts.size.md,;
color: colors.textSecondary,;
lineHeight: fonts.lineHeight.md,;
}
    const marginBottom = spacing.sm;}
  }
description: {fontSize: fonts.size.sm,;
color: colors.textSecondary,;
}
    const lineHeight = fonts.lineHeight.sm;}
  },";,"";
footer: {,";,}flexDirection: "row,",";,"";
justifyContent: "space-between";","";"";
}
    const alignItems = flex-end"}"";"";
  ;},";,"";
tags: {,";,}flexDirection: "row,",";,"";
alignItems: "center";",";
flex: 1,";"";
}
    const flexWrap = wrap"}"";"";
  ;}
tag: {backgroundColor: colors.surface,;
paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: borderRadius.sm,;
marginRight: spacing.xs,;
}
    const marginBottom = spacing.xs;}
  }
tagText: {fontSize: fonts.size.xs,;
}
    const color = colors.text;}
  }
moreTagsText: {fontSize: fonts.size.xs,";,"";
color: colors.textSecondary,";"";
}
    const fontStyle = "italic"}"";"";
  ;},";,"";
stats: {,";,}flexDirection: "row";","";"";
}
    const alignItems = center"}"";"";
  ;}
difficultyBadge: {paddingHorizontal: spacing.sm,;
paddingVertical: spacing.xs,;
borderRadius: borderRadius.sm,;
}
    const marginRight = spacing.md;}
  }
difficultyText: {,";,}fontSize: fonts.size.xs,";"";
}
    const fontWeight = "600"}"";"";
  ;},";,"";
likesContainer: {,";,}flexDirection: "row";","";"";
}
    const alignItems = center"}"";"";
  ;}
likesText: {,;}}
  fontSize: fonts.size.sm,}";,"";
color: colors.textSecondary,marginLeft: spacing.xs;};};);""";