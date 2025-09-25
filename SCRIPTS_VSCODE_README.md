# 🛠️ Scripts de Configuração VS Code

## 📋 Visão Geral
Scripts para integrar com as configurações do VS Code e resolver problemas de VPN/conexão.

## 🚀 Scripts Disponíveis

### 1. `usar_vscode_config.bat`
**Script principal** que executa a configuração completa:
- Lê configurações do VS Code
- Aplica configurações de rede
- Testa conexão

**Como usar:**
```bash
usar_vscode_config.bat
```

### 2. `usar_config_vscode.py`
**Script Python** que faz a integração real:
- Lê `.vscode/settings.json`
- Aplica configurações de rede
- Testa Python (python vs py)
- Executa Extração.py

**Como usar:**
```bash
python usar_config_vscode.py
```

### 3. `testar_sistema_completo.bat`
**Script de teste** que verifica todo o sistema:
- Testa Python
- Testa Extração.py
- Testa Streamlit
- Inicia Dashboard

**Como usar:**
```bash
testar_sistema_completo.bat
```

## 🔧 Configuração VS Code

### Arquivo: `.vscode/settings.json`
```json
{
    "python.defaultInterpreterPath": "C:\\Users\\u235107\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
    "python.terminal.activateEnvironment": false,
    "python.terminal.activateEnvInCurrentTerminal": false
}
```

## 📊 Fluxo de Execução

```
1. Ler .vscode/settings.json
   ↓
2. Aplicar configurações de rede
   ↓
3. Testar Python (python vs py)
   ↓
4. Executar Extração.py
   ↓
5. Sistema configurado!
```

## 🎯 Benefícios

- ✅ **Integração com VS Code**: Usa as mesmas configurações
- ✅ **Resolve problemas de VPN**: Configurações de rede otimizadas
- ✅ **Testa automaticamente**: Verifica se tudo funciona
- ✅ **Executa Extração.py**: Garante que o script principal funciona
- ✅ **Fácil de usar**: Apenas execute o .bat

## 🚨 Solução de Problemas

### Problema: "No pyvenv.cfg file"
**Solução:** Execute `usar_vscode_config.bat`

### Problema: "Connection failed"
**Solução:** Execute `usar_vscode_config.bat`

### Problema: Extração.py não executa
**Solução:** Execute `testar_sistema_completo.bat`

## 📝 Logs

Os scripts mostram logs detalhados:
- ✅ Sucesso
- ❌ Erro
- ⚠️ Aviso
- 🔧 Processando

## 🎉 Resultado Final

Após executar os scripts:
1. **Python funcionando** (python ou py)
2. **Extração.py executando** sem erros
3. **Streamlit funcionando** perfeitamente
4. **Dashboard acessível** sem problemas de VPN

---

**💡 Dica:** Execute `usar_vscode_config.bat` sempre que tiver problemas de conexão!
