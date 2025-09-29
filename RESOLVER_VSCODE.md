# RESOLVER PROBLEMA DO VS CODE

## 🚨 PROBLEMA
```
failed to locate pyvenv.cfg: The system cannot find the file specified.
```

## ✅ SOLUÇÃO IMEDIATA

### **Opção 1: Usar arquivo .bat (MAIS FÁCIL)**
```
executar_extracao.bat
```
Este arquivo já foi criado e usa o Python do sistema diretamente.

### **Opção 2: Configurar VS Code**
1. No VS Code, pressione `Ctrl+Shift+P`
2. Digite: `Python: Select Interpreter`
3. Escolha: `Python 3.13.7` (NÃO escolha opções com "venv")
4. Reinicie o VS Code

### **Opção 3: Terminal direto**
```bash
python Extração.py
```

## 🔧 CONFIGURAÇÃO CRIADA

Arquivo `.vscode/settings.json` foi criado com:
- Python do sistema como padrão
- Ambientes virtuais desabilitados
- Configurações limpas

## 📋 TESTE RÁPIDO

Execute no terminal:
```bash
python --version
python Extração.py
```

## ✅ STATUS
- ✅ Python do sistema: Funcionando
- ✅ Arquivo .bat criado: executar_extracao.bat
- ✅ Configuração VS Code: Aplicada
- ✅ Solução: DISPONÍVEL

**Use `executar_extracao.bat` para execução sem problemas!**


