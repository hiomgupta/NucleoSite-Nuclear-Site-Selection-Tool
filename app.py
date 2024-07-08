import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QVBoxLayout, QComboBox, QCheckBox, QFrame, QHBoxLayout, QTextEdit, QMainWindow, QGraphicsDropShadowEffect
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import Point, wkt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from pyproj import Proj, Transformer
from fpdf import FPDF
from matplotlib.patches import Rectangle

# Nucleosite_splash_screen = r'data\Nucleosite_splash_screen.py'

from Nucleosite_splash_screen import Ui_SplashScreen

counter = 0

class SplashScreen(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self)

        #Remove title bar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        #Drop Shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.frame.setGraphicsEffect(self.shadow)

        ## QTIMER ==> START
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # TIMER IN MILLISECONDS
        self.timer.start(35)

        # Initial Text
        self.ui.loading_label.setText("<strong>WELCOME</strong>")

        # Change Texts
        QtCore.QTimer.singleShot(1500, lambda: self.ui.loading_label.setText("<strong>LOADING</strong> DATABASE"))
        QtCore.QTimer.singleShot(3000, lambda: self.ui.loading_label.setText("<strong>LOADING</strong> USER INTERFACE"))

        

        self.show() 

    def progress(self):

        global counter

        # SET VALUE TO PROGRESS BAR
        self.ui.progressBar.setValue(counter)

        # CLOSE SPLASH SCREE AND OPEN APP
        if counter > 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.main = MainWindow()
            self.main.show()

            # CLOSE SPLASH SCREEN
            self.close()

        # INCREASE COUNTER
        counter += 1

        

        


class CoordinateConverter:
    def __init__(self, ax, transformer, parent):
        self.ax = ax
        self.transformer = transformer
        self.parent = parent
        self.cid = ax.figure.canvas.mpl_connect('button_press_event', self)

    def __call__(self, event):
        if event.inaxes != self.ax:
            return
        
        x, y = event.xdata, event.ydata
        lon, lat = self.transformer.transform(x, y)
        self.parent.check_dam_click(x, y)

class MatplotlibZoom:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.base_scale = 1.5

    def zoom(self, event):
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        if event.button == 'up':
            scale_factor = 1 / self.base_scale
        elif event.button == 'down':
            scale_factor = self.base_scale
        else:
            scale_factor = 1

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        self.ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
        self.ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
        self.canvas.draw()

# Filepath for shapefile for state boundary
shapefile_path = r'data\Administrative Boundary Database\STATE_BOUNDARY.shp' 
gdf = gpd.read_file(shapefile_path)

# Filepath for dams.csv
dams = pd.read_csv(r"data\dam\dam (1).csv")
dams['geometry'] = dams['geometry'].apply(wkt.loads)
dams = gpd.GeoDataFrame(dams, geometry='geometry')
if dams.empty:
    print("The dams GeoDataFrame is empty. Please check the CSV file and contents.")

