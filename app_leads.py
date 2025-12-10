import customtkinter as ctk
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
import platform
import subprocess
import webbrowser  # Para abrir seu site quando clicarem no link

# Configuração da Aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") 

class AppLeads(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Variável para guardar o nome do arquivo gerado
        self.ultimo_arquivo = None

        # Configuração da Janela
        self.title("Lead Hunter PRO - Powered by HubNeoSoma")
        self.geometry("600x600") # Aumentei um pouco para caber o rodapé novo
        self.resizable(False, False)

        # Título Principal
        self.label_titulo = ctk.CTkLabel(self, text="LEAD HUNTER PRO", font=("Roboto", 26, "bold"))
        self.label_titulo.pack(pady=(20, 5))
        
        # Subtítulo (opcional)
        self.label_sub = ctk.CTkLabel(self, text="Automação de Captação de Clientes", text_color="gray")
        self.label_sub.pack(pady=(0, 15))

        # Entrada de Busca
        self.entry_busca = ctk.CTkEntry(self, placeholder_text="Ex: Pizzarias em Campinas", width=400, height=40)
        self.entry_busca.pack(pady=5)

        # Botão Iniciar
        self.btn_iniciar = ctk.CTkButton(
            self, text="INICIAR CAPTAÇÃO", 
            command=self.start_thread, 
            width=200, height=40, 
            fg_color="#00C853", hover_color="#009624",
            font=("Arial", 12, "bold")
        )
        self.btn_iniciar.pack(pady=10)

        # Área de Log
        self.textbox_log = ctk.CTkTextbox(self, width=550, height=220)
        self.textbox_log.pack(pady=10)
        self.textbox_log.insert("0.0", "Sistema pronto para uso.\nDigite o nicho acima e clique em Iniciar.\n")

        # Botão de Abrir Arquivo (Começa Desativado)
        self.btn_abrir = ctk.CTkButton(
            self, 
            text="📂 AGUARDANDO TÉRMINO...", 
            state="disabled", 
            command=self.abrir_arquivo, 
            width=250, 
            height=40,
            fg_color="#37474F"
        )
        self.btn_abrir.pack(pady=10)
        
        # --- RODAPÉ HUBNEOSOMA ---
        # Frame invisível para organizar o rodapé
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", pady=15)

        # Linha 1: Direitos
        self.label_copy = ctk.CTkLabel(
            self.footer_frame, 
            text="HubNeoSoma © Direitos Autorais Reservados", 
            text_color="gray", 
            font=("Arial", 11)
        )
        self.label_copy.pack()

        # Linha 2: Contato e Site (Clicável)
        texto_contato = "📞 (19) 95328-7964  |  🌐 www.hubneosoma.com.br"
        self.label_contact = ctk.CTkLabel(
            self.footer_frame, 
            text=texto_contato, 
            text_color="#4FC3F7", # Um azul claro para indicar link
            font=("Arial", 11, "bold"),
            cursor="hand2" # Muda o mouse para 'mãozinha'
        )
        self.label_contact.pack()
        
        # Torna o site clicável
        self.label_contact.bind("<Button-1>", lambda e: webbrowser.open("https://www.hubneosoma.com.br"))


    def log(self, mensagem):
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end")

    def start_thread(self):
        termo = self.entry_busca.get()
        if not termo:
            self.log("❌ Erro: Digite um termo para busca (Ex: Advogados em SP).")
            return
        
        self.btn_iniciar.configure(state="disabled", text="RODANDO AGUARDE...")
        self.btn_abrir.configure(state="disabled", text="⏳ CAPTURANDO DADOS...", fg_color="#37474F")
        
        thread = threading.Thread(target=self.rodar_robo, args=(termo,))
        thread.start()

    def abrir_arquivo(self):
        if self.ultimo_arquivo:
            try:
                if platform.system() == "Windows":
                    os.startfile(self.ultimo_arquivo)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", self.ultimo_arquivo])
                else:
                    subprocess.call(["xdg-open", self.ultimo_arquivo])
                self.log(f"📂 Abrindo planilha...")
            except Exception as e:
                self.log(f"Erro ao abrir: {e}")

    def rodar_robo(self, termo):
        self.log(f"🚀 Iniciando busca: {termo}")
        
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--lang=pt-BR")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
            driver.get("https://www.google.com/maps")
            time.sleep(3)
            
            ele_busca = driver.find_element(By.ID, "searchboxinput")
            ele_busca.send_keys(termo)
            ele_busca.send_keys(Keys.ENTER)
            time.sleep(4)

            self.log("⬇️ Carregando lista de empresas...")
            try:
                painel = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
                for _ in range(5): 
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", painel)
                    time.sleep(2)
            except:
                pass

            self.log("⛏️ Extraindo dados (Isso pode demorar)...")
            empresas = driver.find_elements(By.CLASS_NAME, "hfpxzc")
            dados = []

            for i, empresa in enumerate(empresas):
                try:
                    nome = empresa.get_attribute("aria-label")
                    link = empresa.get_attribute("href")
                    
                    driver.execute_script("arguments[0].scrollIntoView();", empresa)
                    empresa.click()
                    time.sleep(1.5)
                    
                    tel = "Sem Telefone"
                    try:
                        btn_tel = driver.find_element(By.CSS_SELECTOR, "button[data-item-id^='phone']")
                        tel = btn_tel.get_attribute("aria-label").replace("Telefone:", "").strip()
                    except:
                        pass
                    
                    self.log(f"✅ Capturado: {nome}")
                    dados.append({"Nome": nome, "Telefone": tel, "Link": link})
                    
                except:
                    continue

            driver.quit()

            if dados:
                nome_arq = f"leads_{termo.replace(' ', '_')}.csv"
                pd.DataFrame(dados).to_csv(nome_arq, index=False, encoding='utf-8-sig')
                self.ultimo_arquivo = nome_arq
                
                self.log(f"\n🎉 SUCESSO! {len(dados)} leads capturados.")
                self.log("Clique no botão abaixo para ver a lista.")
                
                self.btn_abrir.configure(
                    state="normal", 
                    text="📂 ABRIR PLANILHA AGORA", 
                    fg_color="#1565C0", 
                    hover_color="#0D47A1"
                )
                self.btn_iniciar.configure(state="normal", text="INICIAR NOVA CAPTAÇÃO")
            else:
                self.log("❌ Nenhum dado encontrado. Tente outro termo.")
                self.btn_iniciar.configure(state="normal", text="TENTAR NOVAMENTE")

        except Exception as e:
            self.log(f"❌ Erro: {str(e)}")
            self.btn_iniciar.configure(state="normal", text="TENTAR NOVAMENTE")

if __name__ == "__main__":
    app = AppLeads()
    app.mainloop()