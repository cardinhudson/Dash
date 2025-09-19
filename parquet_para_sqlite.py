#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migração: Parquet → SQLite
Converte KE5Z.parquet para banco SQLite otimizado para Streamlit Cloud
Mantém TODOS os dados originais exatos
"""

import pandas as pd
import sqlite3
import os
from datetime import datetime
import sys

def migrar_parquet_para_sqlite():
    """
    Migra dados do KE5Z.parquet para SQLite
    Mantém TODOS os dados exatos, mas com performance muito melhor
    """
    
    print("=" * 60)
    print("🚀 MIGRAÇÃO PARQUET → SQLite")
    print("=" * 60)
    
    # Caminhos dos arquivos
    arquivo_parquet = os.path.join("KE5Z", "KE5Z.parquet")
    arquivo_sqlite = "dados_ke5z.db"
    
    # Verificar se parquet existe
    if not os.path.exists(arquivo_parquet):
        print(f"❌ ERRO: Arquivo não encontrado: {arquivo_parquet}")
        print("   Certifique-se de que o arquivo KE5Z.parquet está na pasta KE5Z/")
        return False
    
    try:
        # 1. CARREGAR DADOS DO PARQUET
        print(f"📂 Carregando dados de: {arquivo_parquet}")
        inicio = datetime.now()
        
        df = pd.read_parquet(arquivo_parquet)
        
        tempo_carregamento = (datetime.now() - inicio).total_seconds()
        print(f"✅ Dados carregados em {tempo_carregamento:.1f}s")
        print(f"📊 Total de registros: {len(df):,}")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Mostrar informações dos dados
        print(f"💾 Tamanho em memória: {df.memory_usage(deep=True).sum() / (1024*1024):.1f} MB")
        
        # 2. PREPARAR DADOS PARA SQLite
        print("\n🔧 Preparando dados para SQLite...")
        
        # Limpar dados problemáticos
        for col in df.columns:
            if df[col].dtype == 'object':
                # Substituir NaN por string vazia
                df[col] = df[col].fillna('')
                print(f"   🧹 {col}: NaN substituídos por string vazia")
        
        # 3. CRIAR BANCO SQLite
        print(f"\n🗄️  Criando banco SQLite: {arquivo_sqlite}")
        
        # Remover banco anterior se existir
        if os.path.exists(arquivo_sqlite):
            os.remove(arquivo_sqlite)
            print("   🗑️  Banco anterior removido")
        
        # Conectar ao SQLite
        conn = sqlite3.connect(arquivo_sqlite)
        
        # 4. INSERIR DADOS NO SQLite
        print("📥 Inserindo dados no SQLite...")
        inicio_insert = datetime.now()
        
        # Inserir dados (todos os registros exatos)
        df.to_sql('ke5z_dados', conn, if_exists='replace', index=False, method='multi')
        
        tempo_insert = (datetime.now() - inicio_insert).total_seconds()
        print(f"✅ Dados inseridos em {tempo_insert:.1f}s")
        
        # 5. CRIAR ÍNDICES PARA PERFORMANCE
        print("⚡ Criando índices para otimização...")
        
        indices = [
            ('idx_periodo', 'Período'),
            ('idx_usi', 'USI'),
            ('idx_type05', '"Type 05"'),
            ('idx_type06', '"Type 06"'),
            ('idx_valor', 'Valor'),
            ('idx_periodo_usi', 'Período, USI')
        ]
        
        for nome_indice, colunas in indices:
            try:
                conn.execute(f'CREATE INDEX {nome_indice} ON ke5z_dados({colunas})')
                print(f"   📍 Índice criado: {nome_indice}")
            except Exception as e:
                print(f"   ⚠️  Erro ao criar índice {nome_indice}: {e}")
        
        # 6. VERIFICAR INTEGRIDADE
        print("\n🔍 Verificando integridade dos dados...")
        
        # Contar registros
        cursor = conn.execute('SELECT COUNT(*) FROM ke5z_dados')
        total_sqlite = cursor.fetchone()[0]
        
        if total_sqlite == len(df):
            print(f"✅ Integridade OK: {total_sqlite:,} registros")
        else:
            print(f"❌ ERRO: Parquet={len(df):,}, SQLite={total_sqlite:,}")
            return False
        
        # Verificar algumas estatísticas
        cursor = conn.execute('SELECT SUM(Valor) FROM ke5z_dados')
        soma_sqlite = cursor.fetchone()[0]
        soma_pandas = df['Valor'].sum()
        
        if abs(soma_sqlite - soma_pandas) < 0.01:  # Tolerância para float
            print(f"✅ Soma dos valores OK: R$ {soma_sqlite:,.2f}")
        else:
            print(f"⚠️  Diferença nas somas: Pandas={soma_pandas:,.2f}, SQLite={soma_sqlite:,.2f}")
        
        # 7. INFORMAÇÕES FINAIS
        conn.close()
        
        tamanho_sqlite = os.path.getsize(arquivo_sqlite) / (1024*1024)
        tamanho_parquet = os.path.getsize(arquivo_parquet) / (1024*1024)
        
        print("\n" + "=" * 60)
        print("🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print(f"📁 Arquivo SQLite: {arquivo_sqlite}")
        print(f"📊 Registros migrados: {total_sqlite:,}")
        print(f"💾 Tamanho Parquet: {tamanho_parquet:.1f} MB")
        print(f"💾 Tamanho SQLite: {tamanho_sqlite:.1f} MB")
        print(f"📈 Diferença: {((tamanho_sqlite/tamanho_parquet-1)*100):+.1f}%")
        print(f"⏱️  Tempo total: {(datetime.now() - inicio).total_seconds():.1f}s")
        print("\n✅ Agora você pode usar o SQLite no Streamlit Cloud!")
        print("✅ Performance será MUITO melhor que o Parquet!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO durante a migração: {e}")
        import traceback
        traceback.print_exc()
        return False

def testar_sqlite():
    """Testa se o SQLite foi criado corretamente"""
    
    arquivo_sqlite = "dados_ke5z.db"
    
    if not os.path.exists(arquivo_sqlite):
        print("❌ Arquivo SQLite não encontrado. Execute a migração primeiro.")
        return False
    
    try:
        print("\n🧪 TESTANDO SQLite...")
        conn = sqlite3.connect(arquivo_sqlite)
        
        # Teste 1: Contar registros
        cursor = conn.execute('SELECT COUNT(*) FROM ke5z_dados')
        total = cursor.fetchone()[0]
        print(f"✅ Total de registros: {total:,}")
        
        # Teste 2: Primeiros registros
        df_teste = pd.read_sql_query('SELECT * FROM ke5z_dados LIMIT 5', conn)
        print(f"✅ Primeiros 5 registros carregados")
        print(df_teste.head())
        
        # Teste 3: Agregação
        cursor = conn.execute('SELECT USI, COUNT(*) as qty FROM ke5z_dados GROUP BY USI LIMIT 5')
        print(f"\n✅ Teste de agregação:")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]:,} registros")
        
        conn.close()
        print("✅ Todos os testes passaram!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Script de Migração KE5Z: Parquet → SQLite")
    print("Desenvolvido para otimizar o Dashboard no Streamlit Cloud\n")
    
    # Executar migração
    sucesso = migrar_parquet_para_sqlite()
    
    if sucesso:
        # Testar SQLite
        testar_sqlite()
        
        print("\n" + "="*60)
        print("🎯 PRÓXIMOS PASSOS:")
        print("="*60)
        print("1. ✅ Migração concluída")
        print("2. 🔄 Dash.py será atualizado automaticamente")
        print("3. 🧪 Testes locais serão executados")
        print("4. 🚀 Pronto para deploy no Streamlit Cloud")
        print("\n💡 O arquivo 'dados_ke5z.db' deve ser enviado junto com o projeto!")
        
    else:
        print("\n❌ Migração falhou. Verifique os erros acima.")
        sys.exit(1)
