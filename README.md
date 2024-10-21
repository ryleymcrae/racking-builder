# Racking Builder

The **Racking Builder** is a desktop tool developed in Python 3.10.5 using the [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) UI library. This application helps solar system designers determine the required hardware and optimize rail selections for a defined solar array, minimizing material waste.

The tool allows users to:

- **Select or define a solar panel model:** Choose from a list of predefined solar panel models or manually enter custom specifications.
- **Configure parameters like panel spacing and rail geometry:** Adjust settings like panel spacing and racking geometry, which may vary based on manufacturer specifications or contractor methods.
- **Modify panel and rail data for a customized experience:** Update or add panel and rail information to customize the app.

## Basic Workflow

1. **Select Panel Model:** In the *Inputs* tab, choose a panel model from the dropdown under *Panel Specifications*.
2. **Configure Racking:** Adjust the racking specifications to match the installer's requirements.
3. **Define Rows:** Switch to the *Rows* tab to specify the number of panels and the orientation of each row in the array.
4. **Get Results:** Click *Get Results* at the bottom of the sidebar to view the hardware counts and update the preview pane. Afterward, you can switch to the *Rails* tab for a detailed breakdown of rail selections, cutoff lengths, and the deadload for each row.

## Interpretation of Inputs and Results

### Panel Specifications

Input Label | Type | Units | Description
------------|------|-------|------------
**Panel model** | Dropdown | 
**Panel width** | User-defined | 
**Panel height** | User-defined | 
**Panel weight** | User-defined | 

### Racking Specifications

Input Label | Type | Units | Description
------------|------|-------|------------
**Pattern** | Dropdown | 
**Rafter spacing** | Dropdown | 
**Panel spacing** | 
**Bracket inset** | 
**Rail protrusion** | 
**Portrait rail inset** | 
**Landscape rail inset** | 
**Truss structure** | 

## User Interface

<p align="center">
    <img src="images/default_screen.png" style="width:800px">
    <br>
    Default Interface Displayed on Startup
</p>

<p align="center">
    <img src="images/rows_screen.png" style="width:800px">
    <br>
    Defining the Array Rows
</p>

<p align="center">
    <img src="images/hardware_screen.png" style="width:800px">
    <br>
    Hardware Count Summary
</p>

<p align="center">
    <img src="images/rails_screen.png" style="width:800px">
    <br>
    Detailed Breakdown of Row Information
</p>

<p align="center">
    <img src="images/data_screen.png" style="width:800px">
    <br>
    Editing Application Data
</p>
