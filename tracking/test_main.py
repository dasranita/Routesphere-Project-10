from main import Point,Route,route,distance

def test_distance():
    p=Point(lat=0,lon=0);assert distance(p,p)==0

def test_route():
    p=Point(lat=0,lon=0);assert route(Route(origin=p,stops=[Point(lat=0,lon=2),Point(lat=0,lon=1)]))['order']==[1,0]
