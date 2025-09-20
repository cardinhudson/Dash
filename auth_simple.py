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
    """Carrega usuários do sistema de secrets do Streamlit Cloud OU usuarios.json local"""
    import json
    import os
    
    try:
        # PRIORIDADE 1: Tentar carregar do arquivo usuarios.json (local)
        if os.path.exists('usuarios.json'):
            with open('usuarios.json', 'r', encoding='utf-8') as f:
                usuarios_json = json.load(f)
                # Converter formato se necessário (adicionar tipo se não existir)
                for usuario, dados in usuarios_json.items():
                    if 'tipo' not in dados:
                        # Se não tem tipo, admin é administrador, outros são usuários
                        dados['tipo'] = 'administrador' if usuario == 'admin' else 'usuario'
                return usuarios_json
        
        # PRIORIDADE 2: Tentar carregar do secrets.toml (Streamlit Cloud)
        elif hasattr(st, 'secrets') and 'usuarios' in st.secrets:
            return dict(st.secrets.usuarios)
        
        # FALLBACK: usuários hardcoded para desenvolvimento
        else:
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
        
        # Mostrar modo de operação atual
        modo_atual = st.session_state.get('modo_operacao', 'cloud')
        if modo_atual == 'cloud':
            st.sidebar.success("⚙️ **Modo:** ☁️ Cloud (Otimizado)")
        else:
            st.sidebar.info("⚙️ **Modo:** 💻 Completo")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            fazer_logout_simples()

