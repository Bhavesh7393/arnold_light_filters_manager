# arnold_light_filters_manager

Features:
1. List out all the Lights from /obj context, including Subnets.
2. When you select Lights from the list, 3 sections will update and Light Types will be taken into consideration.
   * Available Light Filters list - List of Light Filters which are available in Scene for selected Lights.
   * Active Light Filters list - List of Light Filters which are active on selected Lights.
   * Add Filter drop-down list - A drop-down list to add a Light Filter on selected Light considering selected Light's Type. That means the drop-down list will show Barndoor Filter for a Spot Light, but not for a Point Light.
3. Multi-selection.
   * If you select multiple Lights from the list, it will remember all the Light Types of the selected Lights and list out common Light Filters. For example, let's say you have selected 3 Lights, and one of them is Skydome Light. Since Skydome Light only supports Light Blocker Filter, the Filters list will only show Light Blocker Filters.
   * Just like Lights, you can multi-select Light Filters and do operations, the operation will happen on all selected Lights.
   * Add Filter drop-down list will list out common Light Filters of selected Lights.
4. To avoid any confusion while selecting Light Filters to do the operations, you can either select Available Light Filters items or Active Light Filters items.
5. Light Filters are connected to Lights using the Fetch Node, so you get the same effect in all Lights and have only one Filter node to drive them all. That means you can have one Light Blocker Node connected in multiple Lights just like Maya Arnold.
6. Light Filters generated from the tool will have a prefix "LFM" to differentiate from manually created Light Filters.

Limitations:
1. Might not work on existing user-created Light Filters.
2. If you remove any Light Filter, a Fetch Node will still remain inside the non-selected Lights. The Light Filter won't be functional as its parent node will be deleted but will be listed in the tool.

Document: https://bhavesh7393.artstation.com/pages/houdini-arnold-light-filter-manager

Instructions:
1. Create a New Tool on your Houdini shelf.
2. Paste load_ui.py content in the Script tab.
3. Replace path variable with your current script folder directory and Save.

Creator:
Bhavesh Budhkar
bhaveshbudhkar@yahoo.com
