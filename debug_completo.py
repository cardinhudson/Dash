#!/usr/bin/env python3
import streamlit as st
import hashlib
import json
import os
from datetime import datetime

st.set_page_config(page_title="Debug Completo", page_icon="🔍")

def log_debug(mensagem):
    """Função para registrar logs de debug"""
    if 'debug_logs' not in st.session_state:
        st.session_state.debug_logs = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.debug_logs.append(f"[{timestamp}] {mensagem}")

def criar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def get_usuarios_cloud():
    try:
        if os.path.exists('usuarios.json'):
            with open('usuarios.json', 'r', encoding='utf-8') as f:
                usuarios = json.load(f)
                log_debug(f"✅ usuarios.json carregado com {len(usuarios)} usuários")
                return usuarios
        else:
            log_debug("❌ usuarios.json não encontrado")
            return {}
    except Exception as e:
        log_debug(f"❌ Erro ao carregar usuarios.json: {e}")
        return {}

def verificar_login_debug(usuario, senha):
    log_debug(f"🔍 INICIANDO verificar_login_debug para: '{usuario}'")
    
    usuarios = get_usuarios_cloud()
    log_debug(f"📋 Usuários disponíveis: {list(usuarios.keys())}")
    
    if usuario in usuarios:
        log_debug(f"✅ Usuário '{usuario}' encontrado!")
        
        dados_usuario = usuarios[usuario]
        log_debug(f"📊 Dados do usuário: {dados_usuario}")
        
        senha_hash = criar_hash_senha(senha)
        senha_armazenada = dados_usuario['senha']
        
        log_debug(f"🔐 Hash da senha digitada: {senha_hash}")
        log_debug(f"🔐 Hash armazenado: {senha_armazenada}")
        
        if senha_hash == senha_armazenada:
            log_debug("✅ Senhas coincidem!")
            
            status = dados_usuario.get('status', 'aprovado')
            log_debug(f"📊 Status da conta: {status}")
            
            if status == 'aprovado':
                log_debug("✅ LOGIN APROVADO!")
                return True
            else:
                log_debug("⏳ Conta pendente de aprovação")
                st.error("⏳ Conta pendente de aprovação.")
                return False
        else:
            log_debug("❌ Senhas não coincidem!")
            st.error("❌ Senha incorreta!")
            return False
    else:
        log_debug(f"❌ Usuário '{usuario}' não encontrado!")
        st.error("❌ Usuário não encontrado!")
        return False

# INÍCIO DA INTERFACE
st.title("🔍 Debug Completo do Sistema de Login")

# Limpar logs
if st.button("🧹 Limpar Logs"):
    st.session_state.debug_logs = []
    st.rerun()

# Mostrar session_state atual
st.subheader("📊 Estado da Sessão")
st.write("**Session State atual:**")
session_info = {}
for key in st.session_state:
    if not key.startswith('debug_'):
        session_info[key] = st.session_state[key]
st.json(session_info)

# Verificar se está logado
if 'usuario_nome' in st.session_state:
    st.success(f"✅ **USUÁRIO LOGADO:** {st.session_state.usuario_nome}")
    st.success(f"⚙️ **MODO:** {st.session_state.get('modo_operacao', 'N/A')}")
    
    if st.button("🚪 Logout"):
        log_debug("🚪 Fazendo logout...")
        keys_to_remove = ['usuario_nome', 'usuario_logado', 'login_time', 'modo_operacao']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
else:
    st.info("👤 **Nenhum usuário logado**")

st.markdown("---")

# TESTE DE LOGIN
st.subheader("🧪 Teste de Login")

tipo_login = st.radio("Tipo de usuário:", ["usuario", "admin"])

if tipo_login == "usuario":
    st.info("👥 **Teste de Usuário Comum**")
    
    with st.form("test_user"):
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        submitted = st.form_submit_button("🔓 Testar Login")
    
    if submitted:
        log_debug(f"🚀 INICIANDO TESTE DE LOGIN DE USUÁRIO: {usuario}")
        
        if usuario and senha:
            log_debug("📝 Campos preenchidos, iniciando verificação...")
            
            # Teste da função de verificação
            resultado_verificacao = verificar_login_debug(usuario, senha)
            log_debug(f"🎯 Resultado da verificação: {resultado_verificacao}")
            
            if resultado_verificacao:
                log_debug("✅ Verificação aprovada, processando login...")
                
                # Verificar se é usuário comum
                usuarios = get_usuarios_cloud()
                if usuario in usuarios and usuarios[usuario].get('tipo') == 'administrador':
                    log_debug("⚠️ Usuário é administrador, mostrando aviso...")
                    st.warning("⚠️ **Você é administrador!** Use o login de admin.")
                else:
                    log_debug("👥 Usuário comum confirmado, definindo session_state...")
                    
                    # Definir session_state
                    st.session_state.usuario_nome = usuario
                    st.session_state.usuario_logado = True
                    st.session_state.login_time = datetime.now().isoformat()
                    st.session_state.modo_operacao = "cloud"
                    
                    log_debug("📊 Session_state definido, valores:")
                    log_debug(f"  - usuario_nome: {st.session_state.usuario_nome}")
                    log_debug(f"  - usuario_logado: {st.session_state.usuario_logado}")
                    log_debug(f"  - modo_operacao: {st.session_state.modo_operacao}")
                    
                    st.success(f"✅ Login realizado! Bem-vindo, {usuario}!")
                    st.success("⚙️ **Modo aplicado:** ☁️ Cloud (Otimizado)")
                    
                    log_debug("🔄 Chamando st.rerun()...")
                    st.rerun()
            else:
                log_debug("❌ Verificação falhou")
        else:
            log_debug("❌ Campos não preenchidos")
            st.error("❌ Preencha usuário e senha!")

else:
    st.info("👑 **Teste de Administrador**")
    
    with st.form("test_admin"):
        usuario = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        modo_operacao = st.radio("Modo:", ["cloud", "completo"])
        submitted = st.form_submit_button("🔓 Testar Login")
    
    if submitted:
        log_debug(f"🚀 INICIANDO TESTE DE LOGIN DE ADMIN: {usuario}")
        
        if usuario and senha:
            log_debug("📝 Campos preenchidos, iniciando verificação...")
            
            resultado_verificacao = verificar_login_debug(usuario, senha)
            log_debug(f"🎯 Resultado da verificação: {resultado_verificacao}")
            
            if resultado_verificacao:
                log_debug("✅ Verificação aprovada, verificando se é admin...")
                
                usuarios = get_usuarios_cloud()
                if usuario in usuarios and usuarios[usuario].get('tipo') == 'administrador':
                    log_debug("👑 Usuário admin confirmado, definindo session_state...")
                    
                    # Definir session_state
                    st.session_state.usuario_nome = usuario
                    st.session_state.usuario_logado = True
                    st.session_state.login_time = datetime.now().isoformat()
                    st.session_state.modo_operacao = modo_operacao
                    
                    log_debug("📊 Session_state definido, valores:")
                    log_debug(f"  - usuario_nome: {st.session_state.usuario_nome}")
                    log_debug(f"  - usuario_logado: {st.session_state.usuario_logado}")
                    log_debug(f"  - modo_operacao: {st.session_state.modo_operacao}")
                    
                    st.success(f"✅ Login realizado! Bem-vindo, {usuario}!")
                    st.success(f"👑 **Admin:** Modo {modo_operacao}")
                    
                    log_debug("🔄 Chamando st.rerun()...")
                    st.rerun()
                else:
                    log_debug("❌ Usuário não é administrador")
                    st.error("❌ Este usuário não é administrador!")
            else:
                log_debug("❌ Verificação falhou")
        else:
            log_debug("❌ Campos não preenchidos")
            st.error("❌ Preencha usuário e senha!")

# LOGS DE DEBUG
st.markdown("---")
st.subheader("📋 Logs de Debug")
if 'debug_logs' in st.session_state and st.session_state.debug_logs:
    for log in st.session_state.debug_logs[-20:]:  # Últimos 20 logs
        st.text(log)
else:
    st.info("Nenhum log ainda...")

# INFORMAÇÕES DO SISTEMA
st.markdown("---")
st.subheader("🔧 Informações do Sistema")
usuarios = get_usuarios_cloud()
st.write("**Usuários carregados:**")
st.json(usuarios)

st.write("**Credenciais corretas para teste:**")
st.write("- admin / admin123 (administrador)")
st.write("- joao / 1234 (usuário)")
st.write("- lauro / 123 (usuário)")
