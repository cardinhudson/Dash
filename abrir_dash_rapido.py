#!/usr/bin/env python3
"""
Script de abertura rápida do Dashboard KE5Z
Não reinstala ambiente virtual - apenas verifica e executa
"""
import os
import sys
import subprocess
import socket
import webbrowser
import time

def verificar_python():
    """Verifica se Python está disponível"""
    try:
        result = subprocess.run([sys.executable, '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ {version}")
            return True
    except:
        pass
    
    print("❌ Python não encontrado!")
    return False

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = ['streamlit', 'pandas', 'altair', 'plotly', 'openpyxl']
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            faltando.append(dep)
            print(f"❌ {dep}")
    
    return faltando

def instalar_dependencias(faltando):
    """Instala dependências que estão faltando"""
    if not faltando:
        return True
    
    print(f"\n🔧 Instalando {len(faltando)} dependências...")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install'] + faltando + [
            '--quiet', '--no-warn-script-location'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso!")
            return True
        else:
            print(f"❌ Erro na instalação: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def encontrar_porta_livre():
    """Encontra uma porta livre para o Streamlit"""
    for porta in range(8501, 8521):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', porta))
                return porta
        except OSError:
            continue
    return 8521  # Fallback

def verificar_dados():
    """Verifica se os arquivos de dados existem"""
    arquivo_dados = os.path.join("KE5Z", "KE5Z.parquet")
    
    if os.path.exists(arquivo_dados):
        size_mb = os.path.getsize(arquivo_dados) / (1024 * 1024)
        print(f"✅ Dados encontrados ({size_mb:.1f} MB)")
        
        if size_mb > 50:
            print("⚠️  Arquivo grande - otimizações automáticas ativas")
        
        return True
    else:
        print("⚠️  Arquivo de dados não encontrado")
        print("💡 Dashboard funcionará com dados de exemplo")
        return False

def abrir_navegador(porta):
    """Abre o navegador automaticamente"""
    url = f"http://localhost:{porta}"
    try:
        webbrowser.open(url)
        print(f"🌐 Navegador aberto: {url}")
    except:
        print(f"🌐 Acesse manualmente: {url}")

def main():
    """Função principal"""
    print("DASHBOARD KE5Z - ABERTURA RAPIDA")
    print("=" * 50)
    
    # Verificar se estamos na pasta correta
    if not os.path.exists("Dash.py"):
        print("❌ ERRO: Arquivo Dash.py não encontrado!")
        print("\n💡 SOLUÇÃO:")
        print("   1. Navegue até a pasta do projeto")
        print("   2. Execute este script na pasta correta")
        input("\nPressione Enter para sair...")
        return False
    
    print("📁 Pasta do projeto: OK")
    
    # Verificar Python
    print("\n🐍 Verificando Python...")
    if not verificar_python():
        input("\nPressione Enter para sair...")
        return False
    
    # Verificar dependências
    print("\n📦 Verificando dependências...")
    faltando = verificar_dependencias()
    
    if faltando:
        print(f"\n⚠️  Faltam {len(faltando)} dependências: {', '.join(faltando)}")
        resposta = input("\n🔧 Instalar dependências automaticamente? (s/n): ")
        
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            if not instalar_dependencias(faltando):
                input("\nPressione Enter para sair...")
                return False
        else:
            print("\n❌ Dependências necessárias não instaladas")
            print("💡 Execute 'abrir_dashboard.bat' para instalação completa")
            input("\nPressione Enter para sair...")
            return False
    
    # Verificar dados
    print("\n📊 Verificando dados...")
    verificar_dados()
    
    # Encontrar porta livre
    print("\n🌐 Configurando servidor...")
    porta = encontrar_porta_livre()
    print(f"✅ Porta disponível: {porta}")
    
    # Mostrar informações de acesso
    print("\n" + "=" * 50)
    print("    🎯 INFORMAÇÕES DE ACESSO")
    print("=" * 50)
    print(f"\n🌐 URLs de Acesso:")
    print(f"   Local:    http://localhost:{porta}")
    print(f"   Rede:     http://{os.environ.get('COMPUTERNAME', 'localhost')}:{porta}")
    
    print(f"\n👥 Usuários Disponíveis:")
    print("   👑 admin / admin123 (Administrador)")
    print("   👤 demo / demo123 (Usuário)")
    print("   👤 joao / hello (Usuário)")
    print("   👤 hudson / hudson123 (Usuário)")
    print("   👤 lauro / hello (Usuário)")
    
    print(f"\n💡 Recursos Ativos:")
    print("   💾 Cache inteligente")
    print("   🧹 Limpeza automática de memória")
    print("   📊 Otimizações para performance")
    print("   🔐 Sistema de autenticação")
    
    print(f"\n⚠️  Para parar: Pressione Ctrl+C")
    print("🔄 Para recarregar: Pressione F5 no navegador")
    
    # Aguardar 3 segundos e abrir navegador
    print(f"\n🚀 Iniciando dashboard em 3 segundos...")
    time.sleep(3)
    
    # Abrir navegador
    abrir_navegador(porta)
    
    print("\n" + "=" * 50)
    print("    📊 DASHBOARD KE5Z EXECUTANDO...")
    print("=" * 50)
    print()
    
    try:
        # Executar Streamlit
        cmd = [
            sys.executable, '-m', 'streamlit', 'run', 'Dash.py',
            '--server.port', str(porta),
            '--server.headless', 'true'
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar dashboard: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   Execute 'abrir_dashboard.bat' para configuração completa")
    
    print("\n" + "=" * 50)
    print("    👋 DASHBOARD ENCERRADO")
    print("=" * 50)
    print("\n💡 Para iniciar novamente: Execute este arquivo")
    print("🔧 Para configuração completa: Execute abrir_dashboard.bat")
    
    input("\nPressione Enter para sair...")
    return True

if __name__ == "__main__":
    main()
