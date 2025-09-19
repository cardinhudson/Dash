# 🔐 Sistema de Autenticação Simplificado

## 🎯 **Novo Sistema Implementado**

Substituímos o sistema baseado em `usuarios.json` por um sistema mais robusto usando **Streamlit Secrets**, que é totalmente compatível com o Streamlit Cloud.

---

## ✅ **Vantagens do Novo Sistema:**

### 🌩️ **Streamlit Cloud:**
- ✅ **Compatível nativo**: Usa system de secrets oficial
- ✅ **Sem arquivos JSON**: Evita problemas de permissão
- ✅ **Seguro**: Senhas não ficam no código
- ✅ **Fácil gerenciamento**: Interface web do Streamlit

### 💻 **Modo Local:**
- ✅ **Fallback automático**: Usuários de demonstração
- ✅ **Desenvolvimento fácil**: Sem configuração complexa
- ✅ **Compatibilidade total**: Funciona em qualquer ambiente

---

## 👥 **Usuários Disponíveis:**

### 🔑 **Credenciais Padrão:**
- **admin** / admin123 (👑 Administrador)
- **demo** / demo123 (👥 Usuário)
- **joao** / hello (👥 Usuário)
- **hudson** / hudson123 (👥 Usuário)
- **lauro** / hello (👥 Usuário)

---

## 🚀 **Como Configurar no Streamlit Cloud:**

### 1. **Acessar Configurações:**
1. Vá para seu app no Streamlit Cloud
2. Clique em **"Settings"**
3. Vá na aba **"Secrets"**

### 2. **Adicionar Usuários:**
```toml
[usuarios.admin]
senha = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
status = "aprovado"
tipo = "administrador"

[usuarios.novo_usuario]
senha = "hash_da_senha_aqui"
status = "aprovado"
tipo = "usuario"
```

### 3. **Gerar Hash de Senha:**
```python
import hashlib
senha = "sua_senha_aqui"
hash_senha = hashlib.sha256(senha.encode()).hexdigest()
print(hash_senha)
```

### 4. **Redeploy:**
- Salve as configurações
- O app será automaticamente redeployado
- Novos usuários estarão disponíveis

---

## 🔧 **Funcionalidades:**

### 👑 **Administradores podem:**
- ✅ Ver todos os usuários cadastrados
- ✅ Acessar área administrativa
- ✅ Ver estatísticas do sistema
- ✅ (Futuro) Gerenciar usuários via interface

### 👥 **Usuários podem:**
- ✅ Acessar dashboard principal
- ✅ Usar todos os filtros
- ✅ Visualizar gráficos e tabelas
- ✅ Exportar dados

---

## 🛠️ **Para Desenvolvedores:**

### **Arquivo Principal:** `auth_simple.py`
```python
from auth_simple import (
    verificar_autenticacao,
    exibir_header_usuario,
    eh_administrador,
    verificar_status_aprovado
)
```

### **Funções Principais:**
- `verificar_autenticacao()`: Obrigatório no início de cada página
- `exibir_header_usuario()`: Mostra info do usuário logado
- `eh_administrador()`: Verifica se é admin
- `verificar_status_aprovado()`: Verifica se usuário está ativo

### **Compatibilidade:**
- ✅ **Mantém compatibilidade** com código existente
- ✅ **Mesmas funções** do sistema anterior
- ✅ **Sem quebrar** páginas existentes

---

## 🔄 **Migração do Sistema Antigo:**

### **Antes (usuarios.json):**
```json
{
  "admin": {
    "senha": "hash",
    "status": "aprovado"
  }
}
```

### **Agora (secrets.toml):**
```toml
[usuarios.admin]
senha = "hash"
status = "aprovado"
tipo = "administrador"
```

---

## 🆘 **Solução de Problemas:**

### **Erro de Login:**
- Verifique se o usuário existe nos secrets
- Confirme se a senha está correta
- Verifique se status = "aprovado"

### **Não mostra área admin:**
- Confirme se tipo = "administrador"
- Verifique se está logado como admin

### **No Streamlit Cloud:**
- Verifique se secrets estão configurados
- Redeploy após mudanças nos secrets
- Verifique logs de erro no painel

---

## 🎉 **Resultado:**

✅ **Sistema robusto e compatível**  
✅ **Funciona local e cloud**  
✅ **Fácil de gerenciar**  
✅ **Seguro e confiável**  

**🚀 Pronto para produção no Streamlit Cloud!**
