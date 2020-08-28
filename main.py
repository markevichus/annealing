#!/usr/bin/python3

from random import randrange, random
from copy import deepcopy
from math import exp
import svgwrite

W = 3120
H = 6000

rectangles_include = []

def random_color():
    r = randrange(0, 200)
    g = randrange(0, 200)
    b = randrange(0, 200)
    return 'rgb(' + str(r) + ',' + str(g) + ',' + str(b) + ')'

def generate_init_state(size, min_dim, max_dim):
    state = []
    for i in range(size):
        width = min_dim
        height = max_dim

        #while (width > height && width/height > 2) || (height > width && height/width > 2):
        width = randrange(min_dim, max_dim)
        height = randrange(min_dim, max_dim)
        rectangle = {'id':i, 'width':width, 'height':height, 'area':width*height}
        state.append(rectangle)

    return state

def decrete_temperature(current_temp, i):
    return current_temp * (1-1/(i+20))

def is_transit(dE, temp):
    probability = exp(-dE/temp)

    if(random() <= probability):
        return True
    else:
        return False

def generate_state_candidate(state, idx_must_shift):
    state_candidate = deepcopy(state)
    state_candidate_size = len(state_candidate)

    if idx_must_shift < 2:
        idx_must_shift = 2

    while True:
        i = randrange(0, idx_must_shift - 1)
        j = randrange(0, len(state_candidate) - 1)
        if i != j:
            tmp_el = state_candidate[i]
            state_candidate[i] = state_candidate[j]
            state_candidate[j] = tmp_el
            break

    if random() > 0.5:
        rotate_idx = randrange(0, len(state_candidate) - 1) 
        width = state_candidate[rotate_idx]['width']
        state_candidate[rotate_idx]['width'] = state_candidate[rotate_idx]['height']
        state_candidate[rotate_idx]['height'] = width

    return state_candidate

# Draw SVG
def draw_state(rectangles=[], energy_hist=[], temp_hist=[]):
    divider = 10

    dwg = svgwrite.Drawing('test.svg', profile='tiny')
    dwg.add(dwg.rect((0,0), (W/divider,H/divider),
        fill="none",
        stroke="red",
        stroke_width="2"))

    for rectangle in rectangles:
        svg_x = round(rectangle['x']/divider)
        svg_y =  round(rectangle['y']/divider)
        svg_width = round(rectangle['width']/divider)
        svg_height = round(rectangle['height']/divider)
        dwg.add(dwg.rect((svg_x, svg_y), (svg_width, svg_height),
            fill=random_color(),
            stroke="black",
            stroke_width="2"))
        dwg.add(dwg.text(rectangle['id'], insert=(svg_x + svg_width - 14, svg_y + 14), font_size='15px'))


    dwg.add(dwg.text(min(energy_hist), insert=((W/divider) + 5, 20), font_size='20px'))

    graph_x_mul = 0.5
    graph_y_mul = 400
    graph_x = round(W/divider)
    graph_y = round(H/divider)
    line_start = (graph_x, graph_y - energy_hist[0]*graph_y_mul)

    for energy in energy_hist:
        line_end = (line_start[0] + graph_x_mul, graph_y - energy*graph_y_mul)
        dwg.add(dwg.line(start=line_start, end=line_end, stroke='black', stroke_width='2'))
        line_start = line_end
    dwg.add(dwg.line(start=(W/divider,H/divider), end=(W/divider + len(energy_hist)*graph_x_mul,H/divider), stroke='black', stroke_width='2'))

    graph_x = round(W/divider)
    graph_y = round(H/(divider*2))
    line_start = (graph_x, graph_y - temp_hist[0]*graph_y_mul)
    for temp in temp_hist:
        line_end = (line_start[0] + graph_x_mul, graph_y - temp*graph_y_mul)
        dwg.add(dwg.line(start=line_start, end=line_end, stroke='black', stroke_width='2'))
        line_start = line_end
    dwg.add(dwg.line(start=(W/divider, H/(divider*2)), end=(W/divider + len(temp_hist)*graph_x_mul, H/(divider*2)), stroke='black', stroke_width='2'))

    dwg.save()

def calculate_energy(rectangles, max_area):
    sum_area = 0
    for rectangle in rectangles:
        # sum_area += rectangle['area']
        sum_area += rectangle['width']*rectangle['height']

    return round(1 - sum_area/max_area, 3)

