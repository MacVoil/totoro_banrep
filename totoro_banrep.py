import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

def fetch_simple_data(dataset_code, date_format, column_name):
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
    df["Fecha"] = pd.to_datetime(df["Fecha"], format=date_format)
    return df

def fetch_series_data(dataset_code, drop_columns, date_format="%Y-%m", month_end=False):
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

# COLCAP
colcap_df = fetch_simple_data("DF_COLCAP_MONTHLY_HIST", None, "COLCAP")

# DTF
dtf_df = fetch_simple_data("DF_DTF_DAILY_HIST", "%Y%m%d", "DTF")

# TRM
trm_df = fetch_simple_data("DF_TRM_DAILY_HIST", "%Y%m%d", "TRM")

# TPM
tpm_df = fetch_simple_data("DF_CBR_DAILY_HIST", "%Y%m%d", "TPM")

# TIB
tib_df = fetch_simple_data("DF_IR_DAILY_HIST", "%Y%m%d", "TIB")

# Agregados Monetarios
ams_df = fetch_series_data("DF_MONAGG_MONTHLY_HIST", ['REFERENCE_AREA','EXPENDITURE','ACTIVITY','UNIT_MEASURE','FREQ'], "%Y-%m", month_end=True)

# IBR
def fetch_ibr_data():
    url = (
        "https://totoro.banrep.gov.co/"
        "nsi-jax-ws/rest/data/ESTAT,DF_IBR_DAILY_HIST,1.0/all/ALL/?"
        f"startPeriod={datetime.now().year - 5}"
        "&dimensionAtObservation=TIME_PERIOD&detail=full"
    )
    root = ET.fromstring(requests.get(url).content)
    ns = {"generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"}

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

ibr_df = fetch_ibr_data()

# UVR
uvr_df = fetch_series_data("DF_UVR_DAILY_HIST", ['REFERENCE_AREA','EXPENDITURE', 'SUBJECT', 'ACTIVITY', 'ADJUSTMENT','FREQ'], "%Y%m%d")

# IPC proxy
ipc_df = uvr_df[uvr_df['UNIT_MEASURE'] == 'APC'].copy()
ipc_df['Fecha'] = ipc_df['Fecha'] - pd.DateOffset(months=2)
ipc_df = ipc_df[ipc_df["Fecha"].dt.day == 15]
ipc_df["Fecha"] = ipc_df["Fecha"] + pd.offsets.MonthEnd(0)
ipc_df = ipc_df.rename(columns={"Valor": "IPC"})
ipc_df = ipc_df.drop(columns=['UNIT_MEASURE'])