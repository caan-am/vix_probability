import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
# Definir una lista de valores para sp_up
sp_up = 0.5

# Cargar el archivo Excel
file_path = 'input/vix_model_data.xlsx'
vix_historical_data = pd.read_excel(file_path)

## PREPARAR DATOS ---------------------------------------------------------------
# Añadir columnas para los valores futuros del SP500 en t+1, t+2, ..., t+7
for i in range(1, 8):
    vix_historical_data[f'SP500 t+{i}'] = vix_historical_data['SP500'].shift(-i)

# Calcular los cambios porcentuales para cada día futuro
for i in range(1, 8):
    vix_historical_data[f'SP500 Change t+{i} (%)'] = (
        (vix_historical_data[f'SP500 t+{i}'] - vix_historical_data['SP500']) / vix_historical_data['SP500']
    ) * 100

# Seleccionar las columnas relevantes
columns = ['Trade Date', 'VIX', 'SP500', 'SP500 Change 1D (%)', 'VIX Change 1D (%)'] + \
          [f'SP500 Change t+{i} (%)' for i in range(1, 8)]
df_filtered = vix_historical_data[columns].copy()

# Convertir fechas a datetime
df_filtered['Trade Date'] = pd.to_datetime(df_filtered['Trade Date'])

# Filtrar las filas donde SP500 sube >= sp_up y VIX sube > 0%
df_condition = df_filtered[(df_filtered['SP500 Change 1D (%)'] >= sp_up) & (df_filtered['VIX Change 1D (%)'] > 0)]
df_non_condition = df_filtered[~((df_filtered['SP500 Change 1D (%)'] >= sp_up) & (df_filtered['VIX Change 1D (%)'] > 0))]

## TEST ---------------------------------------------------------------
# Calcular promedios y medianas
mean_changes = {f't+{i}': df_condition[f'SP500 Change t+{i} (%)'].mean() for i in range(1, 8)}
median_changes = {f't+{i}': df_condition[f'SP500 Change t+{i} (%)'].median() for i in range(1, 8)}
    
# Test t de dos muestras independientes
test_results = {f't+{i}': stats.ttest_ind(df_condition[f'SP500 Change t+{i} (%)'].dropna(),
                                               df_non_condition[f'SP500 Change t+{i} (%)'].dropna(),
                                               equal_var=False)  # Asume varianzas desiguales
                    for i in range(1, 8)}

# for i in test_results:
#         print(f"Resultados para {i}--------------------------------")
#         print(f'Estadístico t: {test_results[i][0]:.3f}')
#         print(f'Valor p: {test_results[i][1]:.3f}')


## TEST BOOTSTRAP ---------------------------------------------------------------
# Definir el número de iteraciones para el bootstrap
num_samples = 10000

# Días a analizar
days = [f't+{i}' for i in range(1, 8)]

# Crear la figura con subplots
fig, axes = plt.subplots(2, 4, figsize=(20, 10))  # 2 filas, 4 columnas
axes = axes.flatten()  # Aplanar para iterar más fácilmente

# Diccionario para almacenar los resultados
bootstrap_results = {}

