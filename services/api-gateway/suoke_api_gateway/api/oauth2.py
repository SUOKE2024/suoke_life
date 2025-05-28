#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
OAuth2/OIDC API 端点

提供完整的 OAuth2 授权服务和 OIDC 协议支持。
"""

from typing import Dict, Any, Optional
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..services.oauth2_provider import get_oauth2_provider, OAuth2Provider
from ..core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/oauth2", tags=["oauth2"])
security = HTTPBearer(auto_error=False)


@router.get("/.well-known/openid_configuration")
async def openid_configuration(
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    OpenID Connect 发现端点
    
    返回 OIDC 提供者的配置信息。
    """
    return oauth2_provider.get_openid_configuration()


@router.get("/jwks")
async def jwks(
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    JSON Web Key Set 端点
    
    返回用于验证 JWT 令牌的公钥。
    """
    return oauth2_provider.get_jwks()


@router.get("/authorize")
async def authorize(
    request: Request,
    response_type: str = Query(..., description="响应类型"),
    client_id: str = Query(..., description="客户端ID"),
    redirect_uri: str = Query(..., description="重定向URI"),
    scope: str = Query(..., description="权限范围"),
    state: Optional[str] = Query(None, description="状态参数"),
    code_challenge: Optional[str] = Query(None, description="PKCE 代码挑战"),
    code_challenge_method: Optional[str] = Query(None, description="PKCE 挑战方法"),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
):
    """
    OAuth2 授权端点
    
    处理授权请求，返回授权页面或直接重定向。
    """
    try:
        # 验证客户端
        client = oauth2_provider.get_client(client_id)
        if not client or not client.is_active:
            raise HTTPException(status_code=400, detail="Invalid client")
        
        # 验证重定向URI
        if not client.validate_redirect_uri(redirect_uri):
            raise HTTPException(status_code=400, detail="Invalid redirect URI")
        
        # 验证响应类型
        if not client.validate_response_type(response_type):
            raise HTTPException(status_code=400, detail="Unsupported response type")
        
        # 这里应该显示授权页面让用户确认
        # 为了演示，我们直接模拟用户同意授权
        user_id = "demo_user_123"  # 实际应该从会话中获取
        
        # 处理授权请求
        result = oauth2_provider.handle_authorization_request(
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type=response_type,
            scope=scope,
            user_id=user_id,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        
        if "error" in result:
            # 构建错误重定向URL
            error_params = {"error": result["error"]}
            if state:
                error_params["state"] = state
            
            from urllib.parse import urlencode
            error_url = f"{redirect_uri}?{urlencode(error_params)}"
            return RedirectResponse(url=error_url)
        
        # 重定向到客户端
        return RedirectResponse(url=result["redirect_url"])
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authorization request failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/authorize/consent")
async def authorization_consent_page(
    response_type: str = Query(...),
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    scope: str = Query(...),
    state: Optional[str] = Query(None),
    code_challenge: Optional[str] = Query(None),
    code_challenge_method: Optional[str] = Query(None),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
):
    """
    授权同意页面
    
    显示授权同意页面，让用户确认是否授权。
    """
    client = oauth2_provider.get_client(client_id)
    if not client:
        raise HTTPException(status_code=400, detail="Invalid client")
    
    # 构建授权页面HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>授权确认 - 索克生活</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .logo {{ text-align: center; margin-bottom: 30px; }}
            .app-info {{ background: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 20px; }}
            .permissions {{ margin: 20px 0; }}
            .permission {{ padding: 10px; border-left: 3px solid #007bff; margin: 10px 0; background: #f8f9fa; }}
            .buttons {{ text-align: center; margin-top: 30px; }}
            .btn {{ padding: 12px 30px; margin: 0 10px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
            .btn-primary {{ background: #007bff; color: white; }}
            .btn-secondary {{ background: #6c757d; color: white; }}
            .btn:hover {{ opacity: 0.9; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>🏥 索克生活</h1>
            </div>
            
            <div class="app-info">
                <h3>应用授权请求</h3>
                <p><strong>应用名称:</strong> {client.client_name}</p>
                <p><strong>客户端ID:</strong> {client_id}</p>
            </div>
            
            <div class="permissions">
                <h4>请求的权限:</h4>
                <div class="permission">📋 基本信息访问 (profile)</div>
                <div class="permission">🏥 健康数据访问 (health_data)</div>
                <div class="permission">🔐 身份验证 (openid)</div>
            </div>
            
            <p>该应用请求访问您的索克生活账户。您是否同意授权？</p>
            
            <div class="buttons">
                <form method="post" action="/oauth2/authorize/approve" style="display: inline;">
                    <input type="hidden" name="response_type" value="{response_type}">
                    <input type="hidden" name="client_id" value="{client_id}">
                    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                    <input type="hidden" name="scope" value="{scope}">
                    <input type="hidden" name="state" value="{state or ''}">
                    <input type="hidden" name="code_challenge" value="{code_challenge or ''}">
                    <input type="hidden" name="code_challenge_method" value="{code_challenge_method or ''}">
                    <button type="submit" class="btn btn-primary">同意授权</button>
                </form>
                
                <form method="post" action="/oauth2/authorize/deny" style="display: inline;">
                    <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                    <input type="hidden" name="state" value="{state or ''}">
                    <button type="submit" class="btn btn-secondary">拒绝</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.post("/authorize/approve")
async def approve_authorization(
    response_type: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    state: Optional[str] = Form(None),
    code_challenge: Optional[str] = Form(None),
    code_challenge_method: Optional[str] = Form(None),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
):
    """
    批准授权请求
    """
    # 这里应该从会话中获取用户ID
    user_id = "demo_user_123"
    
    result = oauth2_provider.handle_authorization_request(
        client_id=client_id,
        redirect_uri=redirect_uri,
        response_type=response_type,
        scope=scope,
        user_id=user_id,
        state=state,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )
    
    if "error" in result:
        from urllib.parse import urlencode
        error_params = {"error": result["error"]}
        if state:
            error_params["state"] = state
        error_url = f"{redirect_uri}?{urlencode(error_params)}"
        return RedirectResponse(url=error_url)
    
    return RedirectResponse(url=result["redirect_url"])


@router.post("/authorize/deny")
async def deny_authorization(
    redirect_uri: str = Form(...),
    state: Optional[str] = Form(None),
):
    """
    拒绝授权请求
    """
    from urllib.parse import urlencode
    error_params = {"error": "access_denied"}
    if state:
        error_params["state"] = state
    
    error_url = f"{redirect_uri}?{urlencode(error_params)}"
    return RedirectResponse(url=error_url)


@router.post("/token")
async def token_endpoint(
    grant_type: str = Form(..., description="授权类型"),
    client_id: str = Form(..., description="客户端ID"),
    client_secret: str = Form(..., description="客户端密钥"),
    code: Optional[str] = Form(None, description="授权码"),
    redirect_uri: Optional[str] = Form(None, description="重定向URI"),
    refresh_token: Optional[str] = Form(None, description="刷新令牌"),
    scope: Optional[str] = Form(None, description="权限范围"),
    code_verifier: Optional[str] = Form(None, description="PKCE 代码验证器"),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    OAuth2 令牌端点
    
    处理令牌请求，支持多种授权类型。
    """
    try:
        if grant_type == "authorization_code":
            # 授权码流程
            if not code or not redirect_uri:
                raise HTTPException(status_code=400, detail="Missing required parameters")
            
            result = oauth2_provider.exchange_code_for_tokens(
                client_id=client_id,
                client_secret=client_secret,
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=code_verifier,
            )
        
        elif grant_type == "refresh_token":
            # 刷新令牌流程
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Missing refresh_token")
            
            result = oauth2_provider.refresh_access_token(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token,
                scope=scope,
            )
        
        elif grant_type == "client_credentials":
            # 客户端凭证流程
            result = oauth2_provider.client_credentials_grant(
                client_id=client_id,
                client_secret=client_secret,
                scope=scope,
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported grant type")
        
        if "error" in result:
            error_code = result["error"]
            if error_code == "invalid_client":
                raise HTTPException(status_code=401, detail="Invalid client credentials")
            elif error_code == "invalid_grant":
                raise HTTPException(status_code=400, detail="Invalid grant")
            elif error_code == "invalid_scope":
                raise HTTPException(status_code=400, detail="Invalid scope")
            else:
                raise HTTPException(status_code=400, detail=error_code)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token request failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/userinfo")
async def userinfo_endpoint(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    OAuth2 用户信息端点
    
    返回当前访问令牌对应的用户信息。
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing access token")
    
    access_token = credentials.credentials
    
    try:
        userinfo = oauth2_provider.get_userinfo(access_token)
        
        if "error" in userinfo:
            raise HTTPException(status_code=401, detail="Invalid access token")
        
        return userinfo
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Userinfo request failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/revoke")
async def revoke_token(
    token: str = Form(..., description="要撤销的令牌"),
    token_type_hint: Optional[str] = Form(None, description="令牌类型提示"),
    client_id: str = Form(..., description="客户端ID"),
    client_secret: str = Form(..., description="客户端密钥"),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    OAuth2 令牌撤销端点
    
    撤销访问令牌或刷新令牌。
    """
    try:
        # 验证客户端
        if not oauth2_provider.validate_client(client_id, client_secret):
            raise HTTPException(status_code=401, detail="Invalid client credentials")
        
        # 撤销令牌
        revoked = False
        
        # 尝试撤销访问令牌
        if token in oauth2_provider.access_tokens:
            access_token_obj = oauth2_provider.access_tokens[token]
            if access_token_obj.client_id == client_id:
                del oauth2_provider.access_tokens[token]
                revoked = True
        
        # 尝试撤销刷新令牌
        if token in oauth2_provider.refresh_tokens:
            refresh_token_obj = oauth2_provider.refresh_tokens[token]
            if refresh_token_obj.client_id == client_id:
                del oauth2_provider.refresh_tokens[token]
                revoked = True
        
        # 根据 RFC 7009，即使令牌不存在也应该返回成功
        return {"revoked": revoked}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token revocation failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/introspect")
async def introspect_token(
    token: str = Query(..., description="要检查的令牌"),
    token_type_hint: Optional[str] = Query(None, description="令牌类型提示"),
    client_id: str = Query(..., description="客户端ID"),
    client_secret: str = Query(..., description="客户端密钥"),
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    OAuth2 令牌内省端点
    
    检查令牌的有效性和元数据。
    """
    try:
        # 验证客户端
        if not oauth2_provider.validate_client(client_id, client_secret):
            raise HTTPException(status_code=401, detail="Invalid client credentials")
        
        # 检查访问令牌
        access_token_obj = oauth2_provider.validate_access_token(token)
        if access_token_obj:
            return {
                "active": True,
                "client_id": access_token_obj.client_id,
                "username": access_token_obj.user_id,
                "scope": access_token_obj.scope,
                "token_type": access_token_obj.token_type,
                "exp": int(access_token_obj.expires_at),
                "iat": int(access_token_obj.expires_at - 3600),  # 假设1小时有效期
            }
        
        # 检查刷新令牌
        if token in oauth2_provider.refresh_tokens:
            refresh_token_obj = oauth2_provider.refresh_tokens[token]
            if not refresh_token_obj.is_expired():
                return {
                    "active": True,
                    "client_id": refresh_token_obj.client_id,
                    "username": refresh_token_obj.user_id,
                    "scope": refresh_token_obj.scope,
                    "token_type": "refresh_token",
                    "exp": int(refresh_token_obj.expires_at),
                }
        
        # 令牌无效或过期
        return {"active": False}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token introspection failed", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/clients")
async def list_clients(
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    列出所有 OAuth2 客户端
    
    Returns:
        客户端列表
    """
    try:
        clients = []
        for client_id, client in oauth2_provider.clients.items():
            clients.append({
                "client_id": client.client_id,
                "client_name": client.client_name,
                "redirect_uris": client.redirect_uris,
                "grant_types": client.grant_types,
                "response_types": client.response_types,
                "scope": client.scope,
                "is_active": client.is_active,
                "created_at": client.created_at,
            })
        
        return {
            "status": "success",
            "clients": clients,
            "total": len(clients),
        }
    
    except Exception as e:
        logger.error("Failed to list OAuth2 clients", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def oauth2_stats(
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    获取 OAuth2 统计信息
    
    Returns:
        统计信息
    """
    try:
        stats = oauth2_provider.get_stats()
        
        return {
            "status": "success",
            "stats": stats,
        }
    
    except Exception as e:
        logger.error("Failed to get OAuth2 stats", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_expired_tokens(
    oauth2_provider: OAuth2Provider = Depends(get_oauth2_provider),
) -> Dict[str, Any]:
    """
    清理过期令牌
    
    Returns:
        清理结果
    """
    try:
        oauth2_provider.cleanup_expired_tokens()
        
        return {
            "status": "success",
            "message": "Expired tokens cleaned up successfully",
        }
    
    except Exception as e:
        logger.error("Failed to cleanup expired tokens", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 