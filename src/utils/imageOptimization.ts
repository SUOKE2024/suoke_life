// 图片优化配置 - 索克生活APP - 性能优化

export interface ImageOptimizationConfig {
  webp: boolean;
  quality: number;
  progressive: boolean;
  sizes: number[];
}

export const imageOptimizationConfig: ImageOptimizationConfig = {
  webp: true,
  quality: 80,
  progressive: true,
  sizes: [1, 2, 3]
};

export interface ImageOptimizationOptions {
  quality?: number;
  format?: 'webp' | 'jpeg' | 'png';
  progressive?: boolean;
  width?: number;
  height?: number;
}

export interface ResponsiveImage {
  size: string;
  path: string;
  width: number;
  height: number;
}

// 图片优化工具
export class ImageOptimizer {
  static optimizeImage(imagePath: string, options: ImageOptimizationOptions = {}): ImageOptimizationOptions {
    // 图片优化逻辑
    const defaultOptions: ImageOptimizationOptions = {
      quality: 80,
      format: "webp",
      progressive: true
    };
    
    return { ...defaultOptions, ...options };
  }

  static generateResponsiveImages(imagePath: string): ResponsiveImage[] {
    const sizes = [1, 2, 3];
    
    return sizes.map(size => ({
      size: `${size}x`,
      path: imagePath.replace(/\.([^.]+)$/, `@${size}x.$1`),
      width: 100 * size,
      height: 100 * size
    }));
  }

  static getOptimizedImageUri(uri: string, options: ImageOptimizationOptions = {}): string {
    // 在实际应用中，这里会调用图片优化服务
    const params = new URLSearchParams();
    
    if (options.quality) {
      params.append('quality', options.quality.toString());
    }
    
    if (options.format) {
      params.append('format', options.format);
    }
    
    if (options.width) {
      params.append('width', options.width.toString());
    }
    
    if (options.height) {
      params.append('height', options.height.toString());
    }

    const queryString = params.toString();
    return queryString ? `${uri}?${queryString}` : uri;
  }

  static calculateImageSize(originalWidth: number, originalHeight: number, maxWidth: number, maxHeight: number): { width: number; height: number } {
    const aspectRatio = originalWidth / originalHeight;
    
    let newWidth = originalWidth;
    let newHeight = originalHeight;
    
    if (newWidth > maxWidth) {
      newWidth = maxWidth;
      newHeight = newWidth / aspectRatio;
    }
    
    if (newHeight > maxHeight) {
      newHeight = maxHeight;
      newWidth = newHeight * aspectRatio;
    }
    
    return {
      width: Math.round(newWidth),
      height: Math.round(newHeight)
    };
  }

  static isImageUri(uri: string): boolean {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
    const lowerUri = uri.toLowerCase();
    return imageExtensions.some(ext => lowerUri.includes(ext));
  }
}

export default ImageOptimizer;