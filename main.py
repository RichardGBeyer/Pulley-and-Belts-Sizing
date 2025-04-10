# main.py

import customtkinter as ctk
from customtkinter import CTkImage

from dimensionamento import dimensionar

# Configuração da Janela Principal
ctk.set_appearance_mode("white")  # Modo de aparência segue o sistema
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Dimensionador de Polias e Correias")
app.geometry("600x700")
app.resizable(False, False)

# Rótulo informativo no limite inferior da tela
informacao_label = ctk.CTkLabel(
    app,
    text="Desenvolvido por Richard Gerhard Beyer - PMP 11429/25 - Rev. 0",
    font=("Arial", 14),  # Tamanho da fonte menor para parecer um rodapé
    anchor="n"  # Alinha o texto no centro
)
informacao_label.pack(side="bottom", pady=5, fill="x")  # Posiciona na parte inferior

# Função para abrir uma nova janela com o resultado
def mostrar_resultado(resultado):
    """
    Abre uma nova janela para exibir o resultado do dimensionamento.
    """
    # Cria uma nova janela
    janela_resultado = ctk.CTkToplevel(app)
    janela_resultado.title("Resultado do Dimensionamento")
    janela_resultado.geometry("500x550")
    
    # Garante que a nova janela fique na frente da principal
    janela_resultado.grab_set()  # Bloqueia a interação com a janela principal
    janela_resultado.focus_force()  # Força o foco na nova janela
    janela_resultado.resizable(False, False)
    
    # Widget de texto para exibir o resultado
    texto_resultado = ctk.CTkTextbox(janela_resultado, wrap="word", width=580, height=520)
    texto_resultado.pack(pady=10)
    

    # Insere o resultado no widget de texto
    texto_resultado.insert("1.0", resultado)
    
    # Torna o texto editável para permitir cópia
    texto_resultado.configure(state="normal")  # O texto já é copiável por padrão

# Botão para calcular
def calcular():
    try:
        # Entradas do usuário
        rotacao_bomba_valor = float(rotacao_bomba.get())  # Rotação da bomba (em rpm)
        freq_motor_valor = int(freq_motor.get())  # Frequência do motor (em Hz)
        num_polos_valor = int(num_polos.get())  # Número de pólos do motor
        potencia_motor_valor = float(potencia_motor.get())  # Potência do motor (em kW)
        modelo_mancal_valor = tamanho_mancal.get().strip()  # Modelo do mancal (string)

        # Chama a função de dimensionamento
        resultado = dimensionar(
            rotacao_bomba_valor,
            freq_motor_valor,
            num_polos_valor,
            potencia_motor_valor,
            modelo_mancal_valor
        )

        # Abre uma nova janela com o resultado
        mostrar_resultado(resultado)

    except ValueError as e:
        # Captura erros de conversão ou dados não encontrados
        resultado_label.configure(text=f"Erro: {e}")
    except ZeroDivisionError:
        # Captura divisão por zero (ex.: rotação da bomba igual a 0)
        resultado_label.configure(text="Erro: A rotação da bomba não pode ser zero.")
    except Exception as e:
        # Captura outros erros inesperados
        resultado_label.configure(text=f"Erro inesperado: {e}")

# Rótulos e Entradas
ctk.CTkLabel(app, text="Rotação da Bomba (rpm):").pack(pady=5)
rotacao_bomba = ctk.CTkEntry(app)
rotacao_bomba.pack(pady=5)


ctk.CTkLabel(app, text="Frequência do Motor (Hz):").pack(pady=5)
freq_motor = ctk.CTkComboBox(app, values=["60", "50"],
state="readonly"  # Bloqueia a entrada manual de texto
)
freq_motor.pack(pady=5)

ctk.CTkLabel(app, text="Número de Pólos:").pack(pady=5)
num_polos = ctk.CTkComboBox(app, values=["6", "8", "4"],
state="readonly"  # Bloqueia a entrada manual de texto
)
num_polos.pack(pady=5)

ctk.CTkLabel(app, text="Potência do Motor (kW):").pack(pady=5)
potencia_motor = ctk.CTkComboBox(app, values=["0.75", "1.1", "1.5", "2.2", "3.0", "3.7", "4.5", "5.5", "7.5",
"9.2", "11.0", "15.0", "18.5", "22.0", "30.0", "37.0", "45.0", "55.0"],
state="readonly"  # Bloqueia a entrada manual de texto
)
potencia_motor.pack(pady=5)

# Novo campo para o tamanho do mancal
ctk.CTkLabel(app, text="Tamanho do Mancal:").pack(pady=5)
tamanho_mancal = ctk.CTkComboBox(app, values=[
    "NM011", "NM021", "NM031", "NM038", "NM045", 
    "NM053", "NM063", "NM076", "NM090", "NM105", "NM125"
],
state="readonly"  # Bloqueia a entrada manual de texto
)
tamanho_mancal.pack(pady=5)

# Botão para calcular
calcular_button = ctk.CTkButton(app, text="Calcular", command=calcular)
calcular_button.pack(pady=10)

# Rótulo para exibir mensagens de erro
resultado_label = ctk.CTkLabel(app, text="", wraplength=550)
resultado_label.pack(pady=10)

# Rodar a Aplicação
app.mainloop()