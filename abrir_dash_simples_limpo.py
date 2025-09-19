#!/usr/bin/env python3
"""
Script Python simples para abrir o Dashboard KE5Z
Sem emojis, máxima compatibilidade
"""
import os
import sys
import subprocess
import webbrowser
import time

def main():
    print("DASHBOARD KE5Z - ABERTURA SIMPLES")
    print("=" * 50)
    
    # Verificar pasta
    if not os.path.exists("Dash.py"):
        print("ERRO: Arquivo Dash.py nao encontrado!")
        print("Execute este script na pasta do projeto")
        input("Pressione Enter para sair...")
        return
    
    print("Pasta do projeto: OK")
    
    # Verificar Python
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Python: {result.stdout.strip()}")
        else:
            print("ERRO: Python nao disponivel")
            return
    except:
        print("ERRO: Python nao encontrado")
        return
    
    # Verificar dependencias
    print("Verificando dependencias...")
    dependencias = ['streamlit', 'pandas']
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  {dep}: OK")
        except ImportError:
            faltando.append(dep)
            print(f"  {dep}: FALTANDO")
    
    # Instalar se necessario
    if faltando:
        print(f"Instalando {len(faltando)} dependencias...")
        try:
            cmd = [sys.executable, '-m', 'pip', 'install'] + faltando + ['--quiet']
            result = subprocess.run(cmd)
            if result.returncode == 0:
                print("Dependencias instaladas com sucesso!")
            else:
                print("ERRO na instalacao")
                return
        except:
            print("ERRO na instalacao")
            return
    
    # Verificar dados
    if os.path.exists("KE5Z/KE5Z.parquet"):
        size_mb = os.path.getsize("KE5Z/KE5Z.parquet") / (1024 * 1024)
        print(f"Dados: OK ({size_mb:.1f} MB)")
    else:
        print("Dados: Nao encontrados (usara dados de exemplo)")
    
    # Informacoes de acesso
    print("\n" + "=" * 50)
    print("INFORMACOES DE ACESSO")
    print("=" * 50)
    print("URL: http://localhost:8501")
    print("Usuarios:")
    print("  admin / admin123 (Administrador)")
    print("  demo / demo123 (Usuario)")
    print("\nPara parar: Pressione Ctrl+C")
    
    # Abrir navegador
    print("\nAbrindo navegador...")
    try:
        webbrowser.open("http://localhost:8501")
    except:
        print("Navegador nao abriu automaticamente")
        print("Acesse manualmente: http://localhost:8501")
    
    # Aguardar e executar
    print("\nIniciando dashboard em 3 segundos...")
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("DASHBOARD EXECUTANDO...")
    print("=" * 50)
    
    try:
        # Executar Streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', 'Dash.py', '--server.port', '8501']
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nDashboard interrompido pelo usuario")
    except Exception as e:
        print(f"\nERRO: {e}")
    
    print("\nDashboard encerrado")
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
