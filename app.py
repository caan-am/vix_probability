import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def analizar_vix(vix_df, vix_actual, strike, dias_vencimiento):
    df_filtrado = vix_df[(vix_df["^VIX"] >= vix_actual - 2.5) & (vix_df["^VIX"] < vix_actual + 2.5)]
    vix_futuro = df_filtrado[["Date", f"VIX_{dias_vencimiento}d_futuro"]].dropna()
    
    vix_futuro["Perdida"] = np.maximum(vix_futuro[f"VIX_{dias_vencimiento}d_futuro"] - strike, 0)
    
    prob_OTM = np.mean(vix_futuro[f"VIX_{dias_vencimiento}d_futuro"] <= strike)  # VIX termina por debajo del strike
    prob_ITM = 1 - prob_OTM  # VIX termina por encima del strike
    
    prima_breakeven = vix_futuro["Perdida"].mean()
    
    umbral_perdida = np.percentile(vix_futuro["Perdida"], 95)  # Definir evento de grandes pérdidas como percentil 95
    eventos_perdida = vix_futuro[vix_futuro["Perdida"] > umbral_perdida]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.histplot(vix_futuro[f"VIX_{dias_vencimiento}d_futuro"], bins=30, kde=True, color="royalblue", alpha=0.6, ax=ax)
    ax.axvline(vix_actual, color='green', linestyle='--', label=f'VIX Actual ({vix_actual})')
    ax.axvline(strike, color='red', linestyle='--', label=f'Strike ({strike})')
    ax.set_title(f"Distribución del VIX en {dias_vencimiento} días")
    ax.set_xlabel("Nivel del VIX en el futuro")
    ax.set_ylabel("Frecuencia")
    ax.legend()
    
    return prob_ITM, prob_OTM, prima_breakeven, eventos_perdida, fig

def ejecutar():
    vix_actual = float(entry_vix.get())
    strike = float(entry_strike.get())
    dias_vencimiento = int(entry_dias.get())
    
    prob_ITM, prob_OTM, prima_breakeven, eventos_perdida, fig = analizar_vix(vix, vix_actual, strike, dias_vencimiento)
    
    resultado.set(f"Probabilidad ITM: {prob_ITM:.2%}\n"
                  f"Probabilidad OTM: {prob_OTM:.2%}\n"
                  f"Prima breakeven: {prima_breakeven:.2f}")
    
    for widget in frame_plot.winfo_children():  # Limpiar gráfico anterior
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    eventos_texto.set("Eventos de Grandes Pérdidas:\n" + eventos_perdida.to_string(index=False))

vix = pd.read_csv("vix.csv") 

root = tk.Tk()
root.title("Análisis de Opciones sobre el VIX")

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0)

frame_plot = ttk.Frame(root, padding=20)
frame_plot.grid(row=0, column=1)

label_vix = ttk.Label(frame, text="Nivel actual del VIX:")
label_vix.grid(row=0, column=0)
entry_vix = ttk.Entry(frame)
entry_vix.grid(row=0, column=1)

label_strike = ttk.Label(frame, text="Strike de la Call:")
label_strike.grid(row=1, column=0)
entry_strike = ttk.Entry(frame)
entry_strike.grid(row=1, column=1)

label_dias = ttk.Label(frame, text="Días hasta vencimiento:")
label_dias.grid(row=2, column=0)
entry_dias = ttk.Entry(frame)
entry_dias.grid(row=2, column=1)

resultado = tk.StringVar()
label_resultado = ttk.Label(frame, textvariable=resultado, justify="left")
label_resultado.grid(row=4, column=0, columnspan=2)

eventos_texto = tk.StringVar()
label_eventos = ttk.Label(frame, textvariable=eventos_texto, justify="left")
label_eventos.grid(row=5, column=0, columnspan=2)

boton = ttk.Button(frame, text="Calcular", command=ejecutar)
boton.grid(row=3, column=0, columnspan=2)

root.mainloop()
