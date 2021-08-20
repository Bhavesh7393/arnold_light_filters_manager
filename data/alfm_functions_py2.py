'''

alfm_functions_py2.py

This file is accessed when Python Version 2 is detected.

This file contains all required functions to run UI.

'''

import hou
from PySide2 import QtWidgets


def accessible_filters(light_indexes, LIGHT_TYPES):
    """
    Intersection of light filters list based on Light Type of selected lights.
    :param light_indexes: light type index
    :param LIGHT_TYPES: Dictionary of LIGHT_TYPES
    :return: List of Intersection of light filters
    """
    light_filters = []
    for index in light_indexes:
        light_filters.append(list(LIGHT_TYPES[index]))

    if light_filters:
        common_filters = list(set.intersection(*map(set, tuple(light_filters))))
        return common_filters
    else:
        pass


def active_list(ui_lights_list, ui_active_list, LIGHT_FILTERS):
    """
    Generate Active Light Filters list based on lights selection.
    :param ui_lights_list: lights_list widget
    :param ui_active_list: active_list widget
    :param LIGHT_FILTERS: LIGHT_FILTERS dictionary
    :return: List of active list widget items
    """

    selected_lights = ui_lights_list.selectedItems()

    selected_filter_nodes = []

    for light in selected_lights:
        selected_light_node = hou.node(light.text())
        selected_asn_node = selected_light_node.node("shopnet/arnold_vopnet")
        light_filters_nodes = selected_asn_node.allSubChildren()
        for filter_name in light_filters_nodes:
            if len(light_filters_nodes) == 1 and light_filters_nodes[0].type().name() == "arnold_light":
                selected_filter_nodes.append(" ")
            elif filter_name.type().name() == "arnold::fetch" or filter_name.type().name() in list(LIGHT_FILTERS):
                selected_filter_nodes.append(filter_name)
            else:
                pass

    filter_names = []

    for light_name in selected_filter_nodes:
        if " " not in selected_filter_nodes:
            filter_names.append(light_name.name())
        else:
            pass

    duplicate_filter_names = []

    ui_active_list.clear()

    for filter_name in filter_names:
        if len(selected_lights) == 1 and " " not in selected_filter_nodes:
            ui_active_list.addItem(filter_name)
        elif filter_names.count(filter_name) == len(
                selected_lights) and filter_name not in duplicate_filter_names and " " not in selected_filter_nodes:
            duplicate_filter_names.append(filter_name)
        else:
            pass

    for filter_name in duplicate_filter_names:
        ui_active_list.addItem(filter_name)

    if len(selected_lights) == 1:
        return filter_names
    else:
        return duplicate_filter_names


def available_list(available_filters_list, common_filters, ui_available_list, ui_active_list):
    """
    Generate Available Light Filters list based on lights selection.
    :param available_filters_list: Available filter nodes for selected lights
    :param common_filters: Available light filters based on light type
    :param ui_available_list: available_list widget
    :param ui_active_list: active_list widget
    :return: List of available list widget items
    """

    filter_names = []

    if common_filters is not None:
        for filter_node in available_filters_list:
            for filter_name in common_filters:
                if filter_node.type().name() == filter_name:
                    filter_names.append(filter_node.name())
                else:
                    pass
    else:
        pass

    active_list_names = []

    for num in range(ui_active_list.count()):
        active_list_names.append(ui_active_list.item(num).text())

    available_list_names = []

    ui_available_list.clear()
    for filter_name in filter_names:
        if filter_name not in active_list_names:
            available_list_names.append(filter_name)
            filter_item = QtWidgets.QListWidgetItem(filter_name)
            ui_available_list.addItem(filter_item)
        else:
            pass

    return available_list_names


def light_blocker_geo(blocker_subnet, blocker_name, blocker_node):
    """
    Create Light Blocker Shape and link it to the relevant Light Blocker Filter.
    :param blocker_subnet: blocker subnet node
    :param blocker_name: Light Blocker name string from UI
    :param blocker_node: Light Blocker Filter Object Node
    :return: None
    """

    # create blocker geo
    geo = blocker_subnet.createNode('geo', blocker_name)
    geo.moveToGoodPosition(move_inputs=False)

    # create shapes
    box = geo.createNode('box')
    sphere = geo.createNode('sphere')
    grid = geo.createNode('grid')
    tube = geo.createNode('tube')
    switch = geo.createNode('switch')
    color = geo.createNode('color')
    convline = geo.createNode('convertline')
    pack = geo.createNode('pack')
    null = geo.createNode('null', 'OUT')

    # set geo Arnold Visibility values
    geo.parm('ar_visibility_camera').set(0)
    geo.parm('ar_visibility_shadow').set(0)
    geo.parm('ar_visibility_diffuse_transmit').set(0)
    geo.parm('ar_visibility_specular_transmit').set(0)
    geo.parm('ar_visibility_diffuse_reflect').set(0)
    geo.parm('ar_visibility_specular_reflect').set(0)
    geo.parm('ar_visibility_volume').set(0)
    geo.parm('ar_receive_shadows').set(0)
    geo.parm('ar_self_shadows').set(0)
    geo.parm('ar_opaque').set(0)
    geo.parm('ar_skip').set(1)

    # set connections
    switch.setInput(0, box, 0)
    switch.setInput(1, sphere, 0)
    switch.setInput(2, grid, 0)
    switch.setInput(3, tube, 0)
    color.setInput(0, switch, 0)
    convline.setInput(0, color, 0)
    pack.setInput(0, convline, 0)
    null.setInput(0, pack, 0)
    geo.layoutChildren()

    # set shape nodes values
    sphere.parm('type').set(2)
    sphere.parm('scale').set(0.5)
    sphere.parm('rows').set(16)
    sphere.parm('cols').set(16)
    grid.parm('sizex').set(1)
    grid.parm('sizey').set(1)
    grid.parm('rx').set(90)
    grid.parm('rows').set(2)
    grid.parm('cols').set(2)
    tube.parm('type').set(1)
    tube.parm('cap').set(1)
    tube.parm('rad1').set(0.5)
    tube.parm('rad2').set(0.5)
    tube.parm('cols').set(20)
    color.parm('colorr').set(0.8)
    color.parm('colorg').set(0.0)
    color.parm('colorb').set(0.0)
    convline.parm('computelength').set(0)
    null.setDisplayFlag(1)
    null.setRenderFlag(1)

    # set switch python expression
    switch.setExpressionLanguage(hou.exprLanguage.Python)
    switch.parm("input").setExpression("""if hou.node("{0}").parm("geometry_type").eval() == "box":
    return 0
elif hou.node("{0}").parm("geometry_type").eval() == "sphere":
    return 1
elif hou.node("{0}").parm("geometry_type").eval() == "plane":
    return 2
else:
    return 3""".format(blocker_node.path()))

    # set 4x4 matrix
    blocker_node.parm('geometry_matrix1').setExpression(
        'ch("{0}/sx")*(cos(ch("{0}/ry"))*cos(ch("{0}/rz")))'.format(geo.path()))
    blocker_node.parm('geometry_matrix2').setExpression(
        'ch("{0}/sx")*(cos(ch("{0}/ry"))*sin(ch("{0}/rz")))'.format(geo.path()))
    blocker_node.parm('geometry_matrix3').setExpression(
        '-ch("{0}/sx")*(sin(ch("{0}/ry")))'.format(geo.path()))
    blocker_node.parm('geometry_matrix5').setExpression(
        '(-ch("{0}/sy")*(cos(ch("{0}/rx"))*sin(ch("{0}/rz"))))+(ch("{0}/sy")*(sin(ch("{0}/rx"))*sin(ch("{0}/ry"))*cos(ch("{0}/rz"))))'.format(geo.path()))
    blocker_node.parm('geometry_matrix6').setExpression(
        '(ch("{0}/sy")*(cos(ch("{0}/rx"))*cos(ch("{0}/rz"))))+(ch("{0}/sy")*(sin(ch("{0}/rx"))*sin(ch("{0}/ry"))*sin(ch("{0}/rz"))))'.format(geo.path()))
    blocker_node.parm('geometry_matrix7').setExpression(
        'ch("{0}/sy")*(sin(ch("{0}/rx"))*cos(ch("{0}/ry")))'.format(geo.path()))
    blocker_node.parm('geometry_matrix9').setExpression(
        '(ch("{0}/sz")*(sin(ch("{0}/rx"))*sin(ch("{0}/rz"))))+(ch("{0}/sz")*(cos(ch("{0}/rx"))*sin(ch("{0}/ry"))*cos(ch("{0}/rz"))))'.format(geo.path()))
    blocker_node.parm('geometry_matrix10').setExpression(
        '(-ch("{0}/sz")*(sin(ch("{0}/rx"))*cos(ch("{0}/rz"))))+(ch("{0}/sz")*(cos(ch("{0}/rx"))*sin(ch("{0}/ry"))*sin(ch("{0}/rz"))))'.format(geo.path()))
    blocker_node.parm('geometry_matrix11').setExpression(
        'ch("{0}/sz")*(cos(ch("{0}/rx"))*cos(ch("{0}/ry")))'.format(geo.path()))
    blocker_node.parm('geometry_matrix13').setExpression('ch("{0}/tx")'.format(geo.path()))
    blocker_node.parm('geometry_matrix14').setExpression('ch("{0}/ty")'.format(geo.path()))
    blocker_node.parm('geometry_matrix15').setExpression('ch("{0}/tz")'.format(geo.path()))


def display_message(message):
    """
    An information dialog popup.
    :param message: text message
    :return: None
    """
    hou.ui.displayMessage(message)


def list_filter(list_items, filter_lineedit, ui_list_widget):
    """
    Filter out the list widget.
    :param list_items: List items of list widget
    :param filter_lineedit: line edit text to filter list widget items
    :param ui_list_widget: list widget ui object
    :return: None
    """

    filter_list = []

    for name in list_items:
        if filter_lineedit.text() in name:
            filter_list.append(name)

    ui_list_widget.clear()

    if ui_list_widget:
        for item in filter_list:
            ui_list_widget.addItem(item)