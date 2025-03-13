#Philip Sherman
#Trains Group 2
#Train Controller SW UI
#3/12/2025

#stats page
'''
class StatsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Stats Page")
        self.setGeometry(100, 100, 600, 400)

        self.main_window = main_window

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Home Button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.return_home)
        layout.addWidget(self.home_btn, alignment=Qt.AlignRight)

        self.train_select = QComboBox()
        self.train_select.addItems(["Train 1", "Train 2", "Train 3"])
        self.train_select.currentIndexChanged.connect(self.update_stats)
        layout.addWidget(QLabel("Select Train:"))
        layout.addWidget(self.train_select)

        self.dim_label = QLabel()
        self.mass_label = QLabel()
        self.power_label = QLabel()
        self.passenger_label = QLabel()
        self.crew_label = QLabel()
        self.weight_label = QLabel()

        layout.addWidget(self.dim_label)
        layout.addWidget(self.mass_label)
        layout.addWidget(self.power_label)
        layout.addWidget(self.passenger_label)
        layout.addWidget(self.crew_label)
        layout.addWidget(self.weight_label)

        self.setLayout(layout)

        self.train_data = {
            "Train 1": {"dimensions": "20m x 3m x 4m", "mass": "5000 kg", "power": "1500 kW", "passengers": 100, "crew": 5},
            "Train 2": {"dimensions": "25m x 3.5m x 4.2m", "mass": "6000 kg", "power": "1800 kW", "passengers": 120, "crew": 6},
            "Train 3": {"dimensions": "30m x 3.8m x 4.5m", "mass": "7500 kg", "power": "2000 kW", "passengers": 150, "crew": 8},
        }

        self.update_stats()

    def update_stats(self):
        select_train = self.train_select.currentText()
        train_info = self.train_data[select_train]

        total_weight = self.calc_tot_weight(train_info["passengers"], train_info["crew"])

        self.dim_label.setText(f"Total Dimensions: {train_info['dimensions']}")
        self.mass_label.setText(f"Total Mass: {train_info['mass']}")
        self.power_label.setText(f"Power: {train_info['power']}")
        self.passenger_label.setText(f"Passenger Count: {train_info['passengers']}")
        self.crew_label.setText(f"Crew Count: {train_info['crew']}")
        self.weight_label.setText(f"Total Weight of Train: {total_weight} kg")

    def calc_tot_weight(self, passengers, crew):
        avg_weight = 75 #75kg per person
        return (passengers + crew) * avg_weight

    def return_home(self):
        self.close()
        self.main_window.show()




        def open_stats_page(self):
        if self.stats_window is None or not self.stats_window.isVisible():
            self.stats_window = StatsPage(self)
            self.stats_window.show()
            self.hide()


        self.stats_btn = QPushButton("Stats")
        self.stats_btn.setStyleSheet(button_style)
        self.stats_btn.clicked.connect(self.open_stats_page)

        button_layout.addWidget(self.stats_btn)    
        '''


'''##################################################################################################################################################

class SetConstantsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setWindowTitle("Set Constants Page")
        self.setGeometry(100, 100, 600, 400)

        P_max = 100 #max power constraint

        self.main_window = main_window
        self.power_control = PowerControl(P_max)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        #Home Button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.return_home)
        layout.addWidget(self.home_btn, alignment=Qt.AlignRight)

        self.ki_label = QLabel("Enter Ki:")
        self.ki_input = QLineEdit()
        layout.addWidget(self.ki_label)
        layout.addWidget(self.ki_input)

        self.kp_label = QLabel("Enter Kp:")
        self.kp_input = QLineEdit()
        layout.addWidget(self.kp_label)
        layout.addWidget(self.kp_input)

        self.P_target_label = QLabel("Enter Target Power:")
        self.P_target_input = QLineEdit()
        layout.addWidget(self.P_target_label)
        layout.addWidget(self.P_target_input)

        self.P_actual_label = QLabel("Enter Actual power:")
        self.P_actual_input = QLineEdit()
        layout.addWidget(self.P_actual_label)
        layout.addWidget(self.P_actual_input)

        #Submit
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.clicked.connect(self.calculate_and_send)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def calculate_and_send(self):
        try:
            ki = float(self.ki_input.text())
            kp = float(self.kp_input.text())
            P_target = float(self.P_target_input.text())
            P_actual = float(self.P_actual_input.text())

            self.power_control.update_gains(kp, ki)
            power = self.power_control.compute_Pcmd(P_target, P_actual)
            self.send_power(power)
        except ValueError:
            print("Please enter valid numerical values for Ki and Kp")

    def send_power(self, power):
        print(f"Power value {power} sent to the Train Model")

    
    def return_home(self):
        self.close()
        self.main_window.show()

##################################################################################################################################################'''