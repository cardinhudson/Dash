#!/usr/bin/env python3
"""
Sistema de autenticação simplificado para Streamlit Cloud
Usa secrets.toml ou variáveis de ambiente - sem arquivos JSON
"""
import streamlit as st
import hashlib
from datetime import datetime

def criar_hash_senha(senha):
    """Cria um hash SHA-256 da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

def get_usuarios_cloud():
    """Carrega usuários do sistema de secrets do Streamlit Cloud"""
    try:
        # Tentar carregar do secrets.toml (Streamlit Cloud)
        if hasattr(st, 'secrets') and 'usuarios' in st.secrets:
            return dict(st.secrets.usuarios)
        else:
            # Fallback: usuários hardcoded para desenvolvimento
            return {
                'admin': {
                    'senha': criar_hash_senha('admin123'),
                    'status': 'aprovado',
                    'tipo': 'administrador'
                },
                'demo': {
                    'senha': criar_hash_senha('demo123'),
                    'status': 'aprovado',
                    'tipo': 'usuario'
                }
            }
    except Exception as e:
        # Em caso de erro, retornar usuários básicos
        return {
            'admin': {
                'senha': criar_hash_senha('admin123'),
                'status': 'aprovado',
                'tipo': 'administrador'
            }
        }

def verificar_login_simples(usuario, senha):
    """Verifica se o login é válido"""
    usuarios = get_usuarios_cloud()
    
    if usuario in usuarios:
        senha_hash = criar_hash_senha(senha)
        if usuarios[usuario]['senha'] == senha_hash:
            if usuarios[usuario].get('status') == 'aprovado':
                return True
            else:
                st.error("⏳ Conta pendente de aprovação.")
                return False
        else:
            st.error("❌ Senha incorreta!")
            return False
    else:
        st.error("❌ Usuário não encontrado!")
        return False

def eh_administrador_simples():
    """Verifica se o usuário atual é administrador"""
    if 'usuario_nome' not in st.session_state:
        return False
    
    usuarios = get_usuarios_cloud()
    usuario_atual = st.session_state.usuario_nome
    
    if usuario_atual in usuarios:
        return usuarios[usuario_atual].get('tipo') == 'administrador'
    
    return usuario_atual == 'admin'  # Fallback

def fazer_logout_simples():
    """Faz logout do usuário"""
    keys_to_remove = ['usuario_nome', 'usuario_logado', 'login_time']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def verificar_autenticacao_simples():
    """Verifica se o usuário está autenticado - versão simplificada"""
    
    # Verificar se já está logado
    if 'usuario_nome' in st.session_state:
        return True
    
    # Mostrar tela de login
    tela_login_simples()
    st.stop()

def exibir_header_usuario_simples():
    """Exibe o header com informações do usuário"""
    if 'usuario_nome' in st.session_state:
        st.sidebar.markdown("---")
        st.sidebar.write(f"👤 **Usuário:** {st.session_state['usuario_nome']}")
        
        if eh_administrador_simples():
            st.sidebar.write("👑 **Administrador**")
        else:
            st.sidebar.write("👥 **Usuário**")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            fazer_logout_simples()

def tela_login_simples():
    """Exibe a tela de login simplificada"""
    
    # Detectar ambiente
    try:
        base_url = st.get_option('server.baseUrlPath') or ''
        is_cloud = 'share.streamlit.io' in base_url
    except Exception:
        is_cloud = False
    
    st.title("🔐 Login - Dashboard KE5Z")
    
    if is_cloud:
        st.info("☁️ **Streamlit Cloud** - Sistema de autenticação simplificado")
    else:
        st.info("💻 **Modo Local** - Sistema de autenticação simplificado")
    
    st.markdown("---")
    
    # Formulário de login
    with st.form("login_form_simple"):
        st.subheader("📝 Fazer Login")
        
        usuario = st.text_input("Usuário:", placeholder="Digite seu usuário")
        senha = st.text_input("Senha:", type="password", placeholder="Digite sua senha")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("🔓 Entrar", use_container_width=True):
                if usuario and senha:
                    if verificar_login_simples(usuario, senha):
                        st.session_state.usuario_nome = usuario
                        st.session_state.usuario_logado = True
                        st.session_state.login_time = datetime.now().isoformat()
                        st.success(f"✅ Login realizado! Bem-vindo, {usuario}!")
                        st.rerun()
                else:
                    st.error("❌ Preencha usuário e senha!")
        
        with col2:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()
    
    # Informações de usuários disponíveis
    st.markdown("---")
    st.subheader("👥 Usuários Disponíveis")
    
    usuarios = get_usuarios_cloud()
    
    # Mostrar usuários de exemplo (sem mostrar senhas)
    if is_cloud:
        st.info("☁️ **No Streamlit Cloud:** Usuários são configurados via secrets")
    else:
        st.info("💻 **Usuários de demonstração:**")
        
    for usuario, dados in usuarios.items():
        tipo_icon = "👑" if dados.get('tipo') == 'administrador' else "👥"
        tipo_text = "Administrador" if dados.get('tipo') == 'administrador' else "Usuário"
        st.write(f"{tipo_icon} **{usuario}** - {tipo_text}")
    
    # Instruções
    st.markdown("---")
    st.subheader("💡 Como usar")
    
    with st.expander("📋 Instruções"):
        st.markdown("""
        ### 🔐 **Para Streamlit Cloud:**
        1. Configure secrets em: `Settings > Secrets`
        2. Adicione usuários no formato:
        ```toml
        [usuarios.admin]
        senha = "hash_da_senha"
        status = "aprovado"
        tipo = "administrador"
        
        [usuarios.usuario1]
        senha = "hash_da_senha"
        status = "aprovado"
        tipo = "usuario"
        ```
        
        ### 💻 **Para uso local:**
        - Use os usuários de demonstração
        - Ou configure secrets localmente
        
        ### 🔑 **Senhas padrão (desenvolvimento):**
        - **admin**: admin123
        - **demo**: demo123
        """)

def adicionar_usuario_simples(nome_usuario, senha, tipo='usuario'):
    """Função para adicionar usuários (apenas para desenvolvimento local)"""
    if 'usuarios_temp' not in st.session_state:
        st.session_state.usuarios_temp = {}
    
    st.session_state.usuarios_temp[nome_usuario] = {
        'senha': criar_hash_senha(senha),
        'status': 'aprovado',
        'tipo': tipo,
        'criado_em': datetime.now().isoformat()
    }
    
    return True

# Funções de compatibilidade com o código existente
def verificar_autenticacao():
    """Compatibilidade com código existente"""
    return verificar_autenticacao_simples()

def exibir_header_usuario():
    """Compatibilidade com código existente"""
    return exibir_header_usuario_simples()

def eh_administrador():
    """Compatibilidade com código existente"""
    return eh_administrador_simples()

def verificar_status_aprovado(username):
    """Compatibilidade com código existente"""
    usuarios = get_usuarios_cloud()
    if username in usuarios:
        return usuarios[username].get('status') == 'aprovado'
    return False
