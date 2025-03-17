import pandas as pd

historical_data = pd.read_excel("input/vix_and_spx.xlsx")

vix = historical_data[["Date","^VIX"]]
spx = historical_data[["Date","^GSPC"]]

# Definir los nuevos rangos y etiquetas
bins = [0, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, float('inf')]
labels = [
    "0-10", "10-11", "11-12", "12-13", "13-14", "14-15", "15-16", "16-17", "17-18", "18-19", "19-20", 
    "20-21", "21-22", "22-23", "23-24", "24-25", "25-26", "26-27", "27-28", "28-29", "29-30", "30-35", 
    "35-40", "40-45", "45-50", "50-55", "55-60", "60-65", "65-70", "70-75", "75-80", "80+"
]

# Crear la nueva columna con los rangos
vix["VIX_Rango"] = pd.cut(vix["^VIX"], bins=bins, labels=labels, right=False)

# Crear columnas para los valores de VIX en los siguientes días (1 a 30)
for i in range(1, 31):
    vix[f"VIX_{i}d_futuro"] = vix["^VIX"].shift(-i)

# Calcular el cambio porcentual del VIX
vix['VIX_cambio_1d'] = (vix['^VIX'] - vix['^VIX'].shift(1)) / vix['^VIX'].shift(1) * 100
vix['VIX_cambio_5d'] = (vix['^VIX'] - vix['^VIX'].shift(5)) / vix['^VIX'].shift(5) * 100
vix['VIX_cambio_2sem'] = (vix['^VIX'] - vix['^VIX'].shift(10)) / vix['^VIX'].shift(10) * 100
vix['VIX_cambio_1mes'] = (vix['^VIX'] - vix['^VIX'].shift(21)) / vix['^VIX'].shift(21) * 100

vix.to_csv("vix.csv")