# ALULA - Accessible Learning Ultralight Layout Assistant

**Version:** 0.19  
**Author:** Keith F. - Ultralight Airplane Workshop  
**Date:** 2025-07-01

![Screenshot 2025-06-21 195830](https://github.com/user-attachments/assets/93d363a7-4159-4f64-bd96-ac8d59a92e1c)

## Description
>**alula**
>[**al**-yuh-luh] noun - _plural alulae_ <br>
>_: "a specialized structure of the upper leading edge of a bird's wing that consists of a tuft of short, stiff flight feathers attached to the movable first wing digit corresponding to the thumb and that facilitates flight, landing, and maneuverability at slow speeds : bastard wing"_ - “Alula.” Merriam-Webster.com Dictionary, Merriam-Webster, https://www.merriam-webster.com/dictionary/alula. Accessed 24 Jun. 2025.

ALULA (Accessible Learning Ultralight Layout Assistant) is a simple, offline desktop tool for the preliminary design and analysis of single-seat ultralight aircraft. It is intended to help hobbyists and amateur builders explore design concepts while considering the rules of FAA FAR Part 103.

The application provides real-time estimates for performance, weight & balance, and stability for several vehicle categories:

*   Fixed-Wing & Gliders
*   Gyrocopters & Helicopters
*   Lighter-Than-Air vehicles
*   Paragliders

## Features

*   **Compliancy Checks:** Calculated values for empty weight, stall speed, and maximum level speed are color-coded to indicate compliance with FAR Part 103 limits.
*   **Weight & Balance:** Calculates total empty weight and center of gravity based on a list of components and their locations.
*   **Performance Estimation:** Provides key metrics such as stall speed, rate of climb, Vh (max level speed), and L/D ratio based on user inputs.
*   **Visual Analysis:** Includes a basic side-view CG diagram, a flight envelope (V-g diagram), and a weight fraction pie chart.
*   **Save/Load Functionality:** Designs can be saved to and loaded from simple `.json` files.
*   **Self-Contained:** The program runs as a single script and uses Python's built-in Tkinter library, requiring no external dependencies.

## How to Run

1.  Make sure you have Python 3 installed on your system.
2.  Download the `ALULA.py` file.
3.  Run the file from your terminal:
    ```bash
    python ALULA.py
    ```
    Alternatively, you may be able to run it by double-clicking the file, depending on your system's configuration.

## Usage

1.  Start by selecting a `Vehicle Type` on the "Configuration" tab. The available input fields in other tabs will update automatically.
2.  Fill in the parameters for your design across the "Sizing," "Weights," and "Aerodynamics" tabs.
3.  Click the **Calculate Design** button in the right-hand panel.
4.  The results will be displayed in the right-hand panel and the graphs will update.
5.  The "Issues & Feedback" tab provides text-based notes on your design, highlighting potential stability issues or rule violations.

## Disclaimer
Programmed mainly with Google AI Studio. Use at your own risk! This work is dedicated to the Public Domain. Fly Safe!

## License

This software is released into the **Public Domain**.

You are free to use, modify, and distribute this software for any purpose, commercial or non-commercial, without any restrictions. The author makes no warranties about the software's functionality or the accuracy of its calculations. For more information, please refer to the [Unlicense](http://unlicense.org/).
