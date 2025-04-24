import global_variables

if global_variables.line == 0:
    BEACON_BLOCKS = {
        64: "beacon 1",
        72: "beacon 2",
        74: "beacon 3",
        87: "beacon 4",
        95: "beacon 5",
        104: "beacon 7",
        113: "beacon 8",
        122: "beacon 9",
        131: "beacon 10",
        140: "beacon 11",
        23: "beacon 12",
        17: "beacon 13",
        10: "beacon 14",
        3: "beacon 15",
        30: "beacon 18",
        38: "beacon 19",
        47: "beacon 20",
        56: "beacon 21",
        58: "beacon 22"
    }

    beacons = {
        "beacon 1": {
            "station_side": "right",
            "arriving_station": "GLENBURY",
            "new_station": "DORMONT",
            "station_distance": 287.0
        },
        "beacon 2": {
            "station_side": "right",
            "arriving_station": "DORMONT",
            "new_station": "MT LEBANON",
            "station_distance": 1237.0
        },
        "beacon 3": {
            "station_side": "right",
            "arriving_station": "MT LEBANON",
            "new_station": "POPLAR",
            "station_distance": 1737.0
        },
        "beacon 4": {
            "station_side": "left",
            "arriving_station": "POPLAR",
            "new_station": "CASTLE SHANNON",
            "station_distance": 4523.6
        },
        "beacon 5": {
            "station_side": "left",
            "arriving_station": "CASTLE SHANNON",
            "new_station": "MT LEBANON",
            "station_distance": 5136.1
        },
        "beacon 6": {
            "station_side": "left",
            "arriving_station": "MT LEBANON",
            "new_station": "DORMONT",
            "station_distance": 8023.6
        },
        "beacon 7": {
            "station_side": "right",
            "arriving_station": "DORMONT",
            "new_station": "GLENBURY",
            "station_distance": 8538.6
        },
        "beacon 8": {
            "station_side": "right",
            "arriving_station": "GLENBURY",
            "new_station": "OVERBROOK",
            "station_distance": 9459.6
        },
        "beacon 9": {
            "station_side": "right",
            "arriving_station": "OVERBROOK",
            "new_station": "INGLEWOOD",
            "station_distance": 10055.6
        },
        "beacon 10": {
            "station_side": "left",
            "arriving_station": "INGLEWOOD",
            "new_station": "CENTRAL",
            "station_distance": 10505.6
        },
        "beacon 11": {
            "station_side": "right",
            "arriving_station": "CENTRAL",
            "new_station": "WHITED",
            "station_distance": 10955.6
        },
        "beacon 12": {
            "station_side": "right",
            "arriving_station": "WHITED",
            "new_station": "LESUNSHINE STATION",
            "station_distance": 12689.6
        },
        "beacon 13": {
            "station_side": "right",
            "arriving_station": "LESUNSHINE STATION",
            "new_station": "EDGEBROOK",
            "station_distance": 13814.6
        },
        "beacon 14": {
            "station_side": "left",
            "arriving_station": "EDGEBROOK",
            "new_station": "PIONEER",
            "station_distance": 14690.6
        },
        "beacon 15": {
            "station_side": "left",
            "arriving_station": "PIONEER",
            "new_station": "LESUNSHINE STATION",
            "station_distance": 15389.6
        },
        "beacon 16": {
            "station_side": "left",
            "arriving_station": "LESUNSHINE STATION",
            "new_station": "WHITED",
            "station_distance": 16064.6
        },
        "beacon 17": {
            "station_side": "left",
            "arriving_station": "WHITED",
            "new_station": "SOUTH BANK",
            "station_distance": 17189.6
        },
        "beacon 18": {
            "station_side": "left",
            "arriving_station": "SOUTH BANK",
            "new_station": "CENTRAL",
            "station_distance": 18464.6
        },
        "beacon 19": {
            "station_side": "right",
            "arriving_station": "CENTRAL",
            "new_station": "INGLEWOOD",
            "station_distance": 18793.1
        },
        "beacon 20": {
            "station_side": "right",
            "arriving_station": "INGLEWOOD",
            "new_station": "OVERBROOK",
            "station_distance": 19314.6
        },
        "beacon 21": {
            "station_side": "left",
            "arriving_station": "OVERBROOK",
            "new_station": "Yard",
            "station_distance": 19764.6
        },
        "beacon 22": {
            "station_side": "none",
            "arriving_station": "YARD",
            "new_station": "YARD",
            "station_distance": 19852.6
        }
    }
elif global_variables.line == 1:
    BEACON_BLOCKS = {
        8: "beacon 1",
        16: "beacon 2",
        21: "beacon 3",
        87: "beacon 4",
        95: "beacon 5",
        104: "beacon 7",
        113: "beacon 8",
        122: "beacon 9",
        131: "beacon 10",
        140: "beacon 11",
        23: "beacon 12",
        17: "beacon 13",
        10: "beacon 14",
        3: "beacon 15",
        30: "beacon 18",
        38: "beacon 19",
        47: "beacon 20",
        56: "beacon 21",
        58: "beacon 22"
    }

    beacons = {
        "beacon 1": {
            "station_side": "right",
            "arriving_station": "SHADYSIDE",
            "new_station": "HERRON AVE",
            "station_distance": 174.5
        },
        "beacon 2": {
            "station_side": "right",
            "arriving_station": "HERRON AVE",
            "new_station": "SWISSVALE",
            "station_distance": 537
        },
        "beacon 3": {
            "station_side": "right",
            "arriving_station": "SWISSVALE",
            "new_station": "PENN STATION",
            "station_distance": 1812
        },
        "beacon 4": {
            "station_side": "left",
            "arriving_station": "PENN STATION",
            "new_station": "HERRON AVE",
            "station_distance": 174.5
        },

    }