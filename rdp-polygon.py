import json
import matplotlib.pyplot as plt
import numpy as np
from rdp import rdp 

html = urlopen("https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo.json")
jdata = html.read().decode('utf-8')
geoJSON = json.loads(jdata)

fig = plt.figure(figsize=(12, 12))
ax = fig.gca()
ax.set_aspect(1.25)

polygons = []
pts=[]    # decrease resolution to four decimal places
for  feature in geoJSON['features']:
    pts = []
    prev_x = 0
    prev_y = 0
    for p in feature['geometry']['coordinates'][0]:
        x = round(p[0], 4)
        y = round(p[1], 4)
        if x == prev_x and y == prev_y:
            continue
        pts.append([x, y, 0])
        prev_x = x
        prev_y = y
    polygons.append(pts)

# accumulate neighbor in three decimal plances 
cum = {} 
for pl in polygons:
    visited = {}
    for p in pl:
        dot = (round(p[0], 3), round(p[1], 3))
        if dot in visited:
            visited[dot] += 1
        else:
            visited[dot] = 1
        if dot in cum:
            if visited[dot] == 1:   #  to prevent p in same pl
                cum[dot] += 1
        else:
            cum[dot] = 1
# assign neighbor counter to 3rd 
for pl in polygons:
    for p in pl:
        p[2] = cum[(round(p[0], 3), round(p[1], 3))]

# find _joints_ where lines meet
joints = []
for  pl in polygons:
    multi = pl[0][2]
    prev =[p[0], p[1]]
    for p in pl[1:]:
        if multi < p[2]: # branch
            if not [p[0], p[1]] in joints:
                joints.append([p[0], p[1]])
        elif multi > p[2]:  # combine
            if not prev in joints:
                joints.append(prev)
        prev = [p[0], p[1]]
        multi = p[2]
x = []
y = []
for p in joints:
    x.append(round(p[0], 3))
    y.append(round(p[1], 3))
#ax.plot(x, y, 'o', color='red')

# 
for  pl in polygons:
    multi = pl[0][2]
    pts = []
    if [pl[0][0], pl[0][1]] in joints: # to merge to joints
        pts.append([round(pl[0][0], 3), round(pl[0][1], 3)])
        prev = [round(pl[0][0], 3), round(pl[0][1], 3)]
    else:
        pts.append([pl[0][0], pl[0][1]])
        prev = [pl[0][0], pl[0][1]]
    for p in pl[1:]:  # from 2nd 
        if multi != p[2]:
            if multi < p[2]:  # 1-1-2
                min_dist =  100.0
                min_idx = 0
                for idx, val in enumerate(joints):   # find nearest joints
                    dist =  abs(val[0] - prev[0]) + abs(val[1] - prev[1])
                    if min_dist > dist:
                        min_idx = idx
                        min_dist = dist
                pts.append([round(joints[min_idx][0], 3),  round(joints[min_idx][1], 3)])
            rdp_pts = rdp(pts, epsilon=0.01)
            x = [i for i, j in rdp_pts]
            y = [j for i, j in rdp_pts]
            ax.plot(x, y, color='gray')
            pts = []
            if multi > p[2]:  # 2-2-1
                pts.append(prev)
        if [p[0], p[1]] in joints: # to merge to joinsts
            pts.append([round(p[0], 3), round(p[1], 3)])
            prev = [round(p[0], 3), round(p[1], 3)]
        else:
            pts.append([p[0], p[1]])
            prev = [p[0], p[1]]
        multi = p[2]
        
    rdp_pts = rdp(pts, epsilon=0.01)
    x = [i for i, j in rdp_pts]
    y = [j for i, j in rdp_pts]
    ax.plot(x, y, color='gray')


