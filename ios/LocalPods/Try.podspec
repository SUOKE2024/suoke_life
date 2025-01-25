Pod::Spec.new do |s|
  s.name         = "Try"
  s.version      = "2.1.1"
  s.summary      = "Handle Objective-C Exceptions with Swift"
  s.description  = "Handle Objective-C Exceptions with Swift"
  s.homepage     = "https://github.com/RxSwiftCommunity/Try"
  s.license      = { :type => "MIT", :file => "LICENSE" }
  s.author       = { "Adam Sharp" => "adam@sharplet.me" }
  s.platform     = :ios, "9.0"
  s.source       = { :http => "https://mirrors.cloud.tencent.com/repository/Try/v2.1.1.zip" }
  s.source_files = "Sources/**/*.{h,m,swift}"
  s.swift_version = "5.0"
end 