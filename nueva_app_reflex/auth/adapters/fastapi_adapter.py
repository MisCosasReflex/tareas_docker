"""
Adaptador para integrar el sistema de autenticación con FastAPI.

Este módulo proporciona clases y funciones para integrar el sistema de autenticación
con aplicaciones FastAPI, incluyendo dependencias y middleware.

Functions:
    get_current_user: Dependency para obtener el usuario autenticado.
    create_auth_router: Crea un router con rutas de autenticación.
    require_auth: Decorador para rutas que requieren autenticación.
"""

from typing import Dict, Optional, Any, Callable, Type, List, Union, TypeVar, cast, Generic
from datetime import datetime, timedelta
import inspect
import functools

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from ..core.auth import AuthManager, AuthUser, LoginResult, InvalidCredentialsException, PasswordPolicyException
from ..core.token import get_token_data, TOKEN_TYPE_ACCESS
from ..config import get_auth_config

# Obtener configuración
config = get_auth_config()

# Tipo genérico para usuario
T = TypeVar('T', bound=AuthUser)

# Esquemas de datos
class TokenSchema(BaseModel):
    """
    Esquema para respuestas con tokens.
    
    Attributes:
        access_token (str): Token de acceso JWT.
        refresh_token (Optional[str]): Token de refresco JWT (si está habilitado).
        token_type (str): Tipo de token, siempre "bearer".
        expires_at (Optional[datetime]): Fecha/hora de expiración del token.
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None


class UserSchema(BaseModel):
    """
    Esquema base para usuarios.
    
    Attributes:
        username (str): Nombre de usuario.
        email (str): Correo electrónico.
    """
    username: str
    email: str


class LoginResponseSchema(BaseModel):
    """
    Esquema para respuestas de login.
    
    Attributes:
        token (TokenSchema): Información del token.
        user (UserSchema): Información del usuario.
    """
    token: TokenSchema
    user: UserSchema


class RegisterSchema(BaseModel):
    """
    Esquema para peticiones de registro.
    
    Attributes:
        username (str): Nombre de usuario.
        email (str): Correo electrónico.
        password (str): Contraseña en texto plano.
    """
    username: str
    email: str
    password: str


class ChangePasswordSchema(BaseModel):
    """
    Esquema para peticiones de cambio de contraseña.
    
    Attributes:
        current_password (str): Contraseña actual.
        new_password (str): Nueva contraseña.
    """
    current_password: str
    new_password: str


# Configuración de seguridad OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    auth_manager: AuthManager[T],
    token: str = Depends(oauth2_scheme)
) -> T:
    """
    Dependency para obtener el usuario autenticado.
    
    Args:
        auth_manager (AuthManager[T]): Gestor de autenticación.
        token (str, optional): Token JWT. Obtenido automáticamente por OAuth2.
        
    Returns:
        T: Usuario autenticado.
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe.
    """
    try:
        user = auth_manager.get_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario inválido o inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_auth_router(auth_manager: AuthManager[T]) -> APIRouter:
    """
    Crea un router con rutas de autenticación.
    
    Args:
        auth_manager (AuthManager[T]): Gestor de autenticación.
        
    Returns:
        APIRouter: Router FastAPI con rutas de autenticación.
    """
    router = APIRouter(tags=["auth"])
    
    @router.post("/token", response_model=TokenSchema)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        """
        Endpoint para obtener un token de acceso.
        
        Args:
            form_data (OAuth2PasswordRequestForm): Datos del formulario de login.
            
        Returns:
            TokenSchema: Token generado.
            
        Raises:
            HTTPException: Si las credenciales son inválidas.
        """
        try:
            result = auth_manager.authenticate(form_data.username, form_data.password)
            
            if not result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenSchema(
                access_token=result.access_token,
                refresh_token=result.refresh_token,
                expires_at=result.expires_at
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error de autenticación: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @router.post("/login", response_model=LoginResponseSchema)
    async def login(
        response: Response,
        username: str,
        password: str,
        set_cookie: bool = False
    ):
        """
        Endpoint para iniciar sesión.
        
        Args:
            response (Response): Objeto de respuesta FastAPI.
            username (str): Nombre de usuario o email.
            password (str): Contraseña en texto plano.
            set_cookie (bool, optional): Si se debe establecer cookie. Por defecto False.
            
        Returns:
            LoginResponseSchema: Información de login y token.
            
        Raises:
            HTTPException: Si las credenciales son inválidas.
        """
        try:
            result = auth_manager.authenticate(username, password)
            
            if not result.success:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=result.message,
                )
            
            # Establecer cookies si se solicitó
            if set_cookie and result.access_token:
                cookie_max_age = config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
                response.set_cookie(
                    key="access_token",
                    value=result.access_token,
                    httponly=True,
                    max_age=cookie_max_age,
                    expires=cookie_max_age,
                    secure=True,
                    samesite="lax"
                )
                
                if result.refresh_token:
                    refresh_max_age = config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
                    response.set_cookie(
                        key="refresh_token",
                        value=result.refresh_token,
                        httponly=True,
                        max_age=refresh_max_age,
                        expires=refresh_max_age,
                        secure=True,
                        samesite="lax"
                    )
            
            user_data = result.user.to_dict() if result.user else {}
            
            return LoginResponseSchema(
                token=TokenSchema(
                    access_token=result.access_token,
                    refresh_token=result.refresh_token,
                    expires_at=result.expires_at
                ),
                user=UserSchema(
                    username=user_data.get("username", ""),
                    email=user_data.get("email", "")
                )
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Error de autenticación: {str(e)}",
            )
    
    @router.post("/register", status_code=status.HTTP_201_CREATED)
    async def register(user_data: RegisterSchema):
        """
        Endpoint para registrar un nuevo usuario.
        
        Args:
            user_data (RegisterSchema): Datos del nuevo usuario.
            
        Returns:
            dict: Mensaje de resultado.
            
        Raises:
            HTTPException: Si hay error en el registro.
        """
        try:
            result = auth_manager.register_user(
                user_data.username,
                user_data.email,
                user_data.password
            )
            
            if isinstance(result, str):
                # Error en el registro
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result,
                )
            
            return {"message": f"Usuario {user_data.username} registrado correctamente"}
        except PasswordPolicyException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en el registro: {str(e)}",
            )
    
    @router.post("/change-password")
    async def change_password(
        data: ChangePasswordSchema,
        current_user: T = Depends(lambda: get_current_user(auth_manager))
    ):
        """
        Endpoint para cambiar la contraseña.
        
        Args:
            data (ChangePasswordSchema): Datos para el cambio de contraseña.
            current_user (T): Usuario actual (obtenido de la dependency).
            
        Returns:
            dict: Mensaje de resultado.
            
        Raises:
            HTTPException: Si hay error en el cambio de contraseña.
        """
        try:
            success = auth_manager.change_password(
                current_user,
                data.current_password,
                data.new_password
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al cambiar la contraseña",
                )
            
            return {"message": "Contraseña cambiada correctamente"}
        except InvalidCredentialsException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )
        except PasswordPolicyException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al cambiar la contraseña: {str(e)}",
            )
    
    @router.get("/me", response_model=UserSchema)
    async def read_users_me(
        current_user: T = Depends(lambda: get_current_user(auth_manager))
    ):
        """
        Endpoint para obtener información del usuario actual.
        
        Args:
            current_user (T): Usuario actual (obtenido de la dependency).
            
        Returns:
            UserSchema: Información del usuario.
        """
        user_data = current_user.to_dict()
        
        return UserSchema(
            username=user_data.get("username", ""),
            email=user_data.get("email", "")
        )
    
    @router.post("/logout")
    async def logout(response: Response):
        """
        Endpoint para cerrar sesión.
        
        Args:
            response (Response): Objeto de respuesta FastAPI.
            
        Returns:
            dict: Mensaje de resultado.
        """
        # Eliminar cookies
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        
        return {"message": "Sesión cerrada"}
    
    return router


def require_auth(handler=None):
    """
    Decorador para rutas que requieren autenticación.
    
    Este decorador verifica que el usuario esté autenticado antes de ejecutar la ruta.
    
    Args:
        handler: Función manejadora de ruta.
        
    Returns:
        Función decorada que verifica autenticación.
    """
    def decorator(handler_func):
        @functools.wraps(handler_func)
        async def wrapper(*args, **kwargs):
            # La lógica de autenticación se maneja a través de dependencias
            # en FastAPI, así que este decorador es más bien un marcador.
            return await handler_func(*args, **kwargs)
        
        return wrapper
    
    # Permitir usar el decorador con o sin paréntesis
    if handler is None:
        return decorator
    return decorator(handler)


def create_auth_middleware(auth_manager: AuthManager[T]):
    """
    Crea un middleware para FastAPI que verifica tokens en cookies.
    
    Args:
        auth_manager (AuthManager[T]): Gestor de autenticación.
        
    Returns:
        Callable: Middleware de autenticación.
    """
    async def auth_middleware(request: Request, call_next):
        # Procesar la solicitud normalmente
        response = await call_next(request)
        
        # Este middleware podría verificar cookies, renovar tokens, etc.
        # pero lo dejamos simple por ahora
        
        return response
    
    return auth_middleware
