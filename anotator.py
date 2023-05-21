import cv2
import numpy as np 
import os
from csv import writer
import keyboard
import time
import json
import pyautogui

HEIGHT = 800
WIDTH = 1200

SIZE = 128

x = 100
y = 100

REGION_CENTER_X = HEIGHT//2
REGION_CENTER_Y = HEIGHT//2
REGION_RADIUS = 330

finish = 0
selected_img = None
data = {}
prior_data = None
config = None
colors = {"cloud": (120, 255, 0), "thinCloud":(0,255,255), "sky": (23, 32, 255), "sun": (0,150,200)}

canvas = np.zeros((HEIGHT, WIDTH, 3)).astype(np.uint8)
sizes = [256, 128, 32, 16, 8, 4, 2]
orig = None
cropped =  None
key =None

precise_mode = False
p_x = 0
p_y = 0
p_x_off = 0
p_y_off = 0

def draw_circle(event,x_,y_,flags,param):
    global x, y
    
    # print(x_)
    if(event == cv2.EVENT_MOUSEMOVE): 
        if precise_mode:
            p_x_off = x_ - p_x
            p_y_off = y_ - p_y

            x = p_x + p_x_off*0.3
            y = p_y + p_y_off*0.3
        else:
            x = x_
            y = y_

def isInRegion(x, y):
    return REGION_RADIUS**2 > ((x-REGION_CENTER_X)**2 + (y-REGION_CENTER_Y)**2)

def tfy(val):
    global orig
    return int((val/HEIGHT)*orig.shape[0])

def tfx(val):
    global orig
    return int((val/HEIGHT)*orig.shape[1])

def print_text(img, text, x, y, font_size, color):
    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left = (x, y)
    font_scale = font_size / 100
    thickness = 1
    cv2.putText(img, text, bottom_left, font, font_scale, color, thickness, cv2.LINE_AA)

def crop():
    global orig
    if isInRegion(x,y):
        cropped = orig[tfy(y) - SIZE//2: tfy(y) + SIZE//2, tfx(x) - SIZE//2: tfx(x) + SIZE//2, :]
        cropped = cv2.resize(cropped, ((WIDTH - HEIGHT) , (WIDTH - HEIGHT)), interpolation = cv2.INTER_AREA)
        cv2.circle(cropped, (cropped.shape[0]//2, cropped.shape[1]//2), 10, (0, 233, 222), 1)
        cv2.circle(cropped, (cropped.shape[0]//2, cropped.shape[1]//2), 9, (0, 0, 0), 1)
        c = cropped[cropped.shape[0]//2, cropped.shape[1]//2, :]
        cv2.circle(cropped, (cropped.shape[0]//2, cropped.shape[1]//2) , 60,(int(c[0]), int(c[1]), int(c[2])), 13)


        canvas[0:(WIDTH - HEIGHT), HEIGHT:WIDTH, :] = cropped


# save data
def save_data(dir):
    global prior_data

    csv_filename = dir +"/labels.csv"

    with open(csv_filename, 'a') as f_object:
        writer_object = writer(f_object)
        for image in list(data.keys()):
            
            if len(data[image]["data"]) == 0:
                continue
            
            original = cv2.imread("images/"+ image)
            image_name = image.strip('.jpg')
            
            if prior_data is not None:
                # print(image_name, data[image]["data"], prior_data[image]["data"])
                
                prior_data[image]["data"] =  prior_data[image]["data"] + data[image]["data"]

                # print(image_name, data[image]["data"], prior_data[image]["data"])
            
            for crop in data[image]["data"]:
                x0 = crop[0]
                y0 = crop[1]
                label = crop[2]
                cropped = original[tfy(y0) - SIZE//2: tfy(y0) + SIZE//2, tfx(x0) - SIZE//2: tfx(x0) + SIZE//2, :]
                
                file_name = dir +"/"+label+ "/{}_{}_{}_{}.jpg".format(image_name, tfx(x0), tfy(y0), label)
                cv2.imwrite(file_name, cropped)
                # print("   crop:",crop)
                writer_object.writerow([file_name,tfy(x0), tfy(y0), label])
    
    file = open("log.txt", 'w')
    
    if prior_data is not None:
        prior_data = json.dumps(prior_data)
    else:
        prior_data = json.dumps(data)
    file.write(prior_data)
    file.close()
        
    f_object.close()

def create_dir():
    folder_path = "./output"  # Set folder path to "./output"

    # Check if the output directory exists and create it if it doesn't
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
        print(f"Created output directory: {folder_path}")

    # Get a list of all directories in the folder
    dir_list = [d for d in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, d))]

    # Filter the list to only include directories with a format of "session_xx"
    filtered_list = [d for d in dir_list if d.startswith("session_") and d[8:].isdigit()]

    # Sort the filtered list in ascending order
    sorted_list = sorted(filtered_list)

    # If the list is not empty, find the next folder name by incrementing the session number
    if sorted_list:
        last_folder_name = sorted_list[-1]
        next_session_num = int(last_folder_name[8:]) + 1
        next_folder_name = f"session_{next_session_num:02}"
    else:
        next_folder_name = "session_01"

    new_dir_path = folder_path + "/" + next_folder_name 

    
    os.mkdir(new_dir_path)
    os.mkdir(new_dir_path+"/sky")
    os.mkdir(new_dir_path+"/cloud")
    os.mkdir(new_dir_path+"/sun")
    os.mkdir(new_dir_path+"/thinCloud")

    return new_dir_path

def make_images(x,y):
    global size, orig
    resizes = []
    target = 32
    
    prev = np.zeros((target, target*len(sizes), 3), np.uint8)

    for i,size in enumerate(sizes):
        
        re_sized = orig[y - size//2: y + size//2, x - size//2:x + size//2, :]
        if size != target:
            re_sized = cv2.resize(re_sized, (target, target), interpolation = cv2.INTER_AREA)
        resizes.append(re_sized)
        prev[:, i*target:(i+1)*target, :] = re_sized
    
    return cv2.resize(prev, (prev.shape[1]*8, prev.shape[0]*8), interpolation = cv2.INTER_AREA)

def on_press(event):
    global key
    key = event.name
    print(key)
    

keyboard.on_press(on_press)
cv2.namedWindow('image')  
cv2.setMouseCallback('image',draw_circle)  


def main():
    global orig, finish, key, prior_data, p_y, p_x, precise_mode, config

    try:
        f = open("config.txt", 'r')
        config = json.loads(f.read())
        f.close()
    except:
        print("no config file")

    try:
        f = open("log.txt", 'r')
        prior_data = json.loads(f.read())
        f.close()
    except:
        print("no log file")

    for _,_,images in os.walk("./images"):
        temp = {}
        for img in images:
            if '.jpg' in img :
                data[img] = {"metadata": {"sky":0, "cloud":0, "sun":0, "thinCloud":0}, "data":[]}
                
                if prior_data is not None:
                    if img in prior_data.keys():
                        temp[img] = prior_data[img]

    images = list(data.keys())
    img_id = 0
    while (finish == 0):
        # print(images)
        img_name = images[img_id]
        orig = cv2.imread("images/"+ img_name)
        resized = cv2.resize(orig, (HEIGHT, HEIGHT), interpolation = cv2.INTER_AREA)
        cv2.circle(resized, (REGION_CENTER_X, REGION_CENTER_Y), REGION_RADIUS, (223,123,123))
        
        
        for i in data[img_name]["data"]:
            cv2.circle(resized, (int(i[0]), int(i[1])), 1, colors[i[2]])
            orig[tfy(i[1]),tfx(i[0]),:] = colors[i[2]]
        
        if prior_data is not None:
            for i in prior_data[img_name]["data"]:
                c = tuple(ti/2 for ti in colors[i[2]])
                cv2.circle(resized, (int(i[0]),int(i[1])), 1, c)
                orig[tfy(i[1]),tfx(i[0]),:] = c
        


        while(True):
            canvas[:,:,:] = 0
            canvas[0:, 0:HEIGHT, :] = resized

            crop()

            text_y = WIDTH-HEIGHT + 30
            print_text(canvas, "SKY ("+config['SKY']+")  : "+ str(data[img_name]["metadata"]["sky"]), HEIGHT, text_y, 60, colors["sky"])
            text_y = text_y + 30
            print_text(canvas, "CLOUD ("+config['CLOUD']+"): "+ str(data[img_name]["metadata"]["cloud"]),HEIGHT, text_y, 60, colors["cloud"])
            text_y = text_y + 30
            print_text(canvas, "THIN_CLOUD ("+config['THIN_CLOUD']+") : "+ str(data[img_name]["metadata"]["thinCloud"]), HEIGHT, text_y , 60, colors["thinCloud"])
            text_y = text_y + 30
            print_text(canvas, "SUN ("+config['SUN']+")  : "+ str(data[img_name]["metadata"]["sun"]), HEIGHT, text_y , 60, colors["sun"])
            text_y = text_y + 40
            print_text(canvas, "Image : "+img_name, HEIGHT, text_y , 60, (255,100,12))
            
            try:
                img = make_images(tfx(x),tfy(y))
                # print(img.shape)
                # cv2.imshow("prev", img)
            except:
                pass
            cv2.imshow("image", canvas)
            
            cv2.waitKey(10)

            if(key == config['CLOUD']):
                data[img_name]["data"].append([x,y,"cloud"])
                data[img_name]["metadata"]["cloud"] = data[img_name]["metadata"]["cloud"] + 1
                cv2.circle(resized, (int(x),int(y)), 2, colors["cloud"],-1)
                orig[tfy(y),tfx(x),:] =  colors["cloud"]
                print("cloud", data[img_name]["data"])
            if(key == config['THIN_CLOUD']):
                data[img_name]["data"].append([x,y,"thinCloud"])
                data[img_name]["metadata"]["thinCloud"] = data[img_name]["metadata"]["thinCloud"] + 1
                cv2.circle(resized, (int(x),int(y)), 2, colors["thinCloud"],-1)
                orig[tfy(y),tfx(x),:] =  colors["thinCloud"]
            if(key == config['SKY']):
                data[img_name]["data"].append([x,y,"sky"])
                data[img_name]["metadata"]["sky"] = data[img_name]["metadata"]["sky"] + 1
                cv2.circle(resized, (int(x),int(y)), 2, colors["sky"],-1)
                orig[tfy(y),tfx(x),:] =  colors["sky"]
            if(key == config['SUN']):
                data[img_name]["data"].append([x,y,"sun"])
                data[img_name]["metadata"]["sun"] = data[img_name]["metadata"]["sun"] + 1
                cv2.circle(resized, (int(x),int(y)), 2, colors["sun"],-1)
                orig[tfy(y),tfx(x),:] =  colors["sun"]

            if(key == 'space'):
                if not precise_mode:
                    p_x = x
                    p_y = y
                    precise_mode = True
                else:
                    precise_mode = False
                    (x1, y1, windowWidth, windowHeight) = cv2.getWindowImageRect("image")
                    
                    pyautogui.moveTo(x1+x, y1+y) 

            if(key == config['ENTER']):
                finish = 1
                print("done")
                break
            

            if(key == config['ESC']):
                finish = 2
                break

            if(key ==config['BACKS']):
                if len(data[img_name]["data"]) != 0:
                    temp = data[img_name]["data"].pop(-1)
                    data[img_name]["metadata"][temp[2]] = data[img_name]["metadata"][temp[2]] - 1
                    cv2.circle(resized, (int(temp[0]),int(temp[1])), 2, (0,0,0), -1)
                    # print(data)

            if(key == config['LEFT']):
                img_id = max(0, img_id - 1)
                key = None
                break
            
            if(key == config['RIGHT']):
                img_id = min(len(images)-1, img_id +1)
                # print(img_id)
                key = None
                break
            
            key = None
            
    if (finish == 1):
        new_dir = create_dir()
        save_data(new_dir)

    cv2.destroyAllWindows()  

main()