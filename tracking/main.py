import os, math
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, AwareDatetime
import psycopg
from psycopg.rows import dict_row
app=FastAPI(title='RouteSphere tracking')
class Point(BaseModel):
    lat: float=Field(ge=-90,le=90)
    lon: float=Field(ge=-180,le=180)
class Event(Point):
    event_id:str=Field(min_length=1,max_length=100)
    vehicle_id:int=Field(gt=0)
    recorded_at:AwareDatetime
class Route(BaseModel):
    origin:Point
    stops:list[Point]=Field(max_length=100)
    speed:float=Field(default=40,gt=0,le=150)
def distance(a,b):
    p,q=map(math.radians,[a.lat,b.lat]); d=math.radians(b.lon-a.lon)
    h=math.sin((q-p)/2)**2+math.cos(p)*math.cos(q)*math.sin(d/2)**2
    return 6371*2*math.asin(math.sqrt(min(1,max(0,h))))
@app.post('/route')
def route(body:Route):
    remaining=list(enumerate(body.stops)); current=body.origin; order=[]; total=0
    while remaining:
        i,p=min(remaining,key=lambda x:distance(current,x[1]));total+=distance(current,p);order.append(i);remaining.remove((i,p));current=p
    return {'order':order,'distance_km':round(total,2),'eta_minutes':round(total/body.speed*60,2)}
@app.post('/gps')
def gps(e:Event):
    if e.recorded_at>datetime.now(timezone.utc):raise HTTPException(400,'Future timestamp')
    try:
        with psycopg.connect(os.environ['DATABASE_URL']) as c:
            x=c.execute('INSERT INTO gps VALUES(%s,%s,%s,%s,%s) ON CONFLICT(event_id) DO NOTHING',(e.event_id,e.vehicle_id,e.lat,e.lon,e.recorded_at));return {'inserted':x.rowcount==1}
    except psycopg.errors.ForeignKeyViolation:raise HTTPException(404,'Unknown vehicle')
@app.get('/gps/{vehicle_id}/latest')
def latest(vehicle_id:int):
    with psycopg.connect(os.environ['DATABASE_URL'],row_factory=dict_row) as c:
        return c.execute('SELECT * FROM gps WHERE vehicle_id=%s ORDER BY recorded_at DESC,event_id DESC LIMIT 1',(vehicle_id,)).fetchone()