for idx, day in enumerate(days):
    # Obtener el tamaño de la muestra original
    sample_size = len(df_condition)
    
    # Generar 1000 muestras aleatorias con reemplazo
    bootstrap_means = [
        np.mean(np.random.choice(df_non_condition[f'SP500 Change {day} (%)'].dropna(), size=sample_size, replace=True))
        for _ in range(num_samples)
    ]
    
    # Media observada
    observed_mean = df_condition[f'SP500 Change {day} (%)'].mean()
    
    # Calcular el percentil de la media observada dentro de la distribución bootstrap
    percentile = np.sum(np.array(bootstrap_means) < observed_mean) / num_samples * 100
    
    # Evaluar si está en la cola (p < 0.05 -> percentil < 2.5 o > 97.5)
    if percentile < 2.5 or percentile > 97.5:
        cola_texto = f"¡En la cola! ({percentile:.1f}%)"
        color_texto = 'red'
    else:
        cola_texto = f"Percentil: {percentile:.1f}%"
        color_texto = 'green'
    
    # Guardar resultados
    bootstrap_results[day] = {'bootstrap_means': bootstrap_means, 'observed_mean': observed_mean, 'percentile': percentile}

    # --- VISUALIZAR EN SUBPLOT ---
    ax = axes[idx]
    sns.histplot(bootstrap_means, bins=30, kde=True, color='blue', alpha=0.6, ax=ax)
    ax.axvline(observed_mean, color='red', linestyle='dashed', linewidth=2, label="Media Observada")
    
    # Añadir texto con el percentil
    ax.text(0.95, 0.85, cola_texto, transform=ax.transAxes, fontsize=12, color=color_texto,
            verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', alpha=0.7))
    
    # Configuración del título y etiquetas
    ax.set_title(f'Distribución Bootstrap ({day})')
    ax.set_xlabel('Cambio % en SP500')
    ax.set_ylabel('Frecuencia')
    ax.legend()

# Ajustar el layout para que no se solapen los gráficos
plt.tight_layout()

# Guardar la imagen
plt.savefig("bootstrap_test.png", dpi=300, bbox_inches='tight')

# Mostrar la imagen en pantalla
plt.show()


# # Configuración de los gráficos
# plt.figure(figsize=(12, 6))

# # Extraer los valores medios y medianos
# x_labels = [f't+{i}' for i in range(1, 8)]
# mean_values = [mean_changes[t] for t in x_labels]
# median_values = [median_changes[t] for t in x_labels]

# # Crear el gráfico de barras
# plt.subplot(1, 2, 1)
# sns.barplot(x=x_labels, y=mean_values, color='blue', alpha=0.6, label='Promedio')
# sns.barplot(x=x_labels, y=median_values, color='red', alpha=0.6, label='Mediana')
# plt.axhline(0, color='black', linewidth=1)  # Línea en 0 para referencia
# plt.title('Cambio en SP500 después de la condición')
# plt.ylabel('Cambio (%)')
# plt.legend()

# # Extraer los valores p del test t
# p_values = [test_results[t].pvalue for t in x_labels]

# # Gráfico de valores p
# plt.subplot(1, 2, 2)
# sns.barplot(x=x_labels, y=p_values, color='purple', alpha=0.6)
# plt.axhline(0.05, color='red', linestyle='dashed', linewidth=1, label='Nivel 0.05 (significativo)')
# plt.title('Valores p del test t')
# plt.ylabel('Valor p')
# plt.legend()

# # Mostrar gráficos
# plt.tight_layout()
# plt.show()


# ## TEST ---------------------------------------------------------------
# # Iterar sobre cada valor de sp_up
# for sp_up in sp_up_values:
#     print(f"\nRESULTADOS PARA UNA SUBIDA DE {sp_up}% del SP500 y una subida cualquiera del VIX")
    
    
    
#     # Calcular probabilidad de que baje
#     probs = {}
#     for i in range(1, 8):
#         freq_down = len(df_condition[df_condition[f"SP500 Change t+{i} (%)"] <= 0])
#         freq_up = len(df_condition[df_condition[f"SP500 Change t+{i} (%)"] > 0])
#         prob_down = freq_down / (freq_down + freq_up) if (freq_down + freq_up) > 0 else 0
#         probs[f"t+{i}"] = prob_down
    
    
## DIBUJAR DISTRIBUCIONES ---------------------------------------------------------------

# Crear carpeta para guardar las imágenes
output_folder = "sp500_distributions_fixed_bins"
os.makedirs(output_folder, exist_ok=True)

bin_probabilities = {}

for i in range(1, 8):
    # Obtener datos
    data = df_condition[f"SP500 Change t+{i} (%)"].dropna()
    
    # Definir bins fijos de 0.5 en 0.5
    min_val, max_val = np.floor(data.min()), np.ceil(data.max())
    bins = np.arange(min_val, max_val + 0.5, 0.5)
    
    # Calcular histograma con bins fijos
    hist_values, bin_edges = np.histogram(data, bins=bins, density=True)
    
    # Convertir densidad a probabilidades
    bin_probs = hist_values * np.diff(bin_edges)
    cum_probs = np.cumsum(bin_probs)  # Probabilidad acumulada
    
    bin_probabilities[f't+{i}'] = cum_probs
    
    ## --- 1. GRAFICAR DISTRIBUCIÓN ---
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.histplot(data, bins=bins, kde=True, color='skyblue', stat='density', ax=ax)
    ax.axvline(mean_changes[f't+{i}'], color='red', linestyle='--', label=f'Media: {mean_changes[f"t+{i}"]:.2f}%')
    ax.axvline(median_changes[f't+{i}'], color='green', linestyle='-', label=f'Mediana: {median_changes[f"t+{i}"]:.2f}%')
    ax.set_title(f'Distribución SP500 en t+{i} con bins de 0.5%')
    ax.set_xlabel('Cambio Porcentual (%)')
    ax.set_ylabel('Densidad')
    ax.legend()
    ax.grid(True)

    # Guardar imagen del histograma
    hist_path = os.path.join(output_folder, f"sp500_distribution_t+{i}.png")
    plt.savefig(hist_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    ## --- 2. CREAR TABLA DE PROBABILIDADES ---
    prob_df = pd.DataFrame({
        'Rango (%)': [f"{bin_edges[j]:.2f} >> {bin_edges[j+1]:.2f}" for j in range(len(bin_probs))],
        'Prob. Acumulada (%)': [f"{cum_probs[j]*100:.2f}" for j in range(len(bin_probs))]
    })
    
    # Ajustar tamaño y dividir la tabla si es muy larga
    fig, ax = plt.subplots(figsize=(8, min(10, len(prob_df) * 0.4)))  # Ajustar altura dinámicamente
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(cellText=prob_df.values,
                      colLabels=prob_df.columns,
                      cellLoc='center',
                      loc='center',
                      colWidths=[0.4, 0.4])  # Ajustar ancho de columnas
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)  # Reducir fuente para que entre mejor
    
    # Guardar imagen de la tabla
    table_path = os.path.join(output_folder, f"sp500_table_t+{i}.png")
    plt.savefig(table_path, dpi=300, bbox_inches='tight')
    plt.show()



    
# Guardar resultados a Excel
output_filename = f'output/df_condition_sp_up_{sp_up}.xlsx'
df_condition.to_excel(output_filename, index=False)
print(f"Resultados guardados en {output_filename}")