def tela_login_simples():
    """Exibe a tela de login com seleção de tipo de usuário"""
    
    st.title("🔐 Login - Dashboard KE5Z")
    st.info("💻 **Sistema de Autenticação Inteligente**")
    
    # Seleção do tipo de usuário
    st.markdown("---")
    st.subheader("👤 Tipo de Usuário")
    
    tipo_login = st.radio(
        "Como você deseja fazer login?",
        options=["usuario", "admin"],
        format_func=lambda x: {
            "usuario": "👥 Usuário Comum - Acesso padrão com modo otimizado",
            "admin": "👑 Administrador - Acesso completo com escolha de modo"
        }[x],
        index=0,
        help="Escolha seu tipo de acesso para ver o formulário apropriado."
    )
    
    st.markdown("---")
    
    # LOGIN PARA USUÁRIO COMUM
    if tipo_login == "usuario":
        st.subheader("👥 Login de Usuário Comum")
        st.info("🎯 **Modo Automático:** ☁️ Cloud (Otimizado)\n• Melhor performance\n• Dados otimizados\n• Experiência rápida")
        
        with st.form("login_usuario"):
            usuario = st.text_input("👤 Usuário:", placeholder="Digite seu usuário")
            senha = st.text_input("🔐 Senha:", type="password", placeholder="Digite sua senha")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🔓 Entrar", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Limpar", use_container_width=True):
                    st.rerun()
        
        if submitted:
            if usuario and senha:
                if verificar_login_simples(usuario, senha):
                    # Verificar se realmente é usuário comum
                    usuarios = get_usuarios_cloud()
                    if usuario in usuarios and usuarios[usuario].get('tipo') == 'administrador':
                        st.warning("⚠️ **Você é administrador!** Use o login de admin para ter acesso completo.")
                        st.info("💡 Selecione 'Administrador' acima para ter acesso às opções avançadas.")
                    else:
                        # Login de usuário comum aprovado
                        st.session_state.usuario_nome = usuario
                        st.session_state.usuario_logado = True
                        st.session_state.login_time = datetime.now().isoformat()
                        st.session_state.modo_operacao = "cloud"  # Sempre cloud para usuários
                        
                        st.success(f"✅ Login realizado! Bem-vindo, {usuario}!")
                        st.success("⚙️ **Modo aplicado:** ☁️ Cloud (Otimizado)")
                        st.rerun()
            else:
                st.error("❌ Preencha usuário e senha!")
    
    # LOGIN PARA ADMINISTRADOR
    else:
        st.subheader("👑 Login de Administrador")
        st.info("🎛️ **Controle Total:** Escolha seu modo de operação")
        
        with st.form("login_admin"):
            usuario = st.text_input("👤 Usuário:", placeholder="Digite seu usuário de admin")
            senha = st.text_input("🔐 Senha:", type="password", placeholder="Digite sua senha de admin")
            
            st.markdown("---")
            st.subheader("⚙️ Modo de Operação")
            
            modo_operacao = st.radio(
                "Escolha o modo:",
                options=["cloud", "completo"],
                format_func=lambda x: {
                    "cloud": "☁️ Cloud (Otimizado) - Recomendado",
                    "completo": "💻 Completo (Todos os dados)"
                }[x],
                index=0,
                help="Cloud: Dados otimizados, melhor performance\nCompleto: Acesso total, pode ser mais lento"
            )
            
            if modo_operacao == "cloud":
                st.info("🎯 **Modo Cloud**\n• Dados otimizados\n• Melhor performance\n• Oculta 'Dados Completos'")
            else:
                st.warning("⚠️ **Modo Completo**\n• Todos os conjuntos de dados\n• Pode impactar performance\n• Inclui 'Dados Completos'")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("🔓 Entrar", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Limpar", use_container_width=True):
                    st.rerun()
        
        if submitted:
            if usuario and senha:
                if verificar_login_simples(usuario, senha):
                    # Verificar se realmente é administrador
                    usuarios = get_usuarios_cloud()
                    if usuario in usuarios and usuarios[usuario].get('tipo') == 'administrador':
                        # Login de admin aprovado
                        st.session_state.usuario_nome = usuario
                        st.session_state.usuario_logado = True
                        st.session_state.login_time = datetime.now().isoformat()
                        st.session_state.modo_operacao = modo_operacao
                        
                        st.success(f"✅ Login realizado! Bem-vindo, {usuario}!")
                        st.success(f"👑 **Admin:** Modo {'☁️ Cloud' if modo_operacao == 'cloud' else '💻 Completo'}")
                        st.rerun()
                    else:
                        st.error("❌ Este usuário não é administrador!")
                        st.info("💡 Use o login de 'Usuário Comum' se você não é admin.")
            else:
                st.error("❌ Preencha usuário e senha!")
    
    
    # Seção informativa
    st.markdown("---")
    st.subheader("ℹ️ Informações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("👥 **Usuário Comum**\n• Modo Cloud automático\n• Melhor performance\n• Interface simplificada")
    
    with col2:
        st.info("👑 **Administrador**\n• Escolha de modo\n• Acesso completo\n• Gerenciamento avançado")
    
    st.caption("💡 **Dica:** Se você não tem certeza, comece com 'Usuário Comum'")
    
    # Administração rápida (apenas para admins logados temporariamente)
    if st.checkbox("🔧 Administração Rápida", help="Para admins adicionarem usuários rapidamente"):
        with st.expander("➕ Adicionar Usuário", expanded=True):
            with st.form("admin_rapido"):
                col1, col2 = st.columns(2)
                with col1:
                    novo_usuario = st.text_input("Usuário:")
                    nova_senha = st.text_input("Senha:", type="password")
                with col2:
                    tipo_usuario = st.selectbox("Tipo:", ["usuario", "administrador"])
                    st.write("")  # Espaçamento
                
                if st.form_submit_button("➕ Adicionar"):
                    if novo_usuario and nova_senha:
                        try:
                            resultado = salvar_usuario_json(novo_usuario, nova_senha, tipo_usuario)
                            if resultado:
                                st.success(f"✅ Usuário '{novo_usuario}' criado!")
                            else:
                                st.error("❌ Usuário já existe!")
                        except Exception as e:
                            st.error(f"❌ Erro: {e}")
                    else:
                        st.error("❌ Preencha os campos!")
    
    # Link para página de administração dedicada
    st.markdown("---")
    st.info("💡 **Para administração completa de usuários:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👑 Ir para Página de Admin", use_container_width=True):
            st.markdown("🔗 **Acesse:** [Administração de Usuários](http://localhost:8640)")
            st.info("📝 Ou navegue pelo dashboard principal")
    with col2:
        if st.button("📊 Ir para Dashboard", use_container_width=True):
            st.markdown("🔗 **Acesse:** [Dashboard Principal](http://localhost:8635)")
    

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

def salvar_usuario_json(nome_usuario, senha, tipo='usuario'):
    """Salva usuário no arquivo usuarios.json para persistência"""
    import json
    import os
    
    try:
        # Carregar usuários existentes
        if os.path.exists('usuarios.json'):
            with open('usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
        else:
            usuarios = {}
        
        # Verificar se usuário já existe
        if nome_usuario in usuarios:
            return False, "❌ Usuário já existe!"
        
        # Validar dados
        if not nome_usuario or not senha:
            return False, "❌ Nome de usuário e senha são obrigatórios!"
        
        if len(senha) < 4:
            return False, "❌ Senha deve ter pelo menos 4 caracteres!"
        
        # Adicionar novo usuário
        usuarios[nome_usuario] = {
            'senha': criar_hash_senha(senha),
            'data_criacao': datetime.now().isoformat(),
            'status': 'aprovado',
            'tipo': tipo,
            'aprovado_em': datetime.now().isoformat()
        }
        
        # Salvar arquivo
        with open('usuarios.json', 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)
        
        return True, f"✅ Usuário '{nome_usuario}' criado com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro ao salvar usuário: {str(e)}"

def listar_usuarios_json():
    """Lista todos os usuários do arquivo usuarios.json"""
    import json
    import os
    
    try:
        if os.path.exists('usuarios.json'):
            with open('usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
            return usuarios
        return {}
    except Exception:
        return {}

def excluir_usuario_json(nome_usuario):
    """Exclui usuário do arquivo usuarios.json"""
    import json
    import os
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists('usuarios.json'):
            return False, "❌ Arquivo de usuários não encontrado!"
        
        # Carregar usuários existentes
        with open('usuarios.json', 'r', encoding='utf-8') as f:
            usuarios = json.load(f)
        
        # Verificar se usuário existe
        if nome_usuario not in usuarios:
            return False, f"❌ Usuário '{nome_usuario}' não encontrado!"
        
        # Não permitir excluir o admin principal
        if nome_usuario == 'admin':
            return False, "❌ Não é possível excluir o usuário 'admin' principal!"
        
        # Remover usuário
        del usuarios[nome_usuario]
        
        # Salvar arquivo atualizado
        with open('usuarios.json', 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=2, ensure_ascii=False)
        
        return True, f"✅ Usuário '{nome_usuario}' excluído com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro ao excluir usuário: {str(e)}"

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

def get_modo_operacao():
    """Retorna o modo de operação selecionado no login"""
    return st.session_state.get('modo_operacao', 'cloud')

def is_modo_cloud():
    """Retorna True se o modo selecionado for cloud (otimizado)"""
    return get_modo_operacao() == 'cloud'

# Se este arquivo for executado diretamente, mostrar a tela de login
if __name__ == "__main__":
    # Configurar página
    st.set_page_config(
        page_title="Login - Dashboard KE5Z",
        page_icon="🔐",
        layout="centered"
    )
    
    # Mostrar tela de login
    tela_login_simples()
