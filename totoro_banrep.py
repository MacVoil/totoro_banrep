# Script para extraer datos económicos del API de Totoro del Banco de la República
# Este script obtiene datos históricos de indicadores como COLCAP, DTF, TRM, etc., de los últimos 5 años.

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# Año de inicio para los datos históricos (5 años atrás)
anio_inicio = datetime.now().year - 5

def fetch_simple_data(dataset_code, date_format, column_name):
    """
    Función para obtener datos simples de series temporales del API de Totoro.
    Parámetros:
    - dataset_code: Código del conjunto de datos (ej. 'DF_COLCAP_MONTHLY_HIST')
    - date_format: Formato de fecha para pd.to_datetime (None si no se especifica)
    - column_name: Nombre de la columna para el valor (ej. 'COLCAP')
    Retorna: DataFrame con columnas 'Fecha' y el nombre especificado.
    """
    url = (
        f"https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
        f"ESTAT,{dataset_code},1.0/all/ALL/"
        f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
    )
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    ns = {"g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}

    data = [
        (
            obs.find("g:ObsDimension", ns).attrib["value"],
            float(obs.find("g:ObsValue", ns).attrib["value"])
        )
        for obs in root.findall(".//g:Obs", ns)
    ]

    df = pd.DataFrame(data, columns=["Fecha", column_name])
    if date_format:
        df["Fecha"] = pd.to_datetime(df["Fecha"], format=date_format)
    else:
        df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

def fetch_series_data(dataset_code, drop_columns, date_format="%Y-%m", month_end=False):
    """
    Función para obtener datos de series múltiples del API de Totoro.
    Parámetros:
    - dataset_code: Código del conjunto de datos
    - drop_columns: Lista de columnas a eliminar del DataFrame
    - date_format: Formato de fecha (por defecto "%Y-%m")
    - month_end: Si True, ajusta la fecha al fin de mes
    Retorna: DataFrame con los datos procesados.
    """
    url = (
        f"https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
        f"ESTAT,{dataset_code},1.0/all/ALL/"
        f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
    )
    response = requests.get(url)
    root = ET.fromstring(response.content)

    ns = {"generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}

    data = []
    for series in root.findall(".//generic:Series", ns):
        series_info = {}
        for val in series.findall(".//generic:SeriesKey/generic:Value", ns):
            series_info[val.attrib["id"]] = val.attrib["value"]

        for obs in series.findall(".//generic:Obs", ns):
            fecha = obs.find("generic:ObsDimension", ns).attrib["value"]
            valor = obs.find("generic:ObsValue", ns).attrib["value"]

            row = {
                "Fecha": fecha,
                "Valor": float(valor),
                **series_info
            }
            data.append(row)

    df = pd.DataFrame(data)
    if drop_columns:
        df = df.drop(columns=drop_columns)
    df["Fecha"] = pd.to_datetime(df["Fecha"], format=date_format)
    if month_end:
        df["Fecha"] = df["Fecha"] + pd.offsets.MonthEnd(0)
    return df

# Obtener datos del índice COLCAP (datos mensuales)
colcap_df = fetch_simple_data("DF_COLCAP_MONTHLY_HIST", None, "COLCAP")

# Obtener datos de la DTF (Tasa de Interés de Referencia, datos diarios)
dtf_df = fetch_simple_data("DF_DTF_DAILY_HIST", "%Y%m%d", "DTF")

# Obtener datos de la TRM (Tasa Representativa del Mercado, datos diarios)
trm_df = fetch_simple_data("DF_TRM_DAILY_HIST", "%Y%m%d", "TRM")

# Obtener datos de la TPM (Tasa Política Monetaria, datos diarios)
tpm_df = fetch_simple_data("DF_CBR_DAILY_HIST", "%Y%m%d", "TPM")

# Obtener datos de la TIB (Tasa de Interés Bancaria, datos diarios)
tib_df = fetch_simple_data("DF_IR_DAILY_HIST", "%Y%m%d", "TIB")

# Obtener datos de Agregados Monetarios (datos mensuales)
ams_df = fetch_series_data("DF_MONAGG_MONTHLY_HIST", ['REFERENCE_AREA','EXPENDITURE','ACTIVITY','UNIT_MEASURE','FREQ'], "%Y-%m", month_end=True)

def fetch_ibr_data():
    """
    Función específica para obtener datos de IBR (Índice de Referencia Bancaria).
    Incluye mapeo de plazos y filtrado por unidad de medida.
    Retorna: DataFrame con columnas 'fecha', 'plazo', 'tasa_efectiva'.
    """
    url = (
        "https://totoro.banrep.gov.co/"
        "nsi-jax-ws/rest/data/ESTAT,DF_IBR_DAILY_HIST,1.0/all/ALL/?"
        f"startPeriod={datetime.now().year - 5}"
        "&dimensionAtObservation=TIME_PERIOD&detail=full"
    )
    root = ET.fromstring(requests.get(url).content)
    ns = {"generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}

    # Mapeo de códigos de plazo a nombres legibles
    map_plazo = {
        "IRIBRM00": "IB00",
        "IRIBRM01": "IB01",
        "IRIBRM03": "IB03",
        "IRIBRM06": "IB06"
    }

    rows = []
    for s in root.findall(".//generic:Series", ns):
        subject = None
        unit = None
        for v in s.findall(".//generic:SeriesKey/generic:Value", ns):
            if v.attrib["id"] == "SUBJECT":
                subject = v.attrib["value"]
            if v.attrib["id"] == "UNIT_MEASURE":
                unit = v.attrib["value"]

        # Filtrar solo unidades en ER (tasa efectiva)
        if unit != "ER":
            continue

        plazo = map_plazo.get(subject, subject)

        for o in s.findall(".//generic:Obs", ns):
            fecha = o.find("generic:ObsDimension", ns).attrib["value"]
            valor = float(o.find("generic:ObsValue", ns).attrib["value"])

            rows.append([fecha, plazo, valor / 100])

    ibr_df = pd.DataFrame(rows, columns=["fecha", "plazo", "tasa_efectiva"])
    ibr_df["fecha"] = pd.to_datetime(ibr_df["fecha"])
    ibr_df["fecha_fin_mes"] = ibr_df["fecha"] + pd.offsets.MonthEnd(0)
    ibr_df["tasa_efectiva"] *= 100
    ibr_df = ibr_df[["fecha", "plazo", "tasa_efectiva"]]
    return ibr_df

# Obtener datos de IBR
ibr_df = fetch_ibr_data()

# Obtener datos de UVR (Unidad de Valor Real, datos diarios)
uvr_df = fetch_series_data("DF_UVR_DAILY_HIST", ['REFERENCE_AREA','EXPENDITURE', 'SUBJECT', 'ACTIVITY', 'ADJUSTMENT','FREQ'], "%Y%m%d")

# Crear proxy del IPC a partir de los datos de UVR
# Filtrar por medida APC, ajustar fechas y renombrar columnas
ipc_df = uvr_df[uvr_df['UNIT_MEASURE'] == 'APC'].copy()
ipc_df['Fecha'] = ipc_df['Fecha'] - pd.DateOffset(months=2)  # Retroceder 2 meses
ipc_df = ipc_df[ipc_df["Fecha"].dt.day == 15]  # Solo días 15
ipc_df["Fecha"] = ipc_df["Fecha"] + pd.offsets.MonthEnd(0)  # Ajustar a fin de mes
ipc_df = ipc_df.rename(columns={"Valor": "IPC"})  # Renombrar columna
ipc_df = ipc_df.drop(columns=['UNIT_MEASURE'])  # Eliminar columna innecesaria