# Move rectangle up and left
def place_rectangle(rectangle_to_place, rectangles_included):
    rectangles_sorted_y = sorted(rectangles_included,  key=lambda i: i['y'] + i['height'], reverse=True)
    rectangles_sorted_x = sorted(rectangles_included,  key=lambda i: i['x'] + i['width'], reverse=True)

    for rectangle_included in rectangles_sorted_y:
        if rectangle_included['y'] + rectangle_included['height'] > rectangle_to_place['y']:
            continue
        
        # Find X-crossing
        if ((rectangle_included['x'] + rectangle_included['width'] <= rectangle_to_place['x'] and rectangle_included['x'] + rectangle_included['width'] > rectangle_to_place['x'])
            or
            (rectangle_included['x'] + rectangle_included['width'] > rectangle_to_place['x'] and rectangle_included['x'] < rectangle_to_place['x'] + rectangle_to_place['width'])):
            # If we're standstill on it already
            if rectangle_to_place['y'] == rectangle_included['y'] + rectangle_included['height'] :
                if rectangle_to_place['y'] + rectangle_to_place['height'] <= H:
                    return rectangle_to_place
                else:
                    return False
            else:
                rectangle_to_place['y'] = rectangle_included['y'] + rectangle_included['height']

            break

    for rectangle_included in rectangles_sorted_x:
        if rectangle_included['x'] + rectangle_included['width'] > rectangle_to_place['x']:
            continue

        # Find Y-crossing
        if ((rectangle_included['y'] + rectangle_included['height'] <= rectangle_to_place['y'] and rectangle_included['y'] + rectangle_included['height'] > rectangle_to_place['y'])
            or
            (rectangle_included['y'] + rectangle_included['height'] > rectangle_to_place['y'] and rectangle_included['y'] < rectangle_to_place['y'] + rectangle_to_place['height'])):
            if rectangle_to_place['x'] == rectangle_included['x'] + rectangle_included['width']:
                if rectangle_to_place['y'] + rectangle_to_place['height'] <= H:
                    return rectangle_to_place
                else:
                    return False
            else:
                rectangle_to_place['x'] = rectangle_included['x'] + rectangle_included['width']

            break

    return place_rectangle(rectangle_to_place, rectangles_included)


def compile_state(state):
    rectangles_included = [{'id': None, 'y': 0, 'x': 0, 'width': 0, 'height': H, 'area': 0},{'id': None, 'y': 0, 'x': 0, 'width': W, 'height': 0, 'area': 0}]

    for rectangle_to_place in state:
        rectangle_to_place['x'] = W - rectangle_to_place['width']
        rectangle_to_place['y'] = H

        placed_rectangle = place_rectangle(rectangle_to_place, rectangles_included)
        if placed_rectangle:
            rectangles_included.append(placed_rectangle)

    return rectangles_included


