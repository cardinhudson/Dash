import streamlit as st
import sys
import os

# Adicionar diretório pai ao path para importar auth_simple
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from auth_simple import (verificar_autenticacao, exibir_header_usuario, 
                             eh_administrador, salvar_usuario_json, listar_usuarios_json)
except ImportError as e:
    st.error(f"❌ Erro ao importar auth_simple: {e}")
    st.stop()

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

# Configuração da página
st.set_page_config(
    page_title="Admin - Usuários",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Verificar autenticação
verificar_autenticacao()

# Navegação simples
st.sidebar.markdown("📋 **NAVEGAÇÃO:** Use abas do navegador")
st.sidebar.markdown("🏠 Dashboard: `http://localhost:8555`")
st.sidebar.markdown("---")

# Verificar se é administrador
if not eh_administrador():
    st.error("🚫 **Acesso Negado**")
    st.error("Esta página é restrita a administradores.")
    st.info("👥 Você está logado como usuário comum.")
    st.stop()

# Header com informações do usuário
exibir_header_usuario()

st.title("👑 Administração de Usuários")
st.success("✅ **4 Funcionalidades:** Cadastrar • Listar • Excluir • Estatísticas")
st.markdown("---")

# Tabs para organizar funcionalidades
tab1, tab2, tab3, tab4 = st.tabs(["➕ Cadastrar Usuário", "👥 Listar Usuários", "🗑️ Excluir Usuário", "📊 Estatísticas"])

with tab1:
    st.subheader("➕ Cadastrar Novo Usuário")
    
    with st.form("cadastrar_usuario_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📝 Dados do Usuário**")
            novo_usuario = st.text_input("Nome do usuário:", placeholder="Digite o nome do usuário")
            nova_senha = st.text_input("Senha:", type="password", placeholder="Digite a senha")
            confirmar_senha = st.text_input("Confirmar senha:", type="password", placeholder="Digite a senha novamente")
        
        with col2:
            st.markdown("**⚙️ Configurações**")
            novo_tipo = st.selectbox("Tipo de usuário:", ["usuario", "administrador"])
            
            if novo_tipo == "administrador":
                st.warning("⚠️ **Administrador terá acesso total ao sistema**")
            else:
                st.info("👥 **Usuário terá acesso padrão**")
            
            # Informações sobre permissões
            st.markdown("**🔐 Permissões:**")
            if novo_tipo == "administrador":
                st.write("✅ Acesso a todas as páginas")
                st.write("✅ Modo Cloud e Completo")
                st.write("✅ Administração de usuários")
                st.write("✅ Extração de dados")
            else:
                st.write("✅ Acesso a páginas de análise")
                st.write("✅ Apenas modo Cloud (otimizado)")
                st.write("❌ Sem acesso administrativo")
        
        st.markdown("---")
        
        col_submit, col_clear = st.columns(2)
        
        with col_submit:
            if st.form_submit_button("➕ Criar Usuário", use_container_width=True, type="primary"):
                # Validações
                if not novo_usuario or not nova_senha:
                    st.error("❌ Preencha todos os campos!")
                elif nova_senha != confirmar_senha:
                    st.error("❌ Senhas não coincidem!")
                elif len(nova_senha) < 4:
                    st.error("❌ Senha deve ter pelo menos 4 caracteres!")
                else:
                    # Tentar criar usuário
                    sucesso, mensagem = salvar_usuario_json(novo_usuario, nova_senha, novo_tipo)
                    if sucesso:
                        st.success(mensagem)
                        st.success(f"🎯 **Usuário criado:** {novo_usuario}")
                        st.success(f"🔐 **Tipo:** {'👑 Administrador' if novo_tipo == 'administrador' else '👥 Usuário'}")
                        st.info("🔄 O usuário pode fazer login imediatamente!")
                    else:
                        st.error(mensagem)
        
        with col_clear:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()

with tab2:
    st.subheader("👥 Usuários Cadastrados")
    
    # Carregar usuários
    usuarios = listar_usuarios_json()
    
    if usuarios:
        # Estatísticas rápidas
        total_usuarios = len(usuarios)
        admins = sum(1 for u in usuarios.values() if u.get('tipo') == 'administrador')
        usuarios_normais = total_usuarios - admins
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total de Usuários", total_usuarios)
        with col2:
            st.metric("👑 Administradores", admins)
        with col3:
            st.metric("👤 Usuários", usuarios_normais)
        
        st.markdown("---")
        
        # Lista detalhada
        for usuario, dados in usuarios.items():
            with st.expander(f"{'👑' if dados.get('tipo') == 'administrador' else '👥'} {usuario}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Usuário:** {usuario}")
                    st.write(f"**Tipo:** {'👑 Administrador' if dados.get('tipo') == 'administrador' else '👥 Usuário'}")
                    st.write(f"**Status:** {'✅ Aprovado' if dados.get('status') == 'aprovado' else '⏳ Pendente'}")
                
                with col2:
                    if 'data_criacao' in dados:
                        data_criacao = dados['data_criacao'][:19].replace('T', ' ')
                        st.write(f"**Criado em:** {data_criacao}")
                    
                    if 'aprovado_em' in dados:
                        data_aprovacao = dados['aprovado_em'][:19].replace('T', ' ')
                        st.write(f"**Aprovado em:** {data_aprovacao}")
    else:
        st.info("📭 Nenhum usuário encontrado no sistema.")

with tab3:
    st.subheader("🗑️ Excluir Usuário")
    
    # Carregar usuários para seleção
    usuarios = listar_usuarios_json()
    
    if usuarios:
        # Filtrar usuários (excluir admin da lista)
        usuarios_excluiveis = {k: v for k, v in usuarios.items() if k != 'admin'}
        
        if usuarios_excluiveis:
            st.warning("⚠️ **ATENÇÃO:** Esta ação é irreversível!")
            
            with st.form("excluir_usuario_form"):
                # Seleção do usuário
                usuario_para_excluir = st.selectbox(
                    "Selecione o usuário para excluir:",
                    options=list(usuarios_excluiveis.keys()),
                    format_func=lambda x: f"{'👑' if usuarios_excluiveis[x].get('tipo') == 'administrador' else '👥'} {x}"
                )
                
                # Mostrar informações do usuário selecionado
                if usuario_para_excluir:
                    dados_usuario = usuarios_excluiveis[usuario_para_excluir]
                    
                    st.markdown("**📋 Informações do usuário:**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"**Usuário:** {usuario_para_excluir}")
                        st.info(f"**Tipo:** {'👑 Administrador' if dados_usuario.get('tipo') == 'administrador' else '👥 Usuário'}")
                    
                    with col2:
                        if 'data_criacao' in dados_usuario:
                            data_criacao = dados_usuario['data_criacao'][:19].replace('T', ' ')
                            st.info(f"**Criado em:** {data_criacao}")
                
                # Confirmação de segurança
                st.markdown("---")
                st.error("🚨 **CONFIRMAÇÃO DE SEGURANÇA**")
                
                confirmacao = st.text_input(
                    f"Digite 'EXCLUIR {usuario_para_excluir}' para confirmar:",
                    placeholder=f"EXCLUIR {usuario_para_excluir}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("🗑️ EXCLUIR USUÁRIO", use_container_width=True, type="primary"):
                        if confirmacao == f"EXCLUIR {usuario_para_excluir}":
                            sucesso, mensagem = excluir_usuario_json(usuario_para_excluir)
                            if sucesso:
                                st.success(mensagem)
                                st.success(f"🎯 **Usuário removido:** {usuario_para_excluir}")
                                st.info("🔄 Lista de usuários atualizada!")
                                st.rerun()
                            else:
                                st.error(mensagem)
                        else:
                            st.error("❌ Confirmação incorreta! Digite exatamente como solicitado.")
                
                with col2:
                    if st.form_submit_button("🔄 Cancelar", use_container_width=True):
                        st.rerun()
        else:
            st.info("📭 Apenas o usuário 'admin' existe (não pode ser excluído).")
    else:
        st.info("📭 Nenhum usuário encontrado no sistema.")

with tab4:
    st.subheader("📊 Estatísticas do Sistema")
    
    usuarios = listar_usuarios_json()
    
    if usuarios:
        import pandas as pd
        from datetime import datetime
        
        # Preparar dados para análise
        dados_usuarios = []
        for usuario, dados in usuarios.items():
            dados_usuarios.append({
                'Usuario': usuario,
                'Tipo': dados.get('tipo', 'usuario'),
                'Status': dados.get('status', 'aprovado'),
                'Data_Criacao': dados.get('data_criacao', '')
            })
        
        df_usuarios = pd.DataFrame(dados_usuarios)
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por tipo
            tipo_counts = df_usuarios['Tipo'].value_counts()
            st.subheader("📊 Distribuição por Tipo")
            st.bar_chart(tipo_counts)
        
        with col2:
            # Status dos usuários
            status_counts = df_usuarios['Status'].value_counts()
            st.subheader("✅ Status dos Usuários")
            st.bar_chart(status_counts)
        
        # Tabela resumo
        st.subheader("📋 Resumo Geral")
        st.dataframe(df_usuarios, use_container_width=True)
        
    else:
        st.info("📭 Nenhum dado disponível para estatísticas.")

# Informações do sistema
st.sidebar.markdown("---")
with st.sidebar.expander("📊 Info Sistema", expanded=False):
    usuarios = listar_usuarios_json()
    st.write(f"**Total usuários:** {len(usuarios)}")
    st.write(f"**Arquivo:** usuarios.json")
    st.write(f"**Status:** ✅ Funcionando")
