# 🚀 Como Executar a Extração KE5Z

## ❌ **PROBLEMA IDENTIFICADO**
O comando `python Extração.py` apresenta erro "No pyvenv.cfg file" e não executa.

## ✅ **SOLUÇÕES DISPONÍVEIS**

### **🔧 Solução 1: Comando Completo (SEMPRE FUNCIONA)**
```bash
C:\Users\u235107\AppData\Local\Programs\Python\Python311\python.exe Extração.py
```

### **🔧 Solução 2: Script Batch (MAIS FÁCIL)**
```bash
EXECUTAR.bat
```
- Duplo clique no arquivo `EXECUTAR.bat`
- Ou execute no terminal: `EXECUTAR.bat`

### **🔧 Solução 3: Script Python Wrapper**
```bash
C:\Users\u235107\AppData\Local\Programs\Python\Python311\python.exe rodar_extracao.py
```

### **🔧 Solução 4: Interface Streamlit**
```bash
streamlit run Dash.py
```
- Navegar para página "Extração Dados"
- Clicar "Executar Extração Completa"

## 📊 **RESULTADOS ESPERADOS**

Quando executada com sucesso, a extração processará:
- ✅ **3+ milhões de registros**
- ✅ **Arquivos parquet** (main, others, waterfall, completo)
- ✅ **Arquivos Excel** (veículos, PWT)
- ✅ **Otimização de memória** (68% redução)

## ⚠️ **IMPORTANTE**

**NÃO USAR:** `python Extração.py` (causa erro)
**USAR:** Qualquer uma das 4 soluções acima

## 🎯 **RECOMENDAÇÃO**

Para uso diário, recomendamos:
1. **`EXECUTAR.bat`** - Mais simples (duplo clique)
2. **Interface Streamlit** - Mais visual (com logs em tempo real)
