import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns


#  Condition. Hacer para una serie de subidas y guardar resultados - Graficas dist, probabilidad de bajar,
#  probabilidad de bajar 0.1, 0.2..., resultados test, graficas test
sp_up = 0.3

print(f"RESULTADOS PARA UNA SUBIDA DE {sp_up}% del SP500 y una subida cualquiera del VIX")
# Cargar el archivo Excel
file_path = 'input/vix_model_data.xlsx'
vix_historical_data = pd.read_excel(file_path)

# Añadir columnas para los valores futuros del SP500 en t+1, t+2, ..., t+7
for i in range(1, 8):
    vix_historical_data[f'SP500 t+{i}'] = vix_historical_data['SP500'].shift(-i)

# Calcular los cambios porcentuales para cada día futuro
for i in range(1, 8):
    vix_historical_data[f'SP500 Change t+{i} (%)'] = ((vix_historical_data[f'SP500 t+{i}'] - vix_historical_data['SP500']) / vix_historical_data['SP500']) * 100

# Seleccionar las columnas relevantes
columns = ['Trade Date', 'VIX', 'SP500', 'SP500 Change 1D (%)', 'VIX Change 1D (%)', 'SP500 Change t+1 (%)', 
           'SP500 Change t+2 (%)', 'SP500 Change t+3 (%)','SP500 Change t+4 (%)','SP500 Change t+5 (%)',
           'SP500 Change t+6 (%)', 'SP500 Change t+7 (%)']
df_filtered = vix_historical_data[columns].copy()

# Convertir fechas a datetime
df_filtered['Trade Date'] = pd.to_datetime(df_filtered['Trade Date'])

# Filtrar las filas donde SP500 sube >= sp_up y VIX sube > 0%
df_condition = df_filtered[(df_filtered['SP500 Change 1D (%)'] >= sp_up) & (df_filtered['VIX Change 1D (%)'] > 0)]

# Crear el grupo de "días sin la condición"
df_non_condition = df_filtered[~((df_filtered['SP500 Change 1D (%)'] >= sp_up) & (df_filtered['VIX Change 1D (%)'] > 0))]

# Calcular probabilidad de que baje y que suba
# Todo
probs = {}
for i in range(1,8):
    freq_down = len(df_condition[df_condition[f"SP500 Change t+{i} (%)"]<=0])
    freq_up = len(df_condition[df_condition[f"SP500 Change t+{i} (%)"]>0])
    prob_down = freq_down/(freq_down+freq_up)
    prob_up = freq_up/(freq_down+freq_up)
    probs[f"t+{i}"] = prob_down

# Calcular promedios y medianas de los cambios porcentuales
mean_changes = {f't+{i}': df_condition[f'SP500 Change t+{i} (%)'].mean() for i in range(1, 8)}
median_changes = {f't+{i}': df_condition[f'SP500 Change t+{i} (%)'].median() for i in range(1, 8)}


# Realizar un test t de dos muestras independientes para cada una de ellas
# t_statistic, p_value = stats.ttest_ind(df_condition['SP500 Change 1D (%)'].dropna(), df_non_condition['SP500 Change 1D (%)'].dropna())
test_results = {f't+{i}': stats.ttest_ind(df_condition[f'SP500 Change t+{i} (%)'].dropna(),
                                                     df_non_condition[f'SP500 Change t+{i} (%)'].dropna()) 
                                                     for i in range(1, 8)}
# Mostrar resultados
for i in test_results:
    print(f"Resultados para {i}--------------------------------")
    print(f'Estadístico t: {test_results[i][0]:.3f}')
    print(f'Valor p: {test_results[i][1]:.3f}')


# Graficar la distribución y las estadísticas (media y mediana)
plt.figure(figsize=(12, 10))  # Ajustamos el tamaño total para que no sea tan largo
for i in range(1, 8):
    plt.subplot(4, 2, i)  # Cambiar a 4 filas y 2 columnas
    sns.histplot(df_condition[f'SP500 Change t+{i} (%)'], kde=True, color='skyblue', stat='density', bins=30)
    plt.axvline(mean_changes[f't+{i}'], color='red', linestyle='--', label=f'Media: {mean_changes[f"t+{i}"]:.2f}%')
    plt.axvline(median_changes[f't+{i}'], color='green', linestyle='-', label=f'Mediana: {median_changes[f"t+{i}"]:.2f}%')
    plt.title(f'Distribución de los cambios porcentuales SP500 en t+{i}')
    plt.xlabel('Cambio Porcentual (%)')
    plt.ylabel('Densidad')
    plt.legend()
    plt.grid(True)

plt.tight_layout()  # Ajusta el diseño para que no se solapen
plt.show()

# Graficar test estadistico
# todo

# Guardar resultados
df_condition.to_excel('output/df_condition.xlsx')
