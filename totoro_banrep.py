import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

# COLCAP

url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_COLCAP_MONTHLY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = []

for obs in root.findall(".//g:Obs", ns):
    fecha = obs.find("g:ObsDimension", ns).attrib["value"]
    valor = obs.find("g:ObsValue", ns).attrib["value"]

    data.append((fecha, float(valor)))

colcap_df = pd.DataFrame(data, columns=["Fecha", "COLCAP"])
colcap_df["Fecha"] = pd.to_datetime(colcap_df["Fecha"])


# DTF

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_DTF_DAILY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = [
    (
        obs.find("g:ObsDimension", ns).attrib["value"],
        float(obs.find("g:ObsValue", ns).attrib["value"])
    )
    for obs in root.findall(".//g:Obs", ns)
]

dtf_df = pd.DataFrame(data, columns=["Fecha", "DTF"])

dtf_df["Fecha"] = pd.to_datetime(dtf_df["Fecha"], format="%Y%m%d")

# TRM

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_TRM_DAILY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = [
    (
        obs.find("g:ObsDimension", ns).attrib["value"],
        float(obs.find("g:ObsValue", ns).attrib["value"])
    )
    for obs in root.findall(".//g:Obs", ns)
]

trm_df = pd.DataFrame(data, columns=["Fecha", "TRM"])

trm_df["Fecha"] = pd.to_datetime(trm_df["Fecha"], format="%Y%m%d")

# TPM

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_CBR_DAILY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = [
    (
        obs.find("g:ObsDimension", ns).attrib["value"],
        float(obs.find("g:ObsValue", ns).attrib["value"])
    )
    for obs in root.findall(".//g:Obs", ns)
]

tpm_df = pd.DataFrame(data, columns=["Fecha", "TPM"])

tpm_df["Fecha"] = pd.to_datetime(tpm_df["Fecha"], format="%Y%m%d")

# TIB

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

anio_inicio = datetime.now().year - 5

url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_IR_DAILY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
response.raise_for_status()

root = ET.fromstring(response.content)

ns = {
    "g": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = [
    (
        obs.find("g:ObsDimension", ns).attrib["value"],
        float(obs.find("g:ObsValue", ns).attrib["value"])
    )
    for obs in root.findall(".//g:Obs", ns)
]

tib_df = pd.DataFrame(data, columns=["Fecha", "TIB"])

tib_df["Fecha"] = pd.to_datetime(tib_df["Fecha"], format="%Y%m%d")

# Agregados Monetarios

import requests
import pandas as pd
import xml.etree.ElementTree as ET

from datetime import datetime
year = datetime.today().year - 5

url = f"https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/ESTAT,DF_MONAGG_MONTHLY_HIST,1.0/all/ALL/?startPeriod={year}&dimensionAtObservation=TIME_PERIOD&detail=full"

# Request
response = requests.get(url)
root = ET.fromstring(response.content)

ns = {
    "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

data = []

# Loop por cada serie
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

ams_df = pd.DataFrame(data)

ams_df = ams_df.drop(columns=['REFERENCE_AREA','EXPENDITURE','ACTIVITY','UNIT_MEASURE','FREQ'])


# IBR

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime

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


# UVR

import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime


anio_inicio = datetime.now().year - 5


url = (
    "https://totoro.banrep.gov.co/nsi-jax-ws/rest/data/"
    "ESTAT,DF_UVR_DAILY_HIST,1.0/all/ALL/"
    f"?startPeriod={anio_inicio}&dimensionAtObservation=TIME_PERIOD&detail=full"
)

response = requests.get(url)
root = ET.fromstring(response.content)


ns = {
    "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic"
}

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

uvr_df = pd.DataFrame(data)

uvr_df = uvr_df.drop(columns=['REFERENCE_AREA','EXPENDITURE', 'SUBJECT', 'ACTIVITY', 'ADJUSTMENT','FREQ'])

uvr_df["Fecha"] = pd.to_datetime(uvr_df["Fecha"], format="%Y%m%d")

# IPC proxy

ipc_df = uvr_df[uvr_df['UNIT_MEASURE'] == 'APC']
ipc_df['Fecha'] = ipc_df['Fecha']-pd.DateOffset(months=2)
ipc_df = ipc_df[ipc_df["Fecha"].dt.day == 15]
ipc_df["Fecha"] = ipc_df["Fecha"] + pd.offsets.MonthEnd(0)
ipc_df = ipc_df.rename(columns={"Valor": "IPC"})
ipc_df = ipc_df.drop(columns=['UNIT_MEASURE'])