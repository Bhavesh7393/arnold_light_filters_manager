"""

alfm_logic_py2.py

This file is accessed when Python Version 2 is detected.

This file contains Class ArnoldLFM.
Main Window loading and Signals and Slots for UI building.

"""

import os
from PySide2 import QtCore, QtUiTools
from collections import OrderedDict
from alfm_functions_py2 import *


def hou_main_window():
    """
    Houdini Main Window QWidget Pointer
    :return:
    """

    return hou.qt.mainWindow()


class ArnoldLFM(QtWidgets.QDialog):
    """
    Arnold Light Filters Manager ArnoldLFM Class.

    This Class contains all main logical functions, and main UI.
    """

    # Dictionary {Light Filter Type: [Name, Node Name]}
    LIGHT_FILTERS = OrderedDict([("arnold::barndoor", ["Barndoor", "LFM_barndoor1"]),
                                 ("arnold::gobo", ["Gobo", "LFM_gobo1"]),
                                 ("arnold::light_blocker", ["Light Blocker", "LFM_light_blocker1"]),
                                 ("arnold::light_decay", ["Light Decay", "LFM_light_decay1"])])

    # Dictionary {Light Type Index: List of Light Filters supported by the Light Type}
    LIGHT_TYPES = {0: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   1: [list(LIGHT_FILTERS)[2]],
                   2: [list(LIGHT_FILTERS)[0], list(LIGHT_FILTERS)[1], list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   3: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   4: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   5: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   6: [list(LIGHT_FILTERS)[2]],
                   7: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]],
                   8: [list(LIGHT_FILTERS)[2], list(LIGHT_FILTERS)[3]]}

    def __init__(self, ui_path=None, parent=hou_main_window()):
        """
        Init Constructor
        :param ui_path: UI file path
        :param parent: Houdini Main Window
        """

        super(ArnoldLFM, self).__init__(parent)

        self.setWindowTitle("Arnold Light Filters Manager v1.0")
        self.resize(600, 500)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.init_ui(ui_path)
        self.create_layout()
        self.create_connections()
        self.light_filters_subnet()
        self.lights_list()

    def init_ui(self, ui_path):
        """
        Init UI
        :param ui_path: UI file path
        :return: None
        """

        if not ui_path:
            ui_path = "{0}/alfm_ui.ui".format(os.path.dirname(__file__))

        file = QtCore.QFile(ui_path)
        file.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(file, parentWidget=None)

        file.close()

    def create_layout(self):
        """
        Insert UI inside Layout
        :return: None
        """

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.ui)

    def create_connections(self):
        """
        Signals and Slots connections
        :return: None
        """
        self.ui.lights_list.itemSelectionChanged.connect(self.filters_list)
        self.ui.available_list.itemDoubleClicked.connect(self.attach_filter_btn)
        self.ui.active_list.itemDoubleClicked.connect(self.disconnect_filter_btn)
        self.ui.refresh_btn.clicked.connect(self.refresh_btn)
        self.ui.add_btn.clicked.connect(self.add_filter_btn)
        self.ui.attach_filter_btn.clicked.connect(self.attach_filter_btn)
        self.ui.remove_filter_btn.clicked.connect(self.remove_filter_btn)
        self.ui.disconnect_filter_btn.clicked.connect(self.disconnect_filter_btn)
        self.ui.light_filter_line.textChanged.connect(self.light_list_filter)
        self.ui.available_filter_line.textChanged.connect(self.available_list_filter)
        self.ui.active_filter_line.textChanged.connect(self.active_list_filter)
        self.ui.light_filter_clear_btn.clicked.connect(self.ui.light_filter_line.clear)
        self.ui.available_filter_clear_btn.clicked.connect(self.ui.available_filter_line.clear)
        self.ui.active_filter_clear_btn.clicked.connect(self.ui.active_filter_line.clear)

    def light_filters_subnet(self):
        """
        Create necessary nodes in obj context
        :return: None
        """

        obj = hou.node("obj")

        if obj.node("LFM_LIGHT_FILTERS_SUBNET") is None:
            self.subnet = obj.createNode("subnet", "LFM_LIGHT_FILTERS_SUBNET")
            self.shop = self.subnet.createNode("shopnet", "LFM_LIGHT_FILTERS_SHOPNET")
            self.blocker_subnet = self.subnet.createNode("subnet", "LFM_LIGHT_BLOCKER_SUBNET")
            self.asn = self.shop.createNode("arnold_vopnet", "LFM_LIGHT_FILTERS_VOPNET")
            self.subnet.layoutChildren()
            self.asn.node("OUT_material").destroy()
            self.subnet.moveToGoodPosition(move_inputs=False)
        else:
            pass

        # assign nodes instances
        self.subnet = obj.node("LFM_LIGHT_FILTERS_SUBNET")
        self.shop = self.subnet.node("LFM_LIGHT_FILTERS_SHOPNET")
        self.blocker_subnet = self.subnet.node("LFM_LIGHT_BLOCKER_SUBNET")
        self.asn = self.shop.node("LFM_LIGHT_FILTERS_VOPNET")

    def lights_list(self):
        """
        List out all Arnold Lights from obj context into Lights List widget
        :return: None
        """

        light_nodes = hou.objNodeTypeCategory().nodeType("arnold_light").instances()
        light_path_list = []
        for light_node in light_nodes:
            light_path_list.append(light_node.path())
        self.ui.lights_list.clear()
        for name in light_path_list:
            light_item = QtWidgets.QListWidgetItem(name)
            self.ui.lights_list.addItem(light_item)

        return light_path_list

    def refresh_btn(self):
        """
        Refreshes List Widgets and update Lights list
        :return: None
        """

        self.lights_list()
        self.ui.available_list.clear()
        self.ui.active_list.clear()
        self.ui.filters_list.clear()
        self.ui.light_filter_line.clear()
        self.ui.available_filter_line.clear()
        self.ui.active_filter_line.clear()
        self.ui.filter_name_line.clear()

    def add_filter_btn(self):
        """
        Add selected Arnold filters on selected lights
        :return: None
        """

        if not self.ui.lights_list.selectedItems():
            display_message("Please select at least one Light from the Lights list.")
        else:
            selected_filter = self.ui.filters_list.currentText()

            filter_name = self.ui.filter_name_line.text()

            filter_names = []

            for name in list(self.LIGHT_FILTERS.values()):
                filter_names.append(name[0])

            if filter_name != "":
                filter_node = self.asn.createNode(list(self.LIGHT_FILTERS.keys())[filter_names.index(selected_filter)],"LFM_" + filter_name)
            else:
                filter_node = self.asn.createNode(list(self.LIGHT_FILTERS.keys())[filter_names.index(selected_filter)],
                                                  list(self.LIGHT_FILTERS.values())[filter_names.index(selected_filter)][1])
            filter_node.moveToGoodPosition(move_inputs=False)

            if selected_filter == list(self.LIGHT_FILTERS.values())[2][0]:  # light blocker geo
                light_blocker_geo(self.blocker_subnet, filter_node.name(), filter_node)

            selected_lights_list = self.ui.lights_list.selectedItems()
            selected_lights = []

            for light_path in selected_lights_list:
                selected_lights.append(light_path.text())

            index = 2
            for light in selected_lights:
                fetch_node = hou.node(light + "/shopnet/arnold_vopnet").createNode("arnold::fetch", filter_node.name())
                fetch_node.parm("target").set(filter_node.path())
                while hou.node(light + "/shopnet/arnold_vopnet/OUT_light").input(index) is not None:
                    index += 1
                hou.node(light + "/shopnet/arnold_vopnet/OUT_light").setInput(index, fetch_node, 0)

            self.ui.active_list.addItem(filter_node.name())

            if self.ui.filter_name_line:
                self.ui.filter_name_line.clear()

    def attach_filter_btn(self):
        """
        Attach selected Arnold filters on selected lights
        :return: None
        """

        index = 2

        if not self.ui.lights_list.selectedItems():
            display_message("Please select at least one Light from the Lights list.")
        elif not self.ui.available_list.selectedItems():
            display_message("Please select at least one Light Filter from the Available Light Filters list.")
        else:
            for filter_name in self.ui.available_list.selectedItems():
                for light_path in self.ui.lights_list.selectedItems():
                    light_node = hou.node(light_path.text())
                    asn = light_node.node("shopnet/arnold_vopnet")
                    filter_node = self.asn.node(filter_name.text())
                    if asn.node(filter_name.text()) is None:
                        fetch_node = asn.createNode("arnold::fetch", filter_node.name())
                        fetch_node.parm("target").set(filter_node.path())
                        while light_node.node("shopnet/arnold_vopnet/OUT_light").input(index) is not None:
                            index += 1
                        light_node.node("shopnet/arnold_vopnet/OUT_light").setInput(index, fetch_node, 0)
                    else:
                        pass
                self.ui.active_list.addItem(filter_name.text())
                self.ui.available_list.takeItem(self.ui.available_list.row(filter_name))

    def remove_filter_btn(self):
        """
        Remove selected Arnold filters from scene
        :return: None
        """

        if self.ui.available_list.selectedItems() == [] and self.ui.active_list.selectedItems() == []:
            display_message("Please select at least one Light Filter from the Filters list.")
        else:
            if self.ui.available_list.selectedItems():
                for filter_name in self.ui.available_list.selectedItems():
                    filter_node = self.asn.node(filter_name.text())
                    if filter_node.type().name() == list(self.LIGHT_FILTERS.keys())[2]:  # "arnold::light_blocker"
                        try:
                            self.blocker_subnet.node(filter_node.name()).destroy()
                            filter_node.destroy()
                        except:
                            filter_node.destroy()
                    else:
                        filter_node.destroy()
                    self.ui.available_list.takeItem(self.ui.available_list.row(filter_name))
            elif self.ui.active_list.selectedItems():
                for filter_name in self.ui.active_list.selectedItems():
                    for light_path in self.ui.lights_list.selectedItems():
                        light_node = hou.node(light_path.text())
                        asn = light_node.node("shopnet/arnold_vopnet")
                        fetch_node = asn.node(filter_name.text())
                        filter_node = hou.node(fetch_node.parm("target").eval())
                        if filter_node is not None:
                            if filter_node.type().name() == list(self.LIGHT_FILTERS.keys())[2]:     # "arnold::light_blocker"
                                try:
                                    self.blocker_subnet.node(filter_node.name()).destroy()
                                    filter_node.destroy()
                                except:
                                    filter_node.destroy()
                            else:
                                filter_node.destroy()
                        else:
                            pass
                        fetch_node.destroy()
                        self.ui.active_list.takeItem(self.ui.active_list.row(filter_name))
            else:
                pass

    def disconnect_filter_btn(self):
        """
        Disconnect selected Arnold filters from selected lights
        :return: None
        """

        if not self.ui.lights_list.selectedItems():
            display_message("Please select at least one Light from the Lights list.")
        elif not self.ui.active_list.selectedItems():
            display_message("Please select at least one Light Filter from the Active Light Filters list.")
        else:
            for filter_name in self.ui.active_list.selectedItems():
                for light_path in self.ui.lights_list.selectedItems():
                    light_node = hou.node(light_path.text())
                    asn = light_node.node("shopnet/arnold_vopnet")
                    filter_node = asn.node(filter_name.text())
                    filter_node.destroy()
                    self.ui.active_list.takeItem(self.ui.active_list.row(filter_name))
                self.ui.available_list.addItem(filter_name.text())

    def filters_list(self):
        """
        Updates Filters list based on Lights selection
        :return: None
        """

        selected_lights = self.ui.lights_list.selectedItems()

        selected_light_paths = []
        for item in selected_lights:
            selected_light_paths.append(item.text())

        light_nodes = []
        for light in selected_light_paths:
            light_nodes.append(hou.node(light))

        light_type_indexes = []
        for light_type in light_nodes:
            light_type_indexes.append(light_type.parm("ar_light_type").eval())

        common_filters_list = accessible_filters(light_type_indexes, self.LIGHT_TYPES)

        if common_filters_list is not None:
            common_filters_list.sort()
            self.ui.filters_list.clear()
            for light_filter in common_filters_list:
                if light_filter == list(self.LIGHT_FILTERS)[0]:
                    self.ui.filters_list.addItem(self.LIGHT_FILTERS[list(self.LIGHT_FILTERS.keys())[0]][0])
                elif light_filter == list(self.LIGHT_FILTERS)[1]:
                    self.ui.filters_list.addItem(self.LIGHT_FILTERS[list(self.LIGHT_FILTERS.keys())[1]][0])
                elif light_filter == list(self.LIGHT_FILTERS)[2]:
                    self.ui.filters_list.addItem(self.LIGHT_FILTERS[list(self.LIGHT_FILTERS.keys())[2]][0])
                else:
                    self.ui.filters_list.addItem(self.LIGHT_FILTERS[list(self.LIGHT_FILTERS.keys())[3]][0])
        else:
            self.ui.filters_list.clear()

        self.active_list = active_list(self.ui.lights_list, self.ui.active_list, self.LIGHT_FILTERS)

        available_filters_list = self.asn.allSubChildren()

        self.available_list = available_list(available_filters_list, common_filters_list, self.ui.available_list,self.ui.active_list)

        if self.ui.available_filter_line:
            self.ui.available_filter_line.clear()
        else:
            pass
        if self.ui.active_filter_line:
            self.ui.active_filter_line.clear()
        else:
            pass

    def light_list_filter(self):
        """
        Filters the Lights text list
        :return: None
        """

        try:
            list_filter(self.lights_list(), self.ui.light_filter_line, self.ui.lights_list)
        except:
            pass

    def available_list_filter(self):
        """
        Filters the Available Filters text list
        :return: None
        """

        try:
            list_filter(self.available_list, self.ui.available_filter_line, self.ui.available_list)
        except:
            pass

    def active_list_filter(self):
        """
        Filters the Active Filters text list
        :return: None
        """

        try:
            list_filter(self.active_list, self.ui.active_filter_line, self.ui.active_list)
        except:
            pass