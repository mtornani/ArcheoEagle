"""Prossimita' sismica delle candidate: conteggi USGS ComCat M>=5 (1960-2025) entro 150/300 km.
Scrive seismic.json nella cartella corrente. Nessuna key."""
import json, urllib.request, urllib.parse, time
C=[("Helike (Golfo di Corinto)",38.22,22.13),("Atalante (Golfo Euboico)",38.67,23.10),("Thera / Santorini",36.40,25.40),
("Doñana / Tartesso",37.00,-6.40),("Banco Spartel",35.92,-5.97),("Sorgente 1755 (Horseshoe)",36.0,-10.5),
("Richat",21.12,-11.40),("Foce Tamanrasset (Timiris)",19.4,-17.5),("Mega-Chad (Bama)",11.5,13.7),
("Doggerland",54.5,2.5),("Azzorre",38.5,-28.0),("Piattaforma Mar Nero NW",45.0,31.0)]
B="https://earthquake.usgs.gov/fdsnws/event/1/"
out=[]
for n,la,lo in C:
    row={"name":n,"lat":la,"lon":lo}
    for R in (150,300):
        q=dict(format="geojson",starttime="1960-01-01",endtime="2026-01-01",minmagnitude=5,latitude=la,longitude=lo,maxradiuskm=R)
        row[f"n_M5_{R}"]=json.load(urllib.request.urlopen(B+"count?"+urllib.parse.urlencode(q),timeout=60))["count"]
    q=dict(format="geojson",starttime="1900-01-01",endtime="2026-01-01",minmagnitude=4,latitude=la,longitude=lo,maxradiuskm=300,orderby="magnitude",limit=1)
    f=json.load(urllib.request.urlopen(B+"query?"+urllib.parse.urlencode(q),timeout=60))["features"]
    row["max_M_300_since1900"]=f[0]["properties"]["mag"] if f else None
    row["max_place"]=f[0]["properties"]["place"] if f else None
    row["max_year"]=time.gmtime(f[0]["properties"]["time"]/1000).tm_year if f else None
    out.append(row); print(row)
json.dump(out,open("seismic.json","w"),indent=1)
