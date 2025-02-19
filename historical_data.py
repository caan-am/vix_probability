import pandas as pd

historical_data = pd.read_excel("input/vix_and_spx.xlsx")

vix = historical_data[["Date","^VIX"]]
spx = historical_data[["Date","^GSPC"]]


# Definir los rangos y etiquetas
bins = [0, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, float('inf')]
labels = ["0-10", "10-15", "15-20", "20-25", "25-30", "30-35", "35-40", "40-45", 
          "45-50", "50-55", "55-60", "60-65", "65-70", "70-75", "75-80", "80+"]

# Crear la nueva columna con los rangos
vix["VIX_Rango"] = pd.cut(vix["^VIX"], bins=bins, labels=labels, right=False)

# Crear columnas para los valores de VIX en los siguientes días (1 a 30)
for i in range(1, 31):
    vix[f"VIX_{i}d_futuro"] = vix["^VIX"].shift(-i)
vix.to_csv("vix.csv")