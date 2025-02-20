import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analizar_vix(vix_df, vix_actual, strike, dias_vencimiento):
    # Filtrar datos donde el VIX estaba en el rango del nivel actual
    df_filtrado = vix_df[(vix_df["^VIX"] >= vix_actual - 2.5) & (vix_df["^VIX"] < vix_actual + 2.5)]
    
    # Extraer los valores del VIX en la fecha de vencimiento
    vix_futuro = df_filtrado[f"VIX_{dias_vencimiento}d_futuro"].dropna()
    
    # Calcular probabilidades
    prob_OTM = np.mean(vix_futuro > strike)  # VIX termina por encima del strike
    prob_ITM = 1 - prob_OTM  # VIX termina por debajo del strike
    
    # Calcular prima breakeven: el promedio de pérdidas en puts vendidas
    perdidas = np.maximum(vix_futuro - strike, 0)  # Para calls (correcto)
    prima_breakeven = perdidas.mean()
    
    # Graficar distribución del VIX en el vencimiento
    plt.figure(figsize=(10, 6))
    sns.histplot(vix_futuro, bins=30, kde=True, color="royalblue", alpha=0.6)
    plt.axvline(vix_actual, color='green', linestyle='--', label=f'VIX Actual ({vix_actual})')
    plt.axvline(strike, color='red', linestyle='--', label=f'Strike ({strike})')
    plt.title(f"Distribución del VIX en {dias_vencimiento} días")
    plt.xlabel("Nivel del VIX en el futuro")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Mostrar resultados
    print(f"Probabilidad de que el VIX termine por ENCIMA del strike: {prob_OTM:.2%}")
    print(f"Probabilidad de que el VIX termine por DEBAJO del strike: {prob_ITM:.2%}")
    print(f"Prima breakeven para puts: {prima_breakeven:.2f}")
    
    return prob_OTM, prob_ITM, prima_breakeven

# Ejemplo de uso
vix = pd.read_csv("vix.csv")
analizar_vix(vix, vix_actual=14.48, strike=25, dias_vencimiento=3)