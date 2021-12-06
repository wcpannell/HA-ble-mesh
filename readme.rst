========
ble_mesh
========

A custom Bluetooth Mesh integration for home assitant. ble_mesh is a quick and dirty integration that adds support for a custom Bluetooth Mesh Gateway Node supporting a Sensor Client. This probably will never be mainlined unless I add a wide variety of Bluetooth Mesh Servers and Clients.

Installation
------------

On a Home-Assistant Operating-System installation you will need to first enable advanced mode for your user. Then install the SSH add-in. Next, either load the Web-UI shell, or ssh into the server.

On any mode of installation the next step is to create a custom_components directory in the config directory and clone this repository there. Reboot the server so it can discover the new integration. Once it is back up click Configuration, Integrations, Add Integration, and search or select the "BLE Mesh Environmental Sensing" Integration. A window will the pop open offering all relevant USB devices found by Home-Assistant. Choose the desired device (typ. /dev/tty/ACMn) and click submit. A sucess message should be posted. Return to the Dashboard overview and enjoy your new sensors.

.. code-block:: bash

   mkdir -p config/custom_components
   cd config/custom_components
   git clone https://github.com/wcpannell/HA-ble-mesh.git ble_mesh

Features
--------

- Communicates with `mesh-gateway-node <https://github.com/wcpannell/mesh-gateway-node>`_
- Integration Polls for new serial messages
- Config Flow to pass in USB-to-serial device (No config files)

TODO
----

- Build into local_push iot_class for asynchronous updates.
- Add more configuration instead of hardcoding sensor names and types.
- More documentation is always better.
