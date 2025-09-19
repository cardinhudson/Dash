#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para listar todas as colunas do arquivo parquet
Para você escolher quais manter e quais remover
"""

import pandas as pd
import os

def listar_colunas_parquet():
    """Lista todas as colunas do arquivo parquet com informações detalhadas"""
    
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    
    if not os.path.exists(arquivo_parquet):
        print(f"❌ ERRO: {arquivo_parquet} não encontrado")
        return
    
    try:
        print("=" * 80)
        print("📋 ANÁLISE DAS COLUNAS DO ARQUIVO KE5Z.PARQUET")
        print("=" * 80)
        
        # Carregar dados para análise
        print("📂 Carregando dados para análise...")
        df = pd.read_parquet(arquivo_parquet)
        
        # Pegar apenas uma amostra para análise rápida
        if len(df) > 10000:
            df = df.sample(n=10000, random_state=42)
            print(f"📊 Usando amostra de 10.000 registros para análise")
        
        print(f"✅ Amostra carregada: {len(df):,} registros")
        print(f"📊 Total de colunas: {len(df.columns)}")
        
        print("\n" + "=" * 80)
        print("📋 LISTA DETALHADA DAS COLUNAS")
        print("=" * 80)
        
        # Analisar cada coluna
        colunas_info = []
        
        for i, col in enumerate(df.columns, 1):
            # Informações básicas
            tipo = str(df[col].dtype)
            nulos = df[col].isnull().sum()
            perc_nulos = (nulos / len(df)) * 100
            unicos = df[col].nunique()
            perc_unicos = (unicos / len(df)) * 100
            
            # Amostra de valores (primeiros 3 valores não nulos)
            valores_exemplo = []
            for val in df[col].dropna().head(3):
                if pd.notna(val) and str(val).strip():
                    valores_exemplo.append(str(val)[:30])  # Limitar a 30 caracteres
            
            amostra = ", ".join(valores_exemplo) if valores_exemplo else "Vazio/Nulo"
            
            colunas_info.append({
                'num': i,
                'nome': col,
                'tipo': tipo,
                'nulos': nulos,
                'perc_nulos': perc_nulos,
                'unicos': unicos,
                'perc_unicos': perc_unicos,
                'amostra': amostra
            })
        
        # Exibir informações formatadas
        for info in colunas_info:
            print(f"{info['num']:2d}. 📋 {info['nome']}")
            print(f"    🔧 Tipo: {info['tipo']}")
            print(f"    📊 Valores únicos: {info['unicos']:,} ({info['perc_unicos']:.1f}%)")
            print(f"    ❌ Valores nulos: {info['nulos']:,} ({info['perc_nulos']:.1f}%)")
            print(f"    📝 Exemplos: {info['amostra']}")
            print()
        
        print("=" * 80)
        print("🎯 CLASSIFICAÇÃO POR IMPORTÂNCIA")
        print("=" * 80)
        
        # Classificar colunas por importância
        essenciais = []
        importantes = []
        opcionais = []
        desnecessarias = []
        
        for info in colunas_info:
            nome = info['nome']
            perc_nulos = info['perc_nulos']
            perc_unicos = info['perc_unicos']
            
            # Classificar por nome e características
            if nome in ['USI', 'Período', 'Valor', 'Type 05', 'Type 06', 'Type 07']:
                essenciais.append(info)
            elif nome in ['Material', 'Fornecedor', 'Cliente', 'Denominação'] and perc_nulos < 50:
                importantes.append(info)
            elif perc_nulos < 80 and perc_unicos > 1:  # Menos de 80% nulos e tem variação
                opcionais.append(info)
            else:
                desnecessarias.append(info)
        
        # Exibir classificações
        def exibir_categoria(titulo, emoji, lista, recomendacao):
            if lista:
                print(f"\n{emoji} {titulo.upper()} ({len(lista)} colunas) - {recomendacao}")
                print("-" * 60)
                for info in lista:
                    print(f"  • {info['nome']} (nulos: {info['perc_nulos']:.1f}%, únicos: {info['perc_unicos']:.1f}%)")
        
        exibir_categoria("Essenciais", "🔴", essenciais, "MANTER SEMPRE")
        exibir_categoria("Importantes", "🟡", importantes, "RECOMENDO MANTER")
        exibir_categoria("Opcionais", "🟢", opcionais, "PODE MANTER OU REMOVER")
        exibir_categoria("Desnecessárias", "⚪", desnecessarias, "RECOMENDO REMOVER")
        
        print("\n" + "=" * 80)
        print("📝 RESUMO PARA DECISÃO")
        print("=" * 80)
        print(f"🔴 Essenciais (manter): {len(essenciais)} colunas")
        print(f"🟡 Importantes (recomendo manter): {len(importantes)} colunas")
        print(f"🟢 Opcionais (sua escolha): {len(opcionais)} colunas")
        print(f"⚪ Desnecessárias (recomendo remover): {len(desnecessarias)} colunas")
        
        print(f"\nTotal atual: {len(df.columns)} colunas")
        print(f"Recomendação mínima: {len(essenciais)} colunas")
        print(f"Recomendação completa: {len(essenciais) + len(importantes)} colunas")
        
        print("\n💡 PRÓXIMO PASSO:")
        print("Revise a lista acima e me informe quais colunas você quer:")
        print("✅ MANTER")
        print("❌ REMOVER")
        
        # Salvar lista em arquivo para referência
        with open("lista_colunas_analise.txt", "w", encoding="utf-8") as f:
            f.write("ANÁLISE DAS COLUNAS - KE5Z.PARQUET\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("ESSENCIAIS (manter sempre):\n")
            for info in essenciais:
                f.write(f"- {info['nome']}\n")
            
            f.write("\nIMPORTANTES (recomendo manter):\n")
            for info in importantes:
                f.write(f"- {info['nome']}\n")
            
            f.write("\nOPCIONAIS (sua escolha):\n")
            for info in opcionais:
                f.write(f"- {info['nome']}\n")
            
            f.write("\nDESNECESSÁRIAS (recomendo remover):\n")
            for info in desnecessarias:
                f.write(f"- {info['nome']}\n")
        
        print(f"\n📄 Lista salva em: lista_colunas_analise.txt")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    listar_colunas_parquet()