# init_state = generate_init_state(23, 400, 2000)
# print(init_state)
# exit()
init_state = [{'id': 0, 'width': 408, 'height': 1139, 'area': 464712},{'id': 1, 'width': 1474, 'height': 1082, 'area': 1594868}, {'id': 2, 'width': 1509, 'height': 1369, 'area': 2065821}, {'id': 3, 'width': 556, 'height': 1984, 'area': 1103104}, {'id': 4, 'width': 1691, 'height': 564, 'area': 953724}, {'id': 5, 'width': 1979, 'height': 903, 'area': 1787037}, {'id': 6, 'width': 556, 'height': 1669, 'area': 927964}, {'id': 7, 'width': 1976, 'height': 1130, 'area': 2232880}, {'id': 8, 'width': 489, 'height': 1967, 'area': 961863}, {'id': 9, 'width': 764, 'height': 1439, 'area': 1099396}, {'id': 10, 'width': 947, 'height': 1032, 'area': 977304}, {'id': 11, 'width': 1417, 'height': 1111, 'area': 1574287}, {'id': 12, 'width': 1857, 'height': 640, 'area': 1188480}, {'id': 13, 'width': 1723, 'height': 780, 'area': 1343940}, {'id': 14, 'width': 1705, 'height': 1836, 'area': 3130380}, {'id': 15, 'width': 1254, 'height': 1262, 'area': 1582548}, {'id': 16, 'width': 1881, 'height': 836, 'area': 1572516}, {'id': 17, 'width': 1678, 'height': 521, 'area': 874238}, {'id': 18, 'width': 1039, 'height': 626, 'area': 650414}, {'id': 19, 'width': 1332, 'height': 539, 'area': 717948}, {'id': 20, 'width': 714, 'height': 1223, 'area': 873222}, {'id': 21, 'width': 1623, 'height': 1741, 'area': 2825643}, {'id': 22, 'width': 1868, 'height': 706, 'area': 1318808}]
init_state = [{'id':0,'width':498,'height':1486},{'id':1,'width':498,'height':1486},{'id':2,'width':498,'height':1486},{'id':3,'width':517,'height':1302},{'id':4,'width':517,'height':1302},{'id':5,'width':517,'height':1302},{'id':6,'width':517,'height':1302},{'id':7,'width':535,'height':1237},{'id':8,'width':535,'height':1237},{'id':9,'width':488,'height':1260},{'id':10,'width':488,'height':1260},{'id':11,'width':413,'height':1198},{'id':12,'width':413,'height':1198},{'id':13,'width':413,'height':1198},{'id':14,'width':413,'height':1198},{'id':15,'width':422,'height':1362},{'id':16,'width':422,'height':1362},{'id':17,'width':372,'height':1362},{'id':18,'width':372,'height':1362},{'id':19,'width':372,'height':1362},{'id':20,'width':372,'height':1362},{'id':21,'width':413,'height':1198},{'id':22,'width':413,'height':1198},{'id':23,'width':155,'height':1237},{'id':24,'width':155,'height':1237},{'id':25,'width':155,'height':637},{'id':26,'width':155,'height':637},{'id':27,'width':498,'height':650},{'id':28,'width':498,'height':650},{'id':29,'width':498,'height':650},{'id':30,'width':498,'height':650},{'id':31,'width':498,'height':650},{'id':32,'width':498,'height':650},{'id':33,'width':498,'height':650},{'id':34,'width':498,'height':650},{'id':35,'width':498,'height':650},{'id':36,'width':498,'height':650},{'id':37,'width':498,'height':650},{'id':38,'width':498,'height':650},{'id':39,'width':498,'height':650},{'id':40,'width':498,'height':650},{'id':41,'width':498,'height':650},{'id':42,'width':498,'height':650},{'id':43,'width':498,'height':650},{'id':44,'width':498,'height':650},{'id':45,'width':498,'height':650},{'id':46,'width':498,'height':650},{'id':47,'width':498,'height':650},{'id':48,'width':629,'height':1289},{'id':49,'width':629,'height':1289},{'id':50,'width':629,'height':1289},{'id':51,'width':550,'height':1330},{'id':52,'width':550,'height':1330},{'id':53,'width':1410,'height':481},{'id':54,'width':1410,'height':481},{'id':55,'width':1410,'height':481},{'id':56,'width':1410,'height':481},{'id':57,'width':1410,'height':481},{'id':58,'width':1410,'height':481},{'id':59,'width':1410,'height':481},{'id':60,'width':1410,'height':481},{'id':61,'width':1410,'height':481},{'id':62,'width':1410,'height':481},{'id':63,'width':1410,'height':481},{'id':64,'width':1410,'height':481},{'id':65,'width':1410,'height':481},{'id':66,'width':1410,'height':481},{'id':67,'width':1410,'height':481},{'id':68,'width':1410,'height':481},{'id':69,'width':1410,'height':481},{'id':70,'width':1410,'height':481},{'id':71,'width':1410,'height':481},{'id':72,'width':1410,'height':481},{'id':73,'width':1410,'height':481},{'id':74,'width':1410,'height':481},{'id':75,'width':1410,'height':481},{'id':76,'width':1410,'height':481},{'id':77,'width':1410,'height':481},{'id':78,'width':1410,'height':481},{'id':79,'width':1410,'height':481},{'id':80,'width':1322,'height':1457},{'id':81,'width':1322,'height':1457},{'id':82,'width':1322,'height':1457},{'id':83,'width':1322,'height':1457},{'id':84,'width':1322,'height':1457},{'id':85,'width':1322,'height':1457},{'id':86,'width':1322,'height':1457},{'id':87,'width':1322,'height':1457},{'id':88,'width':1322,'height':1457},{'id':89,'width':1322,'height':1457},{'id':90,'width':1322,'height':1457},{'id':91,'width':1322,'height':1457},{'id':92,'width':1322,'height':1457},{'id':93,'width':1322,'height':1457},{'id':94,'width':1322,'height':1457},{'id':95,'width':1322,'height':1457},{'id':96,'width':1322,'height':1457},{'id':97,'width':1322,'height':1457},{'id':98,'width':1322,'height':1457},{'id':99,'width':1322,'height':1457},{'id':100,'width':1322,'height':1457},{'id':101,'width':782,'height':1457},{'id':102,'width':782,'height':1457},{'id':103,'width':782,'height':1457},{'id':104,'width':782,'height':1457},{'id':105,'width':782,'height':1457},{'id':106,'width':782,'height':1457},{'id':107,'width':1340,'height':1360},{'id':108,'width':1340,'height':1360},{'id':109,'width':1250,'height':1360},{'id':110,'width':1250,'height':1360},{'id':111,'width':1360,'height':431},{'id':112,'width':1360,'height':431},{'id':113,'width':1360,'height':431},{'id':114,'width':902,'height':1457},{'id':115,'width':902,'height':1457},{'id':116,'width':902,'height':1457},{'id':117,'width':902,'height':1457},{'id':118,'width':902,'height':1457},{'id':119,'width':902,'height':1457},{'id':120,'width':902,'height':1457},{'id':121,'width':902,'height':1457},{'id':122,'width':902,'height':1457},{'id':123,'width':902,'height':1457},{'id':124,'width':902,'height':1457},{'id':125,'width':902,'height':1457},{'id':126,'width':902,'height':1457},{'id':127,'width':902,'height':1457},{'id':128,'width':902,'height':1457},{'id':129,'width':902,'height':1457},{'id':130,'width':902,'height':1457},{'id':131,'width':902,'height':1457},{'id':132,'width':902,'height':1457},{'id':133,'width':902,'height':1457},{'id':134,'width':902,'height':1457},{'id':135,'width':902,'height':1457},{'id':136,'width':902,'height':1457},{'id':137,'width':902,'height':1457},{'id':138,'width':902,'height':1457},{'id':139,'width':902,'height':1457},{'id':140,'width':902,'height':1457},{'id':141,'width':538,'height':1405},{'id':142,'width':538,'height':1405},{'id':143,'width':538,'height':1405},{'id':144,'width':538,'height':1405},{'id':145,'width':538,'height':1405},{'id':146,'width':538,'height':1405},{'id':147,'width':538,'height':1405},{'id':148,'width':538,'height':1405},{'id':149,'width':538,'height':1405},{'id':150,'width':538,'height':1405},{'id':151,'width':538,'height':1405},{'id':152,'width':538,'height':1405},{'id':153,'width':538,'height':1405},{'id':154,'width':538,'height':1405},{'id':155,'width':538,'height':1405},{'id':156,'width':538,'height':1405},{'id':157,'width':538,'height':1405},{'id':158,'width':538,'height':1405},{'id':159,'width':538,'height':1405},{'id':160,'width':538,'height':1405},{'id':161,'width':538,'height':1405},{'id':162,'width':538,'height':1405},{'id':163,'width':538,'height':1405},{'id':164,'width':538,'height':1405}]
#for rectangle in state:
#    print(rectangle)

# rectangles_included = compile_state(init_state)
# print(calculate_energy(rectangles_included, W*H))
# draw_state(rectangles_included, [1], [1])

# for rectangle in rectangles_included:
#     print(rectangle)
# exit()

minest_energy = 1
rectangles_bestofthebest = []
energy_hist_bestofthebest = []
temp_hist_bestofthebest = []

state = deepcopy(init_state)

for run_idx in range(100):
    state = deepcopy(init_state)

    glass_area = W*H
    temp = 0.98
    min_temp = 0.001

    # state = generate_state_candidate(state, 10)
    init_rectangles = compile_state(state)
    # energy = calculate_energy(init_rectangles, glass_area)
    energy = 1
    energy_hist = []
    temp_hist = []
    candidate_rectangles = []
    min_energy = 1

    # draw_state(init_rectangles, [1], [1])
    # print(energy)
    # for rectangle in init_rectangles:
    #     print(rectangle)
    # exit()

    for i in range(10000):
        rectangles_included_len = len(candidate_rectangles) if len(candidate_rectangles) > 0 else len(init_rectangles) 

        state_candidate = generate_state_candidate(state, rectangles_included_len)
        candidate_rectangles = compile_state(state_candidate)
        candidate_energy = calculate_energy(candidate_rectangles, glass_area)
        # print('candidate_energy: ' + str(candidate_energy))

        dE = candidate_energy - energy
        if(dE < 0):
            energy = candidate_energy
            state = state_candidate
            energy_hist.append(energy)
            temp_hist.append(temp)

            if(min_energy > energy):
                min_energy = energy
                rectangles_best = deepcopy(candidate_rectangles)
        else:
            if(is_transit(dE, temp)):
                energy = candidate_energy
                state = state_candidate
                energy_hist.append(energy)
                temp_hist.append(temp)

        temp = decrete_temperature(temp, i)
        if temp < min_temp:
            break

    print("Batch min energy: " + str(min_energy))
    if(minest_energy > min_energy):
        minest_energy = min_energy
        rectangles_bestofthebest = deepcopy(rectangles_best)
        energy_hist_bestofthebest = deepcopy(energy_hist)
        temp_hist_bestofthebest = deepcopy(temp_hist)
        
        print("Minest! " + str(minest_energy))
        draw_state(rectangles_bestofthebest, energy_hist_bestofthebest, temp_hist_bestofthebest)

print("=== Minest: " + str(minest_energy))
for rectangle in rectangles_bestofthebest:
    print(rectangle)
