"""
oauth2_client - 索克生活项目模块
"""

from typing import Dict, Any, Optional
import asyncio
import base64
import hashlib
import httpx
import secrets

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OAuth2 客户端示例

展示如何使用 API 网关的 OAuth2 认证功能。
"""



class OAuth2Client:
    """OAuth2 客户端"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.token_type = "Bearer"
    
    def _get_basic_auth_header(self) -> str:
        """获取基本认证头"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _generate_pkce_challenge(self) -> tuple[str, str]:
        """生成 PKCE 挑战"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        return code_verifier, code_challenge
    
    def get_authorization_url(
        self,
        redirect_uri: str,
        scope: str = "read write",
        state: str = None,
        use_pkce: bool = True
    ) -> tuple[str, Optional[str]]:
        """获取授权 URL"""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
        }
        
        if state:
            params["state"] = state
        
        code_verifier = None
        if use_pkce:
            code_verifier, code_challenge = self._generate_pkce_challenge()
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        
        url = f"{self.base_url}/oauth2/authorize?" + urllib.parse.urlencode(params)
        return url, code_verifier
    
    async def exchange_code_for_token(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: str = None
    ) -> Dict[str, Any]:
        """用授权码换取访问令牌"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        
        if code_verifier:
            data["code_verifier"] = code_verifier
        
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data=data,
                headers=headers,
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_type = token_data.get("token_type", "Bearer")
                return token_data
            else:
                raise Exception(f"Token exchange failed: {response.text}")
    
    async def client_credentials_flow(self, scope: str = "read") -> Dict[str, Any]:
        """客户端凭证流程"""
        data = {
            "grant_type": "client_credentials",
            "scope": scope,
        }
        
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data=data,
                headers=headers,
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.token_type = token_data.get("token_type", "Bearer")
                return token_data
            else:
                raise Exception(f"Client credentials flow failed: {response.text}")
    
    async def refresh_access_token(self) -> Dict[str, Any]:
        """刷新访问令牌"""
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }
        
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/token",
                data=data,
                headers=headers,
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                if "refresh_token" in token_data:
                    self.refresh_token = token_data["refresh_token"]
                return token_data
            else:
                raise Exception(f"Token refresh failed: {response.text}")
    
    async def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        if not self.access_token:
            raise Exception("No access token available")
        
        headers = {
            "Authorization": f"{self.token_type} {self.access_token}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/oauth2/userinfo",
                headers=headers,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Get user info failed: {response.text}")
    
    async def introspect_token(self, token: str = None) -> Dict[str, Any]:
        """检查令牌"""
        token = token or self.access_token
        if not token:
            raise Exception("No token to introspect")
        
        data = {
            "token": token,
        }
        
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/introspect",
                data=data,
                headers=headers,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Token introspection failed: {response.text}")
    
    async def revoke_token(self, token: str = None) -> bool:
        """撤销令牌"""
        token = token or self.access_token
        if not token:
            raise Exception("No token to revoke")
        
        data = {
            "token": token,
        }
        
        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth2/revoke",
                data=data,
                headers=headers,
            )
            
            if response.status_code == 200:
                if token == self.access_token:
                    self.access_token = None
                return True
            else:
                raise Exception(f"Token revocation failed: {response.text}")
    
    async def make_authenticated_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """发送认证请求"""
        if not self.access_token:
            raise Exception("No access token available")
        
        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"{self.token_type} {self.access_token}"
        kwargs["headers"] = headers
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            
            # 如果令牌过期，尝试刷新
            if response.status_code == 401 and self.refresh_token:
                try:
                    await self.refresh_access_token()
                    headers["Authorization"] = f"{self.token_type} {self.access_token}"
                    response = await client.request(method, url, **kwargs)
                except Exception:
                    pass
            
            return response

async def demo_client_credentials():
    """演示客户端凭证流程"""
    print("=== 客户端凭证流程演示 ===")
    
    client = OAuth2Client(
        base_url="http://localhost:8000",
        client_id="demo_client",
        client_secret="demo_secret"
    )
    
    try:
        # 获取访问令牌
        print("1. 获取访问令牌...")
        token_data = await client.client_credentials_flow(scope="read write")
        print(f"✓ 获取到访问令牌: {token_data['access_token'][:20]}...")
        print(f"  令牌类型: {token_data['token_type']}")
        print(f"  过期时间: {token_data.get('expires_in', 'N/A')} 秒")
        print(f"  作用域: {token_data.get('scope', 'N/A')}")
        
        # 检查令牌
        print("\n2. 检查令牌...")
        introspect_data = await client.introspect_token()
        print(f"✓ 令牌有效: {introspect_data.get('active', False)}")
        print(f"  客户端ID: {introspect_data.get('client_id', 'N/A')}")
        print(f"  作用域: {introspect_data.get('scope', 'N/A')}")
        
        # 发送认证请求
        print("\n3. 发送认证请求...")
        response = await client.make_authenticated_request(
            "GET",
            "http://localhost:8000/api/v1/protected"
        )
        print(f"✓ 请求状态: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.json()}")
        
        # 撤销令牌
        print("\n4. 撤销令牌...")
        await client.revoke_token()
        print("✓ 令牌已撤销")
        
        # 验证令牌已失效
        print("\n5. 验证令牌已失效...")
        try:
            await client.introspect_token()
        except Exception as e:
            print(f"✓ 令牌已失效: {e}")
    
    except Exception as e:
        print(f"✗ 错误: {e}")

async def demo_authorization_code():
    """演示授权码流程"""
    print("=== 授权码流程演示 ===")
    
    client = OAuth2Client(
        base_url="http://localhost:8000",
        client_id="demo_client",
        client_secret="demo_secret"
    )
    
    try:
        # 生成授权 URL
        redirect_uri = "http://localhost:3000/callback"
        state = secrets.token_urlsafe(32)
        
        print("1. 生成授权 URL...")
        auth_url, code_verifier = client.get_authorization_url(
            redirect_uri=redirect_uri,
            scope="read write profile",
            state=state,
            use_pkce=True
        )
        
        print(f"✓ 授权 URL: {auth_url}")
        print(f"  状态参数: {state}")
        print(f"  PKCE 验证码: {code_verifier[:20]}...")
        
        # 模拟用户授权（实际应用中用户会在浏览器中完成）
        print("\n2. 模拟用户授权...")
        print("   在实际应用中，用户会被重定向到授权服务器")
        print("   用户登录并授权后，会被重定向回应用")
        
        # 模拟获取授权码（实际应用中从回调 URL 中获取）
        authorization_code = "demo_auth_code_12345"
        print(f"   模拟授权码: {authorization_code}")
        
        # 用授权码换取访问令牌
        print("\n3. 用授权码换取访问令牌...")
        try:
            token_data = await client.exchange_code_for_token(
                code=authorization_code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier
            )
            print(f"✓ 获取到访问令牌: {token_data['access_token'][:20]}...")
            print(f"  刷新令牌: {token_data.get('refresh_token', 'N/A')[:20]}...")
            print(f"  过期时间: {token_data.get('expires_in', 'N/A')} 秒")
        except Exception as e:
            print(f"✗ 令牌交换失败: {e}")
            print("   注意：这是演示代码，授权码是模拟的")
            return
        
        # 获取用户信息
        print("\n4. 获取用户信息...")
        try:
            user_info = await client.get_user_info()
            print(f"✓ 用户信息: {user_info}")
        except Exception as e:
            print(f"✗ 获取用户信息失败: {e}")
        
        # 刷新访问令牌
        print("\n5. 刷新访问令牌...")
        try:
            new_token_data = await client.refresh_access_token()
            print(f"✓ 新访问令牌: {new_token_data['access_token'][:20]}...")
        except Exception as e:
            print(f"✗ 刷新令牌失败: {e}")
    
    except Exception as e:
        print(f"✗ 错误: {e}")

async def demo_openid_connect():
    """演示 OpenID Connect"""
    print("=== OpenID Connect 演示 ===")
    
    try:
        # 获取 OpenID 配置
        print("1. 获取 OpenID 配置...")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://localhost:8000/oauth2/.well-known/openid_configuration"
            )
            
            if response.status_code == 200:
                config = response.json()
                print("✓ OpenID 配置:")
                for key, value in config.items():
                    print(f"  {key}: {value}")
            else:
                print(f"✗ 获取配置失败: {response.text}")
                return
        
        # 获取 JWKS
        print("\n2. 获取 JWKS...")
        jwks_uri = config.get("jwks_uri")
        if jwks_uri:
            response = await client.get(jwks_uri)
            if response.status_code == 200:
                jwks = response.json()
                print(f"✓ JWKS: {len(jwks.get('keys', []))} 个密钥")
            else:
                print(f"✗ 获取 JWKS 失败: {response.text}")
    
    except Exception as e:
        print(f"✗ 错误: {e}")

async def interactive_demo():
    """交互式演示"""
    print("OAuth2 客户端示例")
    print("1. 客户端凭证流程")
    print("2. 授权码流程")
    print("3. OpenID Connect")
    print("4. 全部演示")
    
    choice = input("选择演示 (1-4): ").strip()
    
    if choice == "1":
        await demo_client_credentials()
    elif choice == "2":
        await demo_authorization_code()
    elif choice == "3":
        await demo_openid_connect()
    elif choice == "4":
        await demo_client_credentials()
        print("\n" + "="*50 + "\n")
        await demo_authorization_code()
        print("\n" + "="*50 + "\n")
        await demo_openid_connect()
    else:
        print("无效选择")

async def main():
    """主函数"""
    await interactive_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被中断") 