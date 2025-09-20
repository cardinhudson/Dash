#!/usr/bin/env python3
"""
Script para criar arquivo parquet otimizado especificamente para o gráfico Waterfall
Mantém apenas as colunas essenciais e aplica sumarização quando possível
"""

import pandas as pd
import os
import sys

def criar_waterfall_parquet():
    """Cria arquivo parquet otimizado para waterfall"""
    
    print("🌊 === CRIANDO ARQUIVO WATERFALL OTIMIZADO ===")
    
    # Verificar se arquivo original existe
    arquivo_origem = os.path.join("KE5Z", "KE5Z.parquet")
    if not os.path.exists(arquivo_origem):
        print("❌ Erro: Arquivo KE5Z.parquet não encontrado!")
        return False
    
    print(f"📂 Carregando dados de: {arquivo_origem}")
    
    try:
        # Carregar dados completos
        df_original = pd.read_parquet(arquivo_origem)
        print(f"📊 Dados originais: {len(df_original):,} registros, {len(df_original.columns)} colunas")
        
        # Definir colunas essenciais para o waterfall
        colunas_waterfall = [
            'Período',      # OBRIGATÓRIA - Para seleção de meses
            'Valor',        # OBRIGATÓRIA - Para cálculos
            'USI',          # Filtro principal + dimensão
            'Type 05',      # Dimensão de categoria
            'Type 06',      # Dimensão de categoria
            'Type 07',      # Dimensão de categoria
            'Fornecedor',   # Dimensão de categoria + filtro
            'Centro cst',   # Filtro
            'Nº conta',     # Filtro
            'Fornec.',      # Filtro
            'Tipo'          # Filtro
        ]
        
        # Verificar quais colunas existem
        colunas_existentes = [col for col in colunas_waterfall if col in df_original.columns]
        colunas_faltantes = [col for col in colunas_waterfall if col not in df_original.columns]
        
        print(f"✅ Colunas encontradas ({len(colunas_existentes)}): {colunas_existentes}")
        if colunas_faltantes:
            print(f"⚠️ Colunas não encontradas ({len(colunas_faltantes)}): {colunas_faltantes}")
        
        # Filtrar apenas colunas essenciais
        df_waterfall = df_original[colunas_existentes].copy()
        
        print(f"🔄 Dados filtrados: {len(df_waterfall):,} registros, {len(df_waterfall.columns)} colunas")
        
        # Aplicar otimizações de memória
        print("⚡ Aplicando otimizações de memória...")
        
        # Converter strings categóricas para category
        for col in df_waterfall.columns:
            if df_waterfall[col].dtype == 'object':
                unique_ratio = df_waterfall[col].nunique(dropna=True) / max(1, len(df_waterfall))
                if unique_ratio < 0.5:  # Se menos de 50% são valores únicos
                    df_waterfall[col] = df_waterfall[col].astype('category')
                    print(f"  📋 {col}: convertido para category ({unique_ratio:.1%} únicos)")
        
        # Otimizar tipos numéricos
        for col in df_waterfall.select_dtypes(include=['float64']).columns:
            df_waterfall[col] = pd.to_numeric(df_waterfall[col], downcast='float')
            print(f"  📊 {col}: otimizado para float32")
        
        for col in df_waterfall.select_dtypes(include=['int64']).columns:
            df_waterfall[col] = pd.to_numeric(df_waterfall[col], downcast='integer')
            print(f"  🔢 {col}: otimizado para int32")
        
        # Remover registros com valores nulos nas colunas críticas
        antes_limpeza = len(df_waterfall)
        df_waterfall = df_waterfall.dropna(subset=['Período', 'Valor'])
        depois_limpeza = len(df_waterfall)
        
        if antes_limpeza != depois_limpeza:
            print(f"🧹 Removidos {antes_limpeza - depois_limpeza:,} registros com valores nulos em colunas críticas")
        
        # Salvar arquivo otimizado
        pasta_destino = "KE5Z"
        os.makedirs(pasta_destino, exist_ok=True)
        
        arquivo_destino = os.path.join(pasta_destino, "KE5Z_waterfall.parquet")
        df_waterfall.to_parquet(arquivo_destino, index=False)
        
        # Calcular tamanhos
        tamanho_original = os.path.getsize(arquivo_origem) / (1024*1024)
        tamanho_waterfall = os.path.getsize(arquivo_destino) / (1024*1024)
        reducao = ((tamanho_original - tamanho_waterfall) / tamanho_original) * 100
        
        print(f"\n✅ === ARQUIVO WATERFALL CRIADO COM SUCESSO ===")
        print(f"📁 Arquivo: {arquivo_destino}")
        print(f"📊 Registros: {len(df_waterfall):,}")
        print(f"📋 Colunas: {len(df_waterfall.columns)}")
        print(f"💾 Tamanho original: {tamanho_original:.1f} MB")
        print(f"💾 Tamanho otimizado: {tamanho_waterfall:.1f} MB")
        print(f"⚡ Redução: {reducao:.1f}%")
        
        # Mostrar estatísticas das colunas
        print(f"\n📈 ESTATÍSTICAS DAS COLUNAS:")
        for col in df_waterfall.columns:
            if col in ['Período', 'Valor']:
                valores_unicos = df_waterfall[col].nunique()
                print(f"  🔑 {col}: {valores_unicos:,} valores únicos")
            elif df_waterfall[col].dtype.name == 'category' or df_waterfall[col].dtype == 'object':
                valores_unicos = df_waterfall[col].nunique()
                print(f"  📋 {col}: {valores_unicos:,} categorias")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar arquivo waterfall: {str(e)}")
        return False

if __name__ == "__main__":
    sucesso = criar_waterfall_parquet()
    if sucesso:
        print("\n🎉 Processo concluído com sucesso!")
        sys.exit(0)
    else:
        print("\n💥 Processo falhou!")
        sys.exit(1)
