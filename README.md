# NucleoSite - Nuclear Site Selection Tool

## Project Overview
NucleoSite is a cutting-edge desktop application designed to aid in the selection of optimal sites for nuclear facilities in India. Built with Python and PyQt5, the tool offers interactive geographic visualizations of dam locations, integrating comprehensive data analysis to evaluate dam safety and environmental impacts efficiently.

![NucleoSite Main Interface](optics/main_interface.png)

*The primary interface of NucleoSite displays an interactive map.*


## Key Features
- **Interactive Map Visualization**: Users can navigate through dam locations across different states with options to zoom and access detailed data interactively.

![Data Analysis Interface](optics/dams_India.png)

*Dams in India and potential grid locations for Nuclear Plants*

  
- **Advanced Data Analysis**: Features multiple data layers to evaluate aspects such as seismic risks, population density, and proximity to water sources.

![Data Analysis Interface](optics/buffer_zone.png)

Grid of potential locations within a 10 km buffer zone at a 1 km distance*

- **Dynamic Reporting**: Enables the generation and exportation of detailed PDF reports summarizing user analysis findings.
- **Customizable Search Parameters**: Users can define specific search criteria and thresholds, tailoring the output to particular needs.

![Report Generation Module](optics/report_generation.png)

*Example of a report generation module with output preview.*

## Technologies Used
- **Python**: The core programming language used.
- **PyQt5**: Utilized to create the graphical user interface.
- **Matplotlib & GeoPandas**: For processing and visualizing geospatial data.
- **FPDF**: For generating PDF reports.

## Acknowledgements
- Mentorship provided by Prof. Sushobhan Sen, IIT Gandhinagar.
- Developed by Om Gupta and Nirman Jaiswal.

![Poster](images/Poster_Presentation.jpg)
