import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
# Filtrar los datos donde el VIX actual está entre 15 y 20
vix = pd.read_csv("vix.csv")
vix_filtered = vix[vix["VIX_Rango"] == "15-20"]

# Extraer los valores del VIX en 5 días
vix_5d = vix_filtered["VIX_5d_futuro"].dropna()

# Graficar la distribución
plt.figure(figsize=(10, 6))
sns.histplot(vix_5d, bins=30, kde=True, color="royalblue")

# Personalización del gráfico
plt.title("Distribución del VIX en 5 días (cuando VIX actual está entre 15 y 20)", fontsize=14)
plt.xlabel("Nivel del VIX en 5 días", fontsize=12)
plt.ylabel("Frecuencia", fontsize=12)
plt.grid(True)

# Mostrar gráfico
plt.show()