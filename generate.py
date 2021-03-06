import time
import json
import sys

def actual_time(leg,typ):
    s = leg[typ]["scheduled"]
    if "actual" in leg[typ]:
        s = leg[typ]["actual"]
    return time.strptime(s, "%H:%M")

def delay_pstr(sched, act):
    schedtime = time.strptime(sched, "%H:%M")
    acttime = time.strptime(act, "%H:%M")
    return abs(time.mktime(schedtime) - time.mktime(acttime))

def delay_time(leg,typ):
    sched = leg[typ]["scheduled"]
    if "actual" in leg[typ]:
        actual = leg[typ]["actual"]
        schedtime = time.strptime(sched, "%H:%M")
        acttime = time.strptime(actual, "%H:%M")
        return abs(time.mktime(schedtime)-time.mktime(acttime))
    else:
        return 0

def change_time(old,new):
    arr = actual_time(old,"arrival")
    dep = actual_time(new,"departure")
    return abs(time.mktime(dep)-time.mktime(arr))


def render_intermediate(stop,offset):
    body = "\\draw[red, line width=1.5pt, fill=white] (0,%f) circle (2pt);\n" % (offset)

    if "departure" in stop:
        # split time
        body += "\\node[left] at (1.9,%f) {\\footnotesize\\textsf{%s}};" % (offset+0.17, stop["arrival"]["scheduled"])
        body += "\\node[left] at (1.9,%f) {\\footnotesize\\textsf{%s}};" % (offset-0.17, stop["departure"]["scheduled"])
        if "actual" in stop["arrival"]:
            color = "red"
            if delay_pstr(stop["arrival"]["scheduled"], stop["arrival"]["actual"]) <= 300:
                color = "green!70!black"

            body += "\\node[right] at (2,%f) {\\color{%s}\\footnotesize\\textsf{%s}};" % (
            offset+0.17, color, stop["arrival"]["actual"])

        if "actual" in stop["departure"]:
            color = "red"
            if delay_pstr(stop["departure"]["scheduled"], stop["departure"]["actual"]) <= 300:
                color = "green!70!black"

            body += "\\node[right] at (2,%f) {\\color{%s}\\footnotesize\\textsf{%s}};" % (
            offset-0.17, color, stop["departure"]["actual"])

    else:
        # single time
        body += "\\node[left] at (1.9,%f) {\\footnotesize\\textsf{%s}};"%(offset,stop["arrival"]["scheduled"])
        if "actual" in stop["arrival"]:
            color = "red"
            if delay_pstr(stop["arrival"]["scheduled"],stop["arrival"]["actual"]) <= 300:
                color = "green!70!black"

            body += "\\node[right] at (2,%f) {\\color{%s}\\footnotesize\\textsf{%s}};"%(offset,color,stop["arrival"]["actual"])

    body += "\\node[right] at (3,%f) {\\footnotesize\\textsf{%s}};"%(offset, stop["name"])


    return (body, offset-1)

def render_leg(leg, offset, now=None):
    body = "\n%% leg from %s to %s at offset %f \n"%(leg["departure"]["station"],leg["arrival"]["station"],offset)
    body += "\\fill[red] (0,%f) circle (3pt);\n"%(offset)
    body += "\\node[left] at (1.9,%f) {\\textsf{\\textbf{%s}}};\n"%(offset-0,leg["departure"]["scheduled"])
    body += "\\node[right] at (2,%f) {\\textsf{\\textbf{%s}}};\n"%(offset-0, leg["departure"]["station"])

    if "actual" in leg["departure"]:
        color = "red"
        if delay_time(leg,"departure") <= 300:
            color = "green!70!black"
        body += "\\node[left] at (1.9,%f) {\color{%s}\\footnotesize\\textsf{\\textbf{%s}}};\n"%(offset-0.4,color,leg["departure"]["actual"],)
    body += "\\node[right] at (2,%f) {\\textsf{%s $\\rightarrow$ %s}};\n"%(offset-0.8, leg["train"]["name"], leg["train"]["destination"])
    #show intermediate stations if exist


    offset -= 1.5
    if "stations" in leg["train"]:

        body += "\\draw[red, line width=2pt] (0,%f) -- +(0,%f);\n" % (offset+1.5,-len(leg["train"]["stations"])-1.5)

        for station in leg["train"]["stations"]:
            stopbody, offset = render_intermediate(station,offset)
            body += stopbody
    else:
        body += "\\draw[red, line width=2pt] (0,%f) -- +(0,%f);\n" % (offset+1.5, -1.5)

    body += "\\fill[red] (0,%f) circle (3pt);\n" % (offset)
    body += "\\node[left] at (1.9,%f) {\\textsf{\\textbf{%s}}};\n" % (offset, leg["arrival"]["scheduled"])
    if "actual" in leg["arrival"]:
        color = "red"
        if delay_time(leg,"arrival") <= 300:
            color = "green!70!black"
        body += "\\node[left] at (1.9,%f) {\color{%s}\\footnotesize\\textsf{\\textbf{%s}}};\n"%(offset-0.4,color,leg["arrival"]["actual"],)
    body += "\\node[right] at (2,%f) {\\textsf{\\textbf{%s}}};\n" % (offset, leg["arrival"]["station"])

    return (body, offset)

def render_change(old, new, offset, now=None):
    offset -=0.3
    body ="\n% change from to\n"
    body += "\\draw[red, line width=2pt, dotted] (0,%f) -- +(0,-1.8);\n" % (offset + 0.3)

    body += "\\node[right] at (2,%f) {\\textsf{\\color{gray}%d Min. Umstiegszeit}};\n"%(offset-0.8,change_time(old,new)//60)

    body += "\\fill[gray] (1,%f) circle (2pt);\n"%(offset-0.8)
    body += "\\fill[gray] (1.5,%f) circle (2pt);\n"%(offset-0.8)
    body += "\\draw[gray, -latex] (1,%f) .. controls (1.2,%f) .. (1.4,%f);\n"%(offset-0.8,offset-0.6,offset-0.7)
    # print("returned in change:",offset-1.5)
    return (body, offset-1.5)

def render_path(legs, now=None):
    offset = 0
    body = ""
    for legno in range(len(legs)):
        cur_leg = legs[legno]
        if "station" not in cur_leg["departure"]:
            cur_leg["departure"]["station"] = legs[legno - 1]["arrival"]["station"]

        if legno > 0:
            # print change
            changebody, offset = render_change(legs[legno-1],cur_leg, offset=offset, now=now)
            body += changebody
            # print("offset",offset)
        # duplicate station
        # print("before call:",offset)
        legbody, offset = render_leg(cur_leg, offset=offset, now=now)
        body += legbody

    return body

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        trip = json.load(f)
        print(render_path(trip["legs"], now=trip["now"]))