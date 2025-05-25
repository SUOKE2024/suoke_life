/*
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

#import <Foundation/Foundation.h>

#import "RCTModuleProviders.h"
#import <ReactCommon/RCTTurboModule.h>
#import <React/RCTLog.h>

@implementation RCTModuleProviders

+ (NSDictionary<NSString *, id<RCTModuleProvider>> *)moduleProviders
{
  static NSDictionary<NSString *, id<RCTModuleProvider>> *providers = nil;
  static dispatch_once_t onceToken;

  dispatch_once(&onceToken, ^{
    NSDictionary<NSString *, NSString *> * moduleMapping = @{
      			@"VisionCamera": @"VisionCameraProvider", // suoke-life
			@"RNVoice": @"RNVoiceProvider", // suoke-life
			@"RNVectorIcons": @"RNVectorIconsProvider", // suoke-life
			@"RNSVG": @"RNSVGProvider", // suoke-life
			@"RNReanimated": @"RNReanimatedProvider", // suoke-life
			@"RNScreens": @"RNScreensProvider", // suoke-life
			@"RNSafeAreaContext": @"RNSafeAreaContextProvider", // suoke-life
			@"AsyncStorage": @"AsyncStorageProvider", // suoke-life
			@"DateTimePicker": @"DateTimePickerProvider", // suoke-life
			@"Slider": @"SliderProvider", // suoke-life
			@"RNMMKV": @"RNMMKVProvider", // suoke-life
    };

    NSMutableDictionary *dict = [[NSMutableDictionary alloc] initWithCapacity:moduleMapping.count];

    for (NSString *key in moduleMapping) {
      NSString * moduleProviderName = moduleMapping[key];
      Class klass = NSClassFromString(moduleProviderName);
      if (!klass) {
        RCTLogError(@"Module provider %@ cannot be found in the runtime", moduleProviderName);
        continue;
      }

      id instance = [klass new];
      if (![instance respondsToSelector:@selector(getTurboModule:)]) {
        RCTLogError(@"Module provider %@ does not conform to RCTModuleProvider", moduleProviderName);
        continue;
      }

      [dict setObject:instance forKey:key];
    }

    providers = dict;
  });

  return providers;
}

@end
