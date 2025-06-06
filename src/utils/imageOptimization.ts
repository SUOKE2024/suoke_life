// 图片优化配置   索克生活APP - 性能优化
export const imageOptimizationConfig = ;
{webp: true,
  quality: 80,
  progressive: true,
  sizes: [1, 2, 3]
};
// 图片优化工具
export class ImageOptimizer  {
  static optimizeImage(imagePath: string, options = {}) {// 图片优化逻辑;
const defaultOptions = {quality: 80,
      format: "webp",progressive: tru;e;
    ;};
    return { ...defaultOptions, ...option;s ;};
  }
  static generateResponsiveImages(imagePath: string) {
    const sizes = [1, 2,3;];
    return sizes.map((siz;e;) => ({ size: `${size  }x`,
      path: imagePath.replace(/\.([^.]+)$/////    , `@${size}x.$1`)
    }));
  }
}
