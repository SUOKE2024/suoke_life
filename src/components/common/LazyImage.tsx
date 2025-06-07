import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  View,
  Image,
  Animated,
  StyleSheet,
  Dimensions,
  ImageStyle,
  ViewStyle,
  ImageSourcePropType,
  ActivityIndicator,
} from 'react-native';
const { width: screenWidth } = Dimensions.get('window');
// 图片懒加载配置
interface LazyImageConfig {
  placeholder?: ImageSourcePropType;
  errorImage?: ImageSourcePropType;
  fadeInDuration?: number;
  threshold?: number;
  retryCount?: number;
  retryDelay?: number;
  cachePolicy?: 'memory' | 'disk' | 'none';
  quality?: 'low' | 'medium' | 'high';
  progressive?: boolean;
}
// 图片懒加载属性
interface LazyImageProps {
  source: ImageSourcePropType;
  style?: ImageStyle;
  containerStyle?: ViewStyle;
  config?: Partial<LazyImageConfig>;
  onLoad?: () => void;
  onError?: (error: any) => void;
  onLoadStart?: () => void;
  onLoadEnd?: () => void;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'repeat' | 'center';
  blurRadius?: number;
  accessible?: boolean;
  accessibilityLabel?: string;
  testID?: string;
}
// 默认配置
const DEFAULT_CONFIG: LazyImageConfig = {,
  fadeInDuration: 300,
  threshold: 100,
  retryCount: 3,
  retryDelay: 1000,
  cachePolicy: 'memory',
  quality: 'medium',
  progressive: true,
};
// 图片缓存管理器
class ImageCacheManager {
  private static instance: ImageCacheManager;
  private cache = new Map<string, string>();
  private loading = new Set<string>();
  static getInstance(): ImageCacheManager {
    if (!ImageCacheManager.instance) {
      ImageCacheManager.instance = new ImageCacheManager();
    }
    return ImageCacheManager.instance;
  }
  async preloadImage(uri: string): Promise<string> {
    if (this.cache.has(uri)) {
      return this.cache.get(uri)!;
    }
    if (this.loading.has(uri)) {
      // 等待正在加载的图片
      return new Promise(resolve) => {
        const checkLoading = () => {
          if (!this.loading.has(uri)) {
            resolve(this.cache.get(uri) || uri);
          } else {
            setTimeout(checkLoading, 100);
          }
        };
        checkLoading();
      });
    }
    this.loading.add(uri);
    try {
      // 预加载图片
      await Image.prefetch(uri);
      this.cache.set(uri, uri);
      return uri;
    } catch (error) {
      console.warn('Failed to preload image:', uri, error);
      return uri;
    } finally {
      this.loading.delete(uri);
    }
  }
  clearCache(): void {
    this.cache.clear();
    this.loading.clear();
  }
  getCacheSize(): number {
    return this.cache.size;
  }
}
// 懒加载图片组件
export const LazyImage: React.FC<LazyImageProps> = ({
  source,
  style,
  containerStyle,
  config: userConfig = {},
  onLoad,
  onError,
  onLoadStart,
  onLoadEnd,
  resizeMode = 'cover',
  blurRadius,
  accessible,
  accessibilityLabel,
  testID,
}) => {
  const config = { ...DEFAULT_CONFIG, ...userConfig };
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const cacheManager = useRef(ImageCacheManager.getInstance()).current;
  // 获取图片URI;
  const getImageUri = useCallback() => {
    if (typeof source === 'object' && 'uri' in source) {
      return source.uri;
    }
    return null;
  }, [source]);
  // 处理图片加载开始
  const handleLoadStart = useCallback() => {
    setLoading(true);
    setError(false);
    onLoadStart?.();
  }, [onLoadStart]);
  // 处理图片加载成功
  const handleLoad = useCallback() => {
    setLoading(false);
    setError(false);
        // 淡入动画
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: config.fadeInDuration,
      useNativeDriver: true,
    }).start();
    onLoad?.();
  }, [fadeAnim, config.fadeInDuration, onLoad]);
  // 处理图片加载错误
  const handleError = useCallback(errorEvent: any) => {
    setLoading(false);
    setError(true);
        // 重试逻辑
    if (retryCount < config.retryCount!) {
      setTimeout() => {
        setRetryCount(prev => prev + 1);
        setError(false);
        setLoading(true);
      }, config.retryDelay! * (retryCount + 1)); // 指数退避
    }
    onError?.(errorEvent);
  }, [retryCount, config.retryCount, config.retryDelay, onError]);
  // 处理图片加载结束
  const handleLoadEnd = useCallback() => {
    onLoadEnd?.();
  }, [onLoadEnd]);
  // 预加载图片
  useEffect() => {
    const uri = getImageUri();
    if (uri && config.cachePolicy !== 'none') {
      cacheManager.preloadImage(uri);
    }
  }, [getImageUri, config.cachePolicy, cacheManager]);
  // 渲染占位符
  const renderPlaceholder = () => {
    if (config.placeholder) {
      return (
        <Image;
          source={config.placeholder}
          style={[styles.placeholder, style]}
          resizeMode={resizeMode}
        />
      );
    }
    return (
      <View style={[styles.placeholderContainer, style]}>
        <ActivityIndicator size="small" color="#999" />
      </View>
    );
  };
  // 渲染错误图片
  const renderErrorImage = () => {
    if (config.errorImage) {
      return (
        <Image;
          source={config.errorImage}
          style={[styles.errorImage, style]}
          resizeMode={resizeMode}
        />
      );
    }
    return (
      <View style={[styles.errorContainer, style]}>
        <View style={styles.errorIcon}>
      </View>
    );
  };
  return (
    <View style={[styles.container, containerStyle]} testID={testID}>
      {}
      {(loading || error) && (
        <View style={styles.overlayContainer}>
          {error ? renderErrorImage() : renderPlaceholder()}
        </View>
      )}
      {}
      {!error && (
        <Animated.View style={ opacity: fadeAnim }}>
          <Image;
            source={source}
            style={[styles.image, style]}
            resizeMode={resizeMode}
            blurRadius={blurRadius}
            onLoadStart={handleLoadStart}
            onLoad={handleLoad}
            onError={handleError}
            onLoadEnd={handleLoadEnd}
            accessible={accessible}
            accessibilityLabel={accessibilityLabel}
          />
        </Animated.View>
      )}
    </View>
  );
};
// 渐进式图片组件
export const ProgressiveImage: React.FC<LazyImageProps & {
  thumbnailSource?: ImageSourcePropType;
}> = ({ thumbnailSource, ...props }) => {
  const [thumbnailLoaded, setThumbnailLoaded] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const thumbnailFade = useRef(new Animated.Value(0)).current;
  const imageFade = useRef(new Animated.Value(0)).current;
  const handleThumbnailLoad = useCallback() => {
    setThumbnailLoaded(true);
    Animated.timing(thumbnailFade, {
      toValue: 1,
      duration: 200,
      useNativeDriver: true,
    }).start();
  }, [thumbnailFade]);
  const handleImageLoad = useCallback() => {
    setImageLoaded(true);
    Animated.timing(imageFade, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start() => {
      // 图片加载完成后隐藏缩略图
      Animated.timing(thumbnailFade, {
        toValue: 0,
        duration: 200,
        useNativeDriver: true,
      }).start();
    });
        props.onLoad?.();
  }, [imageFade, thumbnailFade, props.onLoad]);
  return (
    <View style={[styles.container, props.containerStyle]}>
      {}
      {thumbnailSource && (
        <Animated.View style={[styles.thumbnailContainer, { opacity: thumbnailFade }]}>
          <Image;
            source={thumbnailSource}
            style={[styles.thumbnail, props.style]}
            resizeMode={props.resizeMode}
            onLoad={handleThumbnailLoad}
            blurRadius={1}
          />
        </Animated.View>
      )}
      {}
      <Animated.View style={ opacity: imageFade }}>
        <LazyImage;
          {...props}
          onLoad={handleImageLoad}
        />
      </Animated.View>
    </View>
  );
};
// 图片网格组件
export const ImageGrid: React.FC<{,
  images: Array<{ id: string; source: ImageSourcePropType; thumbnail?: ImageSourcePropType }>;
  columns?: number;
  spacing?: number;
  aspectRatio?: number;
  onImagePress?: (image: any, index: number) => void;
  style?: ViewStyle;
}> = ({
  images,
  columns = 2,
  spacing = 8,
  aspectRatio = 1,
  onImagePress,
  style,
}) => {
  const imageWidth = (screenWidth - spacing * (columns + 1)) / columns;
  const imageHeight = imageWidth / aspectRatio;
  const renderImage = useCallback(image: any, index: number) => {
    return (
      <View;
        key={image.id}
        style={[
          styles.gridItem,
          {
            width: imageWidth,
            height: imageHeight,
            marginLeft: spacing,
            marginBottom: spacing,
          },
        ]}
      >
        <ProgressiveImage;
          source={image.source}
          thumbnailSource={image.thumbnail}
          style={styles.gridImage}
          containerStyle={styles.gridImageContainer}
          onLoad={() => console.log(`Image ${index} loaded`)}
        />
      </View>
    );
  }, [imageWidth, imageHeight, spacing]);
  return (
    <View style={[styles.gridContainer, { paddingTop: spacing }, style]}>
      {images.map(renderImage)}
    </View>
  );
};
// 图片预加载Hook;
export const useImagePreloader = (imageUris: string[]) => {
  const [preloadedCount, setPreloadedCount] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const cacheManager = useRef(ImageCacheManager.getInstance()).current;
  useEffect() => {
    const preloadImages = async () => {
      let count = 0;
            for (const uri of imageUris) {
        try {
          await cacheManager.preloadImage(uri);
          count++;
          setPreloadedCount(count);
        } catch (error) {
          console.warn('Failed to preload image:', uri, error);
        }
      }
            setIsComplete(true);
    };
    if (imageUris.length > 0) {
      preloadImages();
    }
  }, [imageUris, cacheManager]);
  return {
    preloadedCount,
    totalCount: imageUris.length,
    isComplete,
    progress: imageUris.length > 0 ? preloadedCount / imageUris.length : 0,
  };
};
const styles = StyleSheet.create({
  container: {,
  position: 'relative',
  },
  image: {,
  width: '100%',
    height: '100%',
  },
  overlayContainer: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 1,
  },
  placeholder: {,
  width: '100%',
    height: '100%',
  },
  placeholderContainer: {,
  width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  errorImage: {,
  width: '100%',
    height: '100%',
  },
  errorContainer: {,
  width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F0F0F0',
  },
  errorIcon: {,
  width: 24,
    height: 24,
    backgroundColor: '#CCC',
    borderRadius: 12,
  },
  thumbnailContainer: {,
  position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  thumbnail: {,
  width: '100%',
    height: '100%',
  },
  gridContainer: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
  },
  gridItem: {,
  borderRadius: 8,
    overflow: 'hidden',
  },
  gridImageContainer: {,
  flex: 1,
  },
  gridImage: {,
  width: '100%',
    height: '100%',
  },
});
export default LazyImage;