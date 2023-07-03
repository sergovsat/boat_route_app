# sample program that can move points (already draws 10 different lines (with user interface)), also has some additonal menu options
# draws and edits curves, saves them to json as 2 points and heading to 3rd

import cv2 as cv
import numpy as np

import sys, math, json

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp, QWidget, \
    QDesktopWidget, QLabel, QVBoxLayout, QFileDialog, QMenu, QToolBar, QComboBox, QSpinBox, \
    QLineEdit, QPushButton, QDialog

from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import Qt


#################################################### ADDITIONAL WINDOWS #####################################################


class RenameWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Rename')
        self.layout = QVBoxLayout()

        self.input_label = QLabel('Enter new title:')
        self.input_field = QLineEdit()
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.change_title)

        self.layout.addWidget(self.input_label)
        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.ok_button)

        self.setLayout(self.layout)

    def change_title(self):
        new_title = self.input_field.text()
        if new_title:
            MyApp.name_of_session = new_title
            self.close()




#######################################################################################################################
##################################################### MAIN WINDOW #####################################################

class MyApp(QMainWindow):

    height = 1500
    width = 900
    # array of all coordinates of the boats
    routes = [[(height // 2, width - 5)], [], [], [], [], [], [], [], [], []]

    velocity_array = [[], [], [], [], [], [], [], [], [], []]

    cur_velocity = 10

    boat_size_array = [[5, 3, 2] for i in range(10)]

    myboard = np.full((width, height, 3), 255, dtype='uint8')

    cur_boat_index = 0

    cur_type_of_line = 0

    name_of_session = "MySession"
    
    cnt_of_boats = 1

    nearest_index = -1

    cur_weather_index = 0

    colors_array = [
        (0, 0, 0),        # Black (Oscar)
        (255, 0, 0),      # Red
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 255),    # Cyan
        (255, 128, 0),    # Orange
        (128, 0, 255),    # Purple
        (0, 255, 128)     # Lime
    ]

    boat_names = [
        "Black (Oscar)",
        "Red",
        "Green",
        "Blue",
        "Yellow",
        "Magenta",
        "Cyan",
        "Orange",
        "Purple",
        "Lime",
    ]

    weather_array = [
        "Sunny",
        "Cloudy",
        "Rainy",
        "Storm"
    ]

    start_time_array = [0 for i in range(10)]

    

######################################################### MENU & INITISLIZATION #########################################################

    def __init__(self):
        super().__init__()
        self.initUI()
        
    
    def initUI(self):
        self.createActions() 
        self.createMenus()
        self.createToolBars()
        
        self.image_frame = QLabel()
        self.setCentralWidget(self.image_frame)
        self.draw_line()

        self.setWindowTitle(self.name_of_session)
        self.setFixedSize(self.height, self.width + 55)
        self.center()
        self.show()

    
    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        
        self.fileMenu.addAction(self.renameAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        self.menuBar().addMenu(self.fileMenu)


        self.editMenu = QMenu("&Edit", self)
        self.editMenu.addAction(self.backAct)
        self.editMenu.addAction(self.newAct)
        self.editMenu.addAction(self.clearAct)
        self.menuBar().addMenu(self.editMenu)

############################################################ TOOL BAR ############################################################ 

    def createToolBars(self):
        editToolBar = QToolBar("Edit", self)
        editToolBar.setMovable(False)
        self.addToolBar(editToolBar)
        
        editToolBar.addAction(self.clearAct)
        editToolBar.addAction(self.deleteAct)
        editToolBar.addAction(self.renameAct)
        editToolBar.addAction(self.backAct)
        editToolBar.addAction(self.newAct)
        editToolBar.addSeparator()

        # combo box of boat
        self.chooseBoatAct = QComboBox()
        self.chooseBoatAct.addItem(self.boat_names[0])
        self.chooseBoatAct.currentIndexChanged.connect(self.cur_boat_changed)
        self.chooseBoatAct.setFixedSize(120, 30)
        editToolBar.addWidget(self.chooseBoatAct)
        editToolBar.addSeparator()

        # combo box of type of line
        self.chooseTypeOfLineAct = QComboBox()
        self.chooseTypeOfLineAct.addItem(QIcon('icons/chart-line-variant.svg'), "Direct line")
        self.chooseTypeOfLineAct.addItem(QIcon('icons/vector-curve.svg'), "Bezier curve")
        self.chooseTypeOfLineAct.currentIndexChanged.connect(self.cur_type_of_line_changed)
        self.chooseTypeOfLineAct.setFixedSize(120, 30)
        editToolBar.addWidget(self.chooseTypeOfLineAct)
        editToolBar.addSeparator()

        # combo box of weather
        self.chooseWeatherAct = QComboBox()
        self.chooseWeatherAct.addItem(QIcon('icons/weather-sunny.svg'), self.weather_array[0])
        self.chooseWeatherAct.addItem(QIcon('icons/cloud-outline.svg'), self.weather_array[1])
        self.chooseWeatherAct.addItem(QIcon('icons/weather-rainy.svg'), self.weather_array[2])
        self.chooseWeatherAct.addItem(QIcon('icons/weather-lightning-rainy.svg'), self.weather_array[3])
        self.chooseWeatherAct.currentIndexChanged.connect(self.cur_weather_changed)
        self.chooseWeatherAct.setFixedSize(100, 30)
        editToolBar.addWidget(self.chooseWeatherAct)
        editToolBar.addSeparator()

        # space
        self.spacer1 = QWidget()
        self.spacer1.setSizePolicy(editToolBar.sizePolicy())
        self.spacer1.setSizePolicy(editToolBar.sizePolicy().Fixed, editToolBar.sizePolicy().Fixed)
        self.spacer1.setMinimumWidth(20)
        self.spacer1.setMaximumWidth(20)
        editToolBar.addWidget(self.spacer1)

        # label of sea state
        label1 = QLabel('Sea state: ')
        editToolBar.addWidget(label1)

        # spin box of sea state
        self.seaStateSpinBox = QSpinBox()
        self.seaStateSpinBox.setRange(1, 20)
        self.seaStateSpinBox.value = 1
        editToolBar.addWidget(self.seaStateSpinBox)
        editToolBar.addSeparator()

        # space
        self.spacer2 = QWidget()
        self.spacer2.setSizePolicy(editToolBar.sizePolicy())
        self.spacer2.setSizePolicy(editToolBar.sizePolicy().Fixed, editToolBar.sizePolicy().Fixed)
        self.spacer2.setMinimumWidth(20)
        self.spacer2.setMaximumWidth(20)
        editToolBar.addWidget(self.spacer2)

        # label of sea state
        label2 = QLabel('Start time: ')
        editToolBar.addWidget(label2)

        # spin box of start time
        self.startTimeSpinBox = QSpinBox()
        self.startTimeSpinBox.setRange(0, 60)
        self.startTimeSpinBox.value = 0
        self.startTimeSpinBox.valueChanged.connect(self.start_time_value_changed)
        editToolBar.addWidget(self.startTimeSpinBox)
        editToolBar.addSeparator()

        # space
        self.spacer3 = QWidget()
        self.spacer3.setSizePolicy(editToolBar.sizePolicy())
        self.spacer3.setSizePolicy(editToolBar.sizePolicy().Fixed, editToolBar.sizePolicy().Fixed)
        self.spacer3.setMinimumWidth(20)
        self.spacer3.setMaximumWidth(20)
        editToolBar.addWidget(self.spacer3)

        # label of velocity
        label3 = QLabel('Velocity (kn): ')
        editToolBar.addWidget(label3)

        # spin box of velocity
        self.velocitySpinBox = QSpinBox()
        self.velocitySpinBox.setRange(1, 100)
        self.velocitySpinBox.setValue(10)
        self.velocitySpinBox.valueChanged.connect(self.velocity_value_changed)
        editToolBar.addWidget(self.velocitySpinBox)
        editToolBar.addSeparator()

        # space
        self.spacer4 = QWidget()
        self.spacer4.setSizePolicy(editToolBar.sizePolicy())
        self.spacer4.setSizePolicy(editToolBar.sizePolicy().Fixed, editToolBar.sizePolicy().Fixed)
        self.spacer4.setMinimumWidth(20)
        self.spacer4.setMaximumWidth(20)
        editToolBar.addWidget(self.spacer4)

        # label of size
        label4 = QLabel('Size (L|W|H): ')
        editToolBar.addWidget(label4)

        # spin box of length
        self.lengthSpinBox = QSpinBox()
        self.lengthSpinBox.setRange(1, 400)
        self.lengthSpinBox.setValue(5)
        self.lengthSpinBox.valueChanged.connect(self.length_value_changed)
        editToolBar.addWidget(self.lengthSpinBox)
        editToolBar.addSeparator()
        # spin box of width
        self.widthSpinBox = QSpinBox()
        self.widthSpinBox.setRange(1, 100)
        self.widthSpinBox.setValue(3)
        self.widthSpinBox.valueChanged.connect(self.width_value_changed)
        editToolBar.addWidget(self.widthSpinBox)
        editToolBar.addSeparator()
        # spin box of height
        self.heightSpinBox = QSpinBox()
        self.heightSpinBox.setRange(1, 50)
        self.heightSpinBox.setValue(2)
        self.heightSpinBox.valueChanged.connect(self.height_value_changed)
        editToolBar.addWidget(self.heightSpinBox)
        editToolBar.addSeparator()


################################################## FUNCTIONS ##################################################

    def createActions(self):
        self.newAct = QAction("New", self, shortcut = "Ctrl+T", triggered=self.new_boat)
        self.newAct.setIcon(QIcon("icons/plus-circle-outline.svg"))
        self.backAct = QAction("Back", self, shortcut = "Ctrl+Z", triggered=self.back_action)
        self.backAct.setIcon(QIcon("icons/keyboard-backspace.svg"))
        self.renameAct = QAction("Rename", self, shortcut = "F2", triggered=self.open_rename_window)
        self.renameAct.setIcon(QIcon("icons/rename-box.svg"))

        self.clearAct = QAction("Clear", self, shortcut="Ctrl+E", triggered=self.clear)
        self.clearAct.setIcon(QIcon("icons/eraser.svg"))
        self.exitAct = QAction("Exit", self, shortcut="Ctrl+Q", triggered=self.close)
        self.exitAct.setIcon(QIcon("icons/exit-to-app.svg"))
        self.deleteAct = QAction("Delete boat", self, shortcut="Ctrl+D", triggered=self.delete_boat)
        self.deleteAct.setIcon(QIcon("icons/trash-can-outline.svg"))

        self.saveAct = QAction("Save", self, shortcut="Ctrl+S", triggered=self.save_to_file)
        self.saveAct.setIcon(QIcon("icons/content-save-outline.svg"))

    def center(self):
        qr = self.frameGeometry() 
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp) 
        self.move(qr.topLeft()) 
    
    def define_distance(self, p_1, p_2):
        return math.sqrt((p_1[0] - p_2[0]) ** 2 + (p_1[1] - p_2[1]) ** 2) 

    def angle_y_down(self, p_1, p_2):
        # Calculate the vector components
        x = p_2[0] - p_1[0]
        y = p_1[1] - p_2[1]  # Invert the y-component for downward direction

        # Calculate the angle in radians
        angle_rad = math.atan2(y, x)

        # Convert the angle to degrees
        angle_deg = math.degrees(angle_rad)

        # Calculate the angle with respect to the upward direction (0 degrees)
        angle_from_upward = (90 - angle_deg) % 360

        # Adjust the angle to be in the range (-180, 180]
        angle_from_upward = (angle_from_upward + 180) % 360 - 180

        return angle_from_upward

    def save_to_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)", options=options)

        if file_name:
            # preparing data to save
            scenario_duration = 300
            cur_scenario_duration = self.start_time_array[0]
            oscar_boat_movement = []
            for i in range(len(self.routes[0]) - 1):
                # curve
                if type(self.routes[0][i+1][0]) == tuple:
                    # not full curve
                    if len(self.routes[0][i+1]) == 1:
                        break
                    if type(self.routes[0][i][0]) == tuple:
                        b_0 = self.routes[0][i][1]
                    else:
                        b_0 = self.routes[0][i]
                    b_1 = self.routes[0][i+1][0]
                    b_2 = self.routes[0][i+1][1]
                    array_of_curve_coords = self.bezier_curve(b_0, b_1, b_2, 10)
                    time = 0
                    for j in range(len(array_of_curve_coords) - 1):
                        time += self.define_distance(array_of_curve_coords[j], array_of_curve_coords[j+1]) / (self.velocity_array[0][i] / 1.9438444924406)
                    cur_scenario_duration += time
                    if cur_scenario_duration > scenario_duration:
                        scenario_duration = cur_scenario_duration
                    a = [
                        time,
                        b_2[0], #b_2 (x)
                        self.width - b_2[1], #b_2 (y)
                        self.velocity_array[0][i],
                        self.angle_y_down(b_0, b_2),
                        b_1[0], #b_1 (x)
                        self.width - b_1[1] #b_1 (y)
                    ]
                else:
                    time = self.define_distance(self.routes[0][i], self.routes[0][i+1]) / (self.velocity_array[0][i] / 1.9438444924406)
                    a = [
                        time,
                        self.routes[0][i][0],
                        self.width - self.routes[0][i][1],
                        self.velocity_array[0][i],
                        self.angle_y_down(self.routes[0][i], self.routes[0][i+1])
                    ]
                oscar_boat_movement.append(a)

            object_list = []
            for i in range(1, self.cnt_of_boats):
                movement = []
                cur_scenario_duration = 0
                for j in range(len(self.routes[i]) - 1):
                    # curve
                    if type(self.routes[i][j+1][0]) == tuple:
                        # not full curve
                        if len(self.routes[i][j+1]) == 1:
                            break
                        if type(self.routes[i][j][0]) == tuple:
                            b_0 = self.routes[i][j][1]
                        else:
                            b_0 = self.routes[i][j]
                        b_1 = self.routes[i][j+1][0]
                        b_2 = self.routes[i][j+1][1]
                        array_of_curve_coords = self.bezier_curve(b_0, b_1, b_2, 10)
                        time = 0
                        for k in range(len(array_of_curve_coords) - 1):
                            time += self.define_distance(array_of_curve_coords[k], array_of_curve_coords[k+1]) / (self.velocity_array[i][j] / 1.9438444924406)
                        cur_scenario_duration += time
                        if cur_scenario_duration > scenario_duration:
                            scenario_duration = cur_scenario_duration
                        a = [
                            time,
                            b_2[0], #b_2 (x)
                            self.width - b_2[1], #b_2 (y)
                            self.velocity_array[i][j],
                            self.angle_y_down(b_0, b_2),
                            b_1[0], #b_1 (x)
                            self.width - b_1[1] #b_1 (y)
                        ]
                    else:
                        time = self.define_distance(self.routes[i][j], self.routes[i][j+1]) / (self.velocity_array[i][j] / 1.9438444924406)
                        a = [
                            time,
                            self.routes[i][j][0],
                            self.width - self.routes[i][j][1],
                            self.velocity_array[i][j],
                            self.angle_y_down(self.routes[i][j], self.routes[i][j+1])
                        ]
                    movement.append(a)
                boat = {
                    "object_name": "object_" + str(i),
                    "type":"boat",
                    "size":[
                        self.boat_size_array[self.cur_boat_index][0],
                        self.boat_size_array[self.cur_boat_index][1],
                        self.boat_size_array[self.cur_boat_index][2]
                    ],
                    "id":i,
                    "command_type":"dynamic_speed_heading",
                    "command" : {
                        "start_time" : self.start_time_array[i],
                        "movement" : movement
                    },
                    'CPA': 0,
                    'TCPA': 0,
                    'alarm_ground_truth':True
                }
                
                object_list.append(boat)

            data = {
                'file_version': 'v2',
                "scenario_duration":math.ceil(scenario_duration),
                'oscar_boat_movement': oscar_boat_movement,
                'object_list' : object_list
            }

            with open(file_name, 'w') as json_file:
                json.dump(data, json_file, indent=2)

    def show_board(self, myboard):
        height, width, _ = self.myboard.shape
        qimage = QImage(self.myboard.data, width, height, QImage.Format_RGB888)
        # Create a QPixmap from the QImage
        qpixmap = QPixmap.fromImage(qimage)
        self.image_frame.setPixmap(qpixmap)
        self.image_frame.mousePressEvent = self.mouse_press_event
        self.image_frame.mouseReleaseEvent = self.mouse_release_event

    def new_boat(self):
        if self.cnt_of_boats == 10:
            return
        self.chooseBoatAct.addItem(self.boat_names[self.cnt_of_boats])
        self.draw_line()
        self.chooseBoatAct.setCurrentIndex(self.cnt_of_boats)
        self.cur_boat_index = self.cnt_of_boats
        self.cnt_of_boats += 1
        self.startTimeSpinBox.setValue(self.start_time_array[self.cur_boat_index])
        

    def cur_boat_changed(self, index):
        self.cur_boat_index = index
        self.startTimeSpinBox.setValue(self.start_time_array[index])
        cnt_of_segments = len(self.velocity_array[self.cur_boat_index])
        if cnt_of_segments != 0:
            self.cur_velocity = self.velocity_array[self.cur_boat_index][cnt_of_segments - 1]
            print('velocity changed to', self.cur_velocity)
        self.velocitySpinBox.setValue(self.cur_velocity)
        self.lengthSpinBox.setValue(self.boat_size_array[self.cur_boat_index][0])
        self.widthSpinBox.setValue(self.boat_size_array[self.cur_boat_index][1])
        self.heightSpinBox.setValue(self.boat_size_array[self.cur_boat_index][2])

    def cur_type_of_line_changed(self, index):
        self.cur_type_of_line = index

    def cur_weather_changed(self, index):
        self.cur_weather_index = index
        # print('index changed to', index)
    
    def open_rename_window(self):
        rename_window = RenameWindow(self)
        rename_window.exec_()
        self.setWindowTitle(self.name_of_session)

    def start_time_value_changed(self, value):
        self.start_time_array[self.cur_boat_index] = value

    def velocity_value_changed(self, value):
        self.cur_velocity = value
    
    def length_value_changed(self, value):
        self.boat_size_array[self.cur_boat_index][0] = value

    def width_value_changed(self, value):
        self.boat_size_array[self.cur_boat_index][1] = value

    def height_value_changed(self, value):
        self.boat_size_array[self.cur_boat_index][2] = value



################################################## BOARD ITSELF ##################################################

    def bezier_curve(self, b_0, b_1, b_2, n):
        res = [b_0]
        for i in range(n):
            t = n * i / 100
            x = (b_0[0]-2*b_1[0]+b_2[0])*t*t+(-2*b_0[0]+2*b_1[0])*t+b_0[0]
            y = (b_0[1]-2*b_1[1]+b_2[1])*t*t+(-2*b_0[1]+2*b_1[1])*t+b_0[1]
            res.append((round(x), round(y)))
        res.append(b_2)
        return res

    def draw_line(self):
        self.myboard = np.full((self.width, self.height, 3), 255, dtype='uint8')
        print('routes:', self.routes)
        print('velocities:', self.velocity_array)
        # new segment of the line
        color_cnt = 0
        for route in self.routes:
            flag = True
            for x, y in route:
                if (type(x)==tuple):
                    b_0 = (curX, curY)
                    b_1 = x
                    b_2 = y
                    print('b_0', b_0, 'b_1', b_1, 'b_2', b_2)
                    array_of_curve_coords = self.bezier_curve(b_0, b_1, b_2, 100)
                    cv.rectangle(self.myboard, pt1=(b_1[0]-3,b_1[1]-3), pt2=(b_1[0]+3,b_1[1]+3), color=self.colors_array[color_cnt], thickness=1)
                    curve_flag = True
                    for i in range(len(array_of_curve_coords) - 1):
                        cv.line(self.myboard, array_of_curve_coords[i], array_of_curve_coords[i+1], self.colors_array[color_cnt], thickness=3)
                    curX = b_2[0]
                    curY = b_2[1]
                    cv.circle(self.myboard, b_2, 3, self.colors_array[color_cnt], thickness=3)
                else:
                    if flag:
                        flag = False
                        cv.circle(self.myboard, (x, y), 4, self.colors_array[color_cnt], thickness=4)
                        self.show_board(self.myboard)
                    else:
                        print('curX', curX, 'curY', curY, ' | ', x, y, sep='\t')
                        cv.line(self.myboard, (curX, curY), (x, y), self.colors_array[color_cnt], thickness=3)
                        cv.circle(self.myboard, (x, y), 3, self.colors_array[color_cnt], thickness=3)
                    curX = x
                    curY = y
            color_cnt += 1
        self.show_board(self.myboard)


    def find_nearest_point_index(self, point):
        min_distance = float('inf')
        self.nearest_index = -1
        # print('point = ', point, ', routes[cur_boat_index] =', self.routes[self.cur_boat_index])
        for i, coord in enumerate(self.routes[self.cur_boat_index]):
            if type(coord[0])==tuple:
                if len(coord) == 1:
                    distance = self.define_distance(coord[0], point)
                    if distance <= 10 and distance < min_distance:
                        min_distance = distance
                        self.nearest_index = (i, 0)
                    continue
                b_1 = coord[0]
                b_2 = coord[1]
                distance = self.define_distance(b_1, point)
                if distance <= 10 and distance < min_distance:
                    min_distance = distance
                    self.nearest_index = (i, 0)
                distance = self.define_distance(b_2, point)
                if distance <= 10 and distance < min_distance:
                    min_distance = distance
                    self.nearest_index = (i, 1)
            else:
                distance = self.define_distance(coord, point)
                # print(i, coord, 'distance =', distance)
                if distance <= 10 and distance < min_distance:
                    min_distance = distance
                    self.nearest_index = i

        return self.nearest_index



    def back_action(self):
        if self.cur_boat_index == 0 and len(self.routes[self.cur_boat_index]) == 1:
            return
        if len(self.routes[self.cur_boat_index]) == 0:
            return
        if len(self.routes[self.cur_boat_index]) == 1:
            self.routes[self.cur_boat_index].pop()
            self.draw_line()
            return
        if type(self.routes[self.cur_boat_index][-1])==tuple or \
         (type(self.routes[self.cur_boat_index][-1])==list and len(self.routes[self.cur_boat_index][-1]) == 2):
            self.velocity_array[self.cur_boat_index].pop()
        self.routes[self.cur_boat_index].pop()
        self.draw_line()


    def mouse_press_event(self, event):
        x = event.pos().x()
        y = event.pos().y()
        # add a segment
        if event.button() == Qt.LeftButton:
            #thirst step
            if len(self.routes[self.cur_boat_index]) == 0:
                cv.circle(self.myboard, (x, y), 4, self.colors_array[self.cur_boat_index], thickness=4)
                self.show_board(self.myboard)
                print(x, y, sep='\t')
                self.routes[self.cur_boat_index].append((x, y))
                return
            # direct line
            if self.cur_type_of_line == 0:
                if type(self.routes[self.cur_boat_index][-1]) == tuple:
                    prevX, prevY = self.routes[self.cur_boat_index][-1]
                else:
                    prevX, prevY = self.routes[self.cur_boat_index][-1][-1]
                print(x, y, sep='\t')
                cv.line(self.myboard, (prevX, prevY), (x, y), self.colors_array[self.cur_boat_index], thickness=3)
                cv.circle(self.myboard, (x, y), 3, self.colors_array[self.cur_boat_index], thickness=3)
                self.show_board(self.myboard)
                self.routes[self.cur_boat_index].append((x, y))
                self.velocity_array[self.cur_boat_index].append(self.cur_velocity)
                return
            # bezier curve
            if self.cur_type_of_line == 1:
                if type(self.routes[self.cur_boat_index][-1])==tuple or (type(self.routes[self.cur_boat_index][-1])==list and len(self.routes[self.cur_boat_index][-1]) == 2):
                    cv.circle(self.myboard, (x, y), 3, self.colors_array[self.cur_boat_index], thickness=3)
                    self.show_board(self.myboard)
                    print(x, y, sep='\t')
                    self.routes[self.cur_boat_index].append([(x, y)])
                    return
                else:
                    if type(self.routes[self.cur_boat_index][-2]) == tuple:
                        prevX, prevY = self.routes[self.cur_boat_index][-2]
                    else:
                        prevX, prevY = self.routes[self.cur_boat_index][-2][-1]
                    b_2 = self.routes[self.cur_boat_index][-1][0]
                    b_1 = (x, y)
                    b_0 = (prevX, prevY)
                    array_of_curve_coords = self.bezier_curve(b_0, b_1, b_2, 100)
                    curve_flag = True
                    cv.rectangle(self.myboard, pt1=(b_1[0]-3,b_1[1]-3), pt2=(b_1[0]+3,b_1[1]+3), color=self.colors_array[self.cur_boat_index], thickness=1)
                    for i in range(len(array_of_curve_coords) - 1):
                        cv.line(self.myboard, array_of_curve_coords[i], array_of_curve_coords[i+1], self.colors_array[self.cur_boat_index], thickness=3)
                    self.routes[self.cur_boat_index][-1][0] = b_1    
                    self.routes[self.cur_boat_index][-1].append(b_2)
                    self.velocity_array[self.cur_boat_index].append(self.cur_velocity)
                    print('b_0', b_0, 'b_1', b_1, 'b_2', b_2)
                    print(self.routes)
                    self.show_board(self.myboard)
                return


        # track a point to change its position
        if event.button() == Qt.RightButton:
            self.find_nearest_point_index((x, y))
            print('nearest_index =', self.nearest_index)

        # go back
        if event.button() == Qt.MiddleButton:
            self.back_action()
    
    def mouse_release_event(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.button() == Qt.RightButton:
            if self.nearest_index == -1:
                return
            if type(self.nearest_index) == tuple:
                self.routes[self.cur_boat_index][self.nearest_index[0]][self.nearest_index[1]] = (x, y)
            else:
                self.routes[self.cur_boat_index][self.nearest_index] = (x, y)
            self.draw_line()
        


    def clear(self):
        self.myboard = np.full((self.width, self.height, 3), 255, dtype='uint8')
        self.routes = [[(self.height // 2, self.width - 5)], [], [], [], [], [], [], [], [], []]
        self.chooseBoatAct.clear()
        self.cur_boat_index = 0
        self.cnt_of_boats = 1
        colors_array = [
            (0, 0, 0),        # Black (Oscar)
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (255, 128, 0),    # Orange
            (128, 0, 255),    # Purplel
            (0, 255, 128)     # Lime
        ]

        boat_names = [
            "Black (Oscar)",
            "Red",
            "Green",
            "Blue",
            "Yellow",
            "Magenta",
            "Cyan",
            "Orange",
            "Purple",
            "Lime",
        ]
        self.chooseBoatAct.addItem(self.boat_names[0])
        self.draw_line()
        self.start_time_array = [0 for i in range(10)]
        self.velocity_array = [[], [], [], [], [], [], [], [], [], []]
        self.boat_size_array = [[5, 3, 2] for i in range(10)]
        self.startTimeSpinBox.setValue(self.start_time_array[self.cur_boat_index])
        self.lengthSpinBox.setValue(self.boat_size_array[self.cur_boat_index][0])
        self.widthSpinBox.setValue(self.boat_size_array[self.cur_boat_index][1])
        self.heightSpinBox.setValue(self.boat_size_array[self.cur_boat_index][2])
        

    def delete_boat(self):
        if self.cur_boat_index == 0:
            self.routes[self.cur_boat_index] = [(self.height // 2, self.width - 5)]
            self.start_time_array[self.cur_boat_index] = 0
            self.draw_line()
            self.startTimeSpinBox.setValue(self.start_time_array[self.cur_boat_index])
            self.velocity_array[self.cur_boat_index] = []
            return
        if self.cnt_of_boats == 1:
            self.clear()
            return
        if len(self.routes) == 1:
            return
        self.myboard = np.full((self.width, self.height, 3), 255, dtype='uint8')
        self.routes.pop(self.cur_boat_index)
        self.start_time_array.pop(self.cur_boat_index)
        self.colors_array.pop(self.cur_boat_index)
        self.boat_names.pop(self.cur_boat_index)
        self.velocity_array.pop(self.cur_boat_index)
        self.boat_size_array.pop(self.cur_boat_index)
        self.show_board(self.myboard)
        self.cnt_of_boats -= 1
        
        if (self.cnt_of_boats == self.cur_boat_index):
            self.cur_boat_index -= 1

        self.chooseBoatAct.clear()
        for i in range(self.cnt_of_boats):
            self.chooseBoatAct.addItem(self.boat_names[i])
        self.draw_line()
        self.startTimeSpinBox.setValue(self.start_time_array[self.cur_boat_index])

        




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())