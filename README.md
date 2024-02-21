# ADCS GUI
Graphical user interface for the ADCS system developed by students at Faculty of Electrical Engineering and Computing, University of Zagreb.



## Installation
run the following command in the root directory of the project
```bash
pip install -r requirements.txt
```

## Usage
run the following command in the root directory of the project
```bash
python main.py
```

connect the GUI to your ADCS over bluetooth. Refresh COM ports and select your correction. Enter the correct settings and open the port.
Now the GUI is connected to your ADCS.

### Linux

If you are using Linux, you need to create a rfcomm device to connect to your ADCS.
this can be done by following these steps:

1. Turn on your bluetooth and pair with your ADCS
2. Find the MAC address of your ADCS by running the following command

```bash
hcitool scan
```

3. Create a rfcomm device by running the following command

```bash
sudo rfcomm bind 0 <MAC address of your ADCS>
```

*`bind 0` refers to device number 0 (rfcomm0) and 1 is the channel*

4. You can now connect to your ADCS using the rfcomm device in the GUI

## Glosary
* **ADCS** - Attitude Determination and Control System
* **GUI** - Graphical User Interface

## Project structure
* **main.py** - main file of the project
* **/core** - utilities and functions that are not directly related to GUI
* **/modules** - modules of the GUI. A module is a collection of multiple widgets.
* **/tabs** - Tabs of the GUI.
* **/validators** - Validators for input fields of the GUI.
* **/widgets** - Custom widgets of the GUI.

## Contributors and Acknowledgment
* [doc. dr. sc. Josip Lončar](https://www.fer.unizg.hr/josip.loncar) - Mentor
* [Neven Lukić](https://github.com/Cyber3x) - Main developer


## License
[MIT](https://choosealicense.com/licenses/mit/)