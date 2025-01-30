import Flutter
import UIKit
import FirebaseCore

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // 初始化 Firebase
    FirebaseApp.configure()
    if FirebaseApp.app() != nil {
      print("Firebase initialized successfully!")
    } else {
      print("Firebase initialization failed!")
    }

    // 注册 Flutter 插件
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}
