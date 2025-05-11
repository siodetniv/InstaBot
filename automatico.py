import os
import time
import random
import logging
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from instagram_private_api import Client, ClientCompatPatch

# ======================= CONFIG ============================
USERNAME = ''
PASSWORD = ''
ALVO = ''  
QUANTIDADE = 20
DELAY_ENTRE_SEGUIR = (50, 90)
DELAY_ENTRE_UNFOLLOW = (60, 100)
ESPERA_HORAS = 4

# ======================= LOGGER ============================
logging.basicConfig(
    filename='instabot.log',
    filemode='a',
    format='[%(asctime)s] %(levelname)s - %(message)s',
    level=logging.INFO
)

# ======================= TKINTER INTERFACE ============================
class InstaBotApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('InstaBot by siodetniv')
        self.geometry('600x400')
        self.configure(bg='#333333')

        tk.Label(self, text='Username:', fg='#FFFFFF', bg='#333333').grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self, text='Password:', fg='#FFFFFF', bg='#333333').grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self, show='*', width=30)
        self.password_entry.grid(row=1, column=1)

        tk.Label(self, text='Alvo:', fg='#FFFFFF', bg='#333333').grid(row=2, column=0, padx=10, pady=10)
        self.alvo_entry = tk.Entry(self, width=30)
        self.alvo_entry.grid(row=2, column=1)

        tk.Button(self, text='Iniciar Bot', command=self.iniciar_bot, bg='#555555', fg='#FFFFFF').grid(row=3, columnspan=2, pady=10)

        
        self.log_output = scrolledtext.ScrolledText(self, width=70, height=15, bg='#222222', fg='#00FF00')
        self.log_output.grid(row=4, columnspan=2, padx=10, pady=10)

    def log(self, message):
        self.log_output.insert(tk.END, message + '\n')
        self.log_output.see(tk.END)

    def iniciar_bot(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        alvo = self.alvo_entry.get()

        if not username or not password or not alvo:
            messagebox.showerror('Erro', 'Todos os campos são obrigatórios!')
            return

        
        threading.Thread(target=self.run_bot, args=(username, password, alvo)).start()

    def validar_id(self, api, uid):
        try:
            user_info = api.user_info(uid)
            return True
        except Exception as e:
            self.log(f'[ERRO] ID inválido ou restrito: {uid} - {e}')
            return False

    def run_bot(self, username, password, alvo):
        try:
            api = Client(username, password)
            self.log('[LOGIN] Login realizado com sucesso ✅')
            user_id = api.username_info(alvo)['user']['pk']
            rank_token = api.generate_uuid()

            seguidores_data = api.user_followers(user_id, rank_token=rank_token)
            seguidores = seguidores_data.get('users', [])

            if not seguidores:
                self.log('[ERRO] Nenhum seguidor encontrado ou endpoint mudou.')
                return

            for user in seguidores:
                uid = user['pk']
                username = user.get('username', 'N/A')
                is_private = user.get('is_private', False)

                if is_private:
                    self.log(f'[IGNORADO] {username} é privado. Pulando.')
                    continue

                if not self.validar_id(api, uid):
                    self.log(f'[ERRO AO SEGUIR] {username}: ID inválido. Pulando.')
                    continue

                try:
                    api.friendships_create(uid)
                    self.log(f'[SEGUIR] Seguiu: {username} ({uid})')
                    time.sleep(random.randint(*DELAY_ENTRE_SEGUIR))
                except Exception as e:
                    self.log(f'[ERRO AO SEGUIR] {username}: {e}')

            time.sleep(ESPERA_HORAS * 3600)

            for user in seguidores:
                uid = user['pk']
                try:
                    api.friendships_destroy(uid)
                    self.log(f'[UNFOLLOW] Deixou de seguir: {uid}')
                    time.sleep(random.randint(*DELAY_ENTRE_UNFOLLOW))
                except Exception as e:
                    self.log(f'[ERRO UNFOLLOW] {uid}: {e}')

            self.log('🏁 OPERAÇÃO FINALIZADA COM SUCESSO 🏁')
        except Exception as e:
            self.log(f'[ERRO] {e}')

if __name__ == '__main__':
    app = InstaBotApp()
    app.mainloop()

# ======================= COMPILAR COM PYINSTALLER ============================
# Para compilar o .exe:
# 1. Instale o PyInstaller:
#    pip install pyinstaller
# 2. Compile o script:
#    pyinstaller --onefile --windowed --icon=icon.ico bot_instagram_exe.py
# 3. O .exe estará na pasta 'dist'.