proj = 'epsg:3857'  # WGS 84 / Pseudo-Mercator
inverse_proj = 'epsg:4326'  # WGS 84
transformer = Transformer.from_crs(proj, inverse_proj, always_xy=True)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("NucleoSite")
        
        MainWindow.resize(1500, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Main vertical layout
        self.mainLayout = QVBoxLayout(self.centralwidget)
        
        # Horizontal layout for sidebar and graphics
        self.contentLayout = QHBoxLayout()

        self.frame = QFrame(self.centralwidget)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame.setFixedWidth(400)
        self.frame.setMinimumSize(QtCore.QSize(400, 600))  # Set minimum size for the frame
        self.frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # Set size policy

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 19, 0, 1, 1)

        self.combo_box = QComboBox(self.frame)
        self.combo_box.addItem("STATE")
        self.combo_box.addItems(gdf['STATE'].unique())
        self.combo_box.currentIndexChanged.connect(self.plot_selected_state)
        self.gridLayout.addWidget(self.combo_box, 0, 0, 1, 1)


        self.gridLayoutWidget = QtWidgets.QWidget(self.frame)
        self.gridLayoutWidget.setMinimumSize(QtCore.QSize(400, 300))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout.addWidget(self.gridLayoutWidget, 1, 0, 1, 1)  # Add this line to place gridLayoutWidget in the layout


        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)

        self.checkBox = QCheckBox(self.frame)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 4, 0, 1, 1)

        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_2.addWidget(self.lineEdit, 4, 1, 1, 1)

        self.SlineEdit = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit.setObjectName("SlineEdit")
        self.gridLayout_2.addWidget(self.SlineEdit, 4, 2, 1, 1)

        self.checkBox_2 = QCheckBox(self.frame)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_2.addWidget(self.checkBox_2, 5, 0, 1, 1)

        self.lineEdit_2 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout_2.addWidget(self.lineEdit_2, 5, 1, 1, 1)

        self.SlineEdit_2 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_2.setObjectName("SlineEdit_2")
        self.gridLayout_2.addWidget(self.SlineEdit_2, 5, 2, 1, 1)

        self.checkBox_3 = QCheckBox(self.frame)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout_2.addWidget(self.checkBox_3, 6, 0, 1, 1)

        self.lineEdit_3 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.gridLayout_2.addWidget(self.lineEdit_3, 6, 1, 1, 1)

        self.SlineEdit_3 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_3.setObjectName("SlineEdit_3")
        self.gridLayout_2.addWidget(self.SlineEdit_3, 6, 2, 1, 1)

        self.checkBox_4 = QCheckBox(self.frame)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout_2.addWidget(self.checkBox_4, 7, 0, 1, 1)

        self.lineEdit_4 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.gridLayout_2.addWidget(self.lineEdit_4, 7, 1, 1, 1)

        self.SlineEdit_4 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_4.setObjectName("SlineEdit_4")
        self.gridLayout_2.addWidget(self.SlineEdit_4, 7, 2, 1, 1)

        self.checkBox_5 = QCheckBox(self.frame)
        self.checkBox_5.setObjectName("checkBox_5")
        self.gridLayout_2.addWidget(self.checkBox_5, 8, 0, 1, 1)

        self.lineEdit_5 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout_2.addWidget(self.lineEdit_5, 8, 1, 1, 1)

        self.SlineEdit_5 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_5.setObjectName("SlineEdit_5")
        self.gridLayout_2.addWidget(self.SlineEdit_5, 8, 2, 1, 1)

        self.checkBox_6 = QCheckBox(self.frame)
        self.checkBox_6.setObjectName("checkBox_6")
        self.gridLayout_2.addWidget(self.checkBox_6, 9, 0, 1, 1)

        self.lineEdit_6 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.gridLayout_2.addWidget(self.lineEdit_6, 9, 1, 1, 1)

        self.SlineEdit_6 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_6.setObjectName("SlineEdit_6")
        self.gridLayout_2.addWidget(self.SlineEdit_6, 9, 2, 1, 1)

        self.checkBox_7 = QCheckBox(self.frame)
        self.checkBox_7.setObjectName("checkBox_7")
        self.gridLayout_2.addWidget(self.checkBox_7, 10, 0, 1, 1)

        self.lineEdit_7 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.gridLayout_2.addWidget(self.lineEdit_7, 10, 1, 1, 1)

        self.SlineEdit_7 = QtWidgets.QLineEdit(self.frame)
        self.SlineEdit_7.setObjectName("SlineEdit_7")
        self.gridLayout_2.addWidget(self.SlineEdit_7, 10, 2, 1, 1)

        self.contentLayout.addWidget(self.frame)

        self.graphics_frame = QFrame(self.centralwidget)
        self.graphics_layout = QVBoxLayout(self.graphics_frame)

        self.figure, self.ax = plt.subplots(figsize=(20, 20))
        self.ax.axis('off')
        self.canvas = FigureCanvas(self.figure)
        self.graphics_layout.addWidget(self.canvas)
        self.contentLayout.addWidget(self.graphics_frame)

        self.converter = CoordinateConverter(self.ax, transformer, self)
        self.zoom = MatplotlibZoom(self.ax, self.canvas)
        self.canvas.mpl_connect('scroll_event', self.zoom.zoom)

        self.current_hover_text = None  # Keep track of the current hover text
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)


        # Add the content layout to the main layout
        self.mainLayout.addLayout(self.contentLayout)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        MainWindow.setCentralWidget(self.centralwidget)

        # Create the menu bar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1084, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # Create the File menu
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menubar.addAction(self.menuFile.menuAction())

        # Add Exit action to the File menu
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionExit)
        self.actionExit.triggered.connect(QtWidgets.qApp.quit)

        # Create the Help menu
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menubar.addAction(self.menuHelp.menuAction())

        # Add About action to the Help menu
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.menuHelp.addAction(self.actionAbout)
        self.actionAbout.triggered.connect(self.show_about)

        # Add Export Report action to the File menu
        self.actionExport_Report = QtWidgets.QAction(MainWindow)
        self.actionExport_Report.setObjectName("actionExport_Report")
        self.menuFile.addAction(self.actionExport_Report)
        self.actionExport_Report.triggered.connect(self.export_report)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.dams = dams
        self.selected_dam = None
        self.current_grid_points = []
        self.info_ax = None  # Axis for displaying dam information
        self.info_box = None  # Rectangle for info box

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NucleoSite"))
        MainWindow.setWindowIcon(QIcon(r'New folder\logo.png'))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionExport_Report.setText(_translate("MainWindow", "Export Report"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.label.setText(_translate("MainWindow", "Parameters"))
        self.checkBox.setText(_translate("MainWindow", "Earthquake risk"))
        self.checkBox_2.setText(_translate("MainWindow", "Population"))
        self.checkBox_3.setText(_translate("MainWindow", "Nearest Highway"))
        self.checkBox_4.setText(_translate("MainWindow", "Nearest Airport"))
        self.checkBox_5.setText(_translate("MainWindow", "Soil/Geotechnical"))
        self.checkBox_6.setText(_translate("MainWindow", "Mining"))
        self.checkBox_7.setText(_translate("MainWindow", "Wind speed "))
        

    def show_about(self):
        about_text = """
        <h2>About Nucleosite</h2>
        <p>NucleoSite is an advanced desktop application developed to enhance the site selection process for nuclear power plants across India. Utilizing the robust PyQt5 framework, this application provides interactive geographical visualizations that allow users to explore dam locations within various states. <br> The application displays detailed information about selected dams, such as earthquake risk, population density, proximity to highways and airports, soil/geotechnical conditions, mining activities, and wind speed.</p>
        <h3>Features:</h3>
        <ul>
            <li>Interactive map with zoom and coordinate conversion</li>
            <li>Detailed dam information</li>
            <li>Grid point visualization</li>
            <li>Comprehensive PDF report generation</li>
        </ul>
        <h3>Developers:</h3>
        <p>Developed by <b>Om Gupta</b> and <b>Nirman Jaiswal</b><br>
        under the mentorship of <b>Prof. Sushobhan Sen</b> at IIT Gandhinagar, as part of the Summer Research Internship Program (SRIP) 2024.</p>
        <p>For more information or support, please visit our <a href="https://github.com/hiomgupta/Nuclear-Site-Selection">GitHub repository</a>.</p>
        """

        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle("About Nucleosite")
        msg_box.setText(about_text)
        msg_box.setWindowIcon(QIcon(r'D:\CS\GitHub\Nuclear-Site-Selection\Optics\WhatsApp Image 2024-07-02 at 18.24.47_01ef9468.jpg'))
        msg_box.exec_()
    
    def log(self, message):
        """Log a message to the QTextEdit widget."""
        self.log_output.append(message)

    def plot_selected_state(self):
        state_name = self.combo_box.currentText()
        self.ax.clear()
        state_dams = self.dams[self.dams['STATE_1'] == state_name]
        state = gdf[gdf['STATE'] == state_name]
        if not state.empty:
            self.ax.axis('off')
            state.plot(ax=self.ax, edgecolor='black', color='white', figsize=(20, 20))
            if not state_dams.empty:
                state_dams.plot(ax=self.ax, marker='.', color='red', markersize=15)
            self.ax.set_title(f"Dams in {state_name}")
            self.canvas.draw()

    def add_grid_points(self, dam_name):
        # Folderpath for base directory where all the csv files for gridpoints are stored
        base_dir = r"data\gridpoints_dams_csv"
        safe_dam_name = dam_name.replace(' ', '_').replace('/', '_').replace(':', '').replace('\n', '_')
        file_path = os.path.join(base_dir, safe_dam_name)
        file_path += '.csv'

        grid_points_for_dam = pd.read_csv(file_path)
        grid_points_for_dam['geometry'] = grid_points_for_dam['geometry'].apply(wkt.loads)
        grid_points_for_dam = gpd.GeoDataFrame(grid_points_for_dam, geometry='geometry')

        if not grid_points_for_dam.empty:
            # Remove previous grid points
            for point in self.current_grid_points:
                point.remove()
            self.current_grid_points.clear()

            # Plot new grid points and store the plot objects
            x = grid_points_for_dam.geometry.x
            y = grid_points_for_dam.geometry.y
            self.current_grid_points = self.ax.plot(x, y, 'o', markersize=0.5, color='blue')
            self.canvas.draw()

    def add_dam_info_plot(self, dam):

        # Create new info plot in bottom right corner with box
        self.info_ax = self.figure.add_axes([0.65, 0.05, 0.3, 0.25])  # Adjust position and size as needed
        self.info_ax.axis('off')

        info_text = f"Dam Name: {dam['dm_name']}\n" \
                    f"Location: ({dam.dm_long}, {dam.dm_lat})"

        # Add a rectangle patch around the info text
        bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1.5)
        self.info_ax.text(0.5, 0.5, info_text, verticalalignment='center', horizontalalignment='center', 
                          transform=self.info_ax.transAxes, bbox=bbox_props, wrap=True, fontsize=10)

        # Calculate and add the rectangle patch
        info_bbox = self.info_ax.get_window_extent().transformed(self.figure.dpi_scale_trans.inverted())
        self.info_box = Rectangle((info_bbox.x0, info_bbox.y0), info_bbox.width, info_bbox.height,
                                  edgecolor="black", linewidth=1.5, facecolor="none", transform=self.figure.transFigure)
        self.figure.patches.append(self.info_box)

        self.canvas.draw()

    def check_dam_click(self, lon, lat):
        click_point = Point(lon, lat)
        click_buffer = click_point.buffer(5000)
        self.selected_dam = None  # Initialize or reset the selected dam attribute
        for idx, dam in self.dams.iterrows():
           
            if dam.geometry.intersects(click_buffer):
                self.selected_dam = dam  # Store the entire GeoSeries object representing the dam
                self.update_parameters(dam)
                dam_name = dam['dm_name']
                self.add_grid_points(dam_name)
                self.add_dam_info_plot(dam)
                break

        if self.selected_dam is None:
            self.log("No dam selected.")

    def update_parameters(self, dam):
        self.lineEdit.setText(str(dam['dm_ses_zon']))
        self.lineEdit_2.setText(str(dam['Avg_population']))
        self.lineEdit_3.setText(str(dam['nearest_highway_distance'])+" km, "+(dam['nearest_highway']))
        self.lineEdit_4.setText(str(dam['distance_to_nearest_airport_km'])+" km")

    def on_hover(self, event):
        if event.inaxes != self.ax:
            return

        x, y = event.xdata, event.ydata
        hover_point = Point(x, y)
        hover_buffer = hover_point.buffer(5000)

        # Remove previous hover text if it exists
        if self.current_hover_text is not None:
            self.current_hover_text.remove()
            self.current_hover_text = None

        # Check if the mouse is near any dam
        for idx, dam in dams.iterrows():
            if dam.geometry.intersects(hover_buffer):
                self.current_hover_text = self.ax.text(x, y, dam['dm_name'], fontsize=12, color='blue')
                self.canvas.draw()
                break
        else:
            self.canvas.draw()

    def capture_canvas(self):
        # Ensure the GUI has updated its visual representation
        self.canvas.draw()
        
        # Grab the current state of the canvas after all drawings are complete
        pixmap = self.canvas.grab()

        # Correct the file path handling for cross-platform compatibility
        image_path = os.path.join(r"New folder", "image.png")  # More reliable path handling
        pixmap.save(image_path, "PNG")  # Save the image as PNG

        # Optionally log the image path to confirm where it's saved
        self.log(f"Canvas image saved at: {image_path}")

    def export_report(self):
        state_name = self.combo_box.currentText()
        if self.selected_dam is None:
            self.log("No dam has been selected for reporting.")
            QtWidgets.QMessageBox.information(None, "Export Report", "Please select a dam before exporting a report.")
            return

        self.capture_canvas()  # Capture the canvas image before starting the PDF report

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, 'NucleoSite', 0, 1, 'C')
        pdf.cell(200, 10, f"Report for {self.selected_dam['dm_name']} in {state_name}", 0, 1, 'C')
        coordinates = f"{self.selected_dam.geometry.x}, {self.selected_dam.geometry.y}"
        pdf.cell(200, 10, f'Coordinates: {coordinates}', 0, 1, 'C')
        pdf.cell(200, 10, f'Dam Name: {self.selected_dam["dm_name"]}', 0, 1, 'C')

        # Include the image captured from the canvasMain APP\data\Canvas Captures
        image_path = r"New folder\image.png"

        image_x = 10  # X position of the image
        image_y = 80  # Y position of the image
        image_width = 180  # Width of the image
        image_height = 120  # Height of the image
        pdf.image(image_path, x=image_x, y=image_y, w=image_width, h=image_height)

        table_start_y = image_y + image_height + 10  # 10 is a buffer space to ensure no overlap


        pdf.set_y(table_start_y)

        # Table header
        pdf.set_fill_color(200, 220, 255)  # Light blue background for header
        column_width = 40
        pdf.set_font("Arial", 'B', 10)
        headers = ["S.No", "Data", "Threshold Value", "Current Values", "Result"]
        for header in headers:
            pdf.cell(column_width, 10, header, 1, 0, 'C', 1)
        pdf.ln()

        # Table rows
        factors = {
            "Earthquake Risk": self.lineEdit.text(),
            "Population": self.lineEdit_2.text(),
            "Nearest Highway": self.lineEdit_3.text(),
            "Nearest Airport": self.lineEdit_4.text(),
            "Soil/Geotechnical": self.lineEdit_5.text(),
            "Mining": self.lineEdit_6.text(),
            "Wind Speed": self.lineEdit_7.text()
        }

        pdf.set_font("Arial", '', 10)
        default_current_value = "100"  # Default current value, can be adjusted as needed
        for idx, (factor, threshold_value) in enumerate(factors.items(), 1):
            pdf.cell(column_width, 10, str(idx), 1)
            pdf.cell(column_width, 10, factor, 1)
            pdf.cell(column_width, 10, threshold_value, 1)
            pdf.cell(column_width, 10, default_current_value, 1)
            pdf.cell(column_width, 10, "Unknown", 1)
            pdf.ln()

        # Save the PDF
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save Report", "", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            pdf.output(file_path)
            self.log(f"Report saved to {file_path}")
            QtWidgets.QMessageBox.information(None, "Export Report", f"Report saved to {file_path}")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()

    # Load main window after splash screen
    main = MainWindow()

    sys.exit(app.exec_())
