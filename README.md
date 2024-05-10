# network-simulation

## Overview
This network simulation provides a graphical interface for creating, managing, and simulating interactions between servers. It's designed to help users understand concepts like server connectivity and response times through interactive visualization.

## Features

- **Server Creation:** Easily create servers by right-clicking on the graphical interface. A menu will appear, allowing you to name and customize the server.
  
- **Server Configuration:**
  - Right-clicking on a created server provides options like:
    - Adding URLs (sites) to the server.
    - Establishing connections with other servers and specifying response times (weights).
    - Stopping the server to simulate downtime or maintenance.
  
- **Search Functionality:**
  - The main functionality includes conducting searches across servers.
  - The shortest path to the server with the fastest response time is highlighted.

- **Drag and Drop:** Servers can be easily repositioned on the graphical interface by dragging with the mouse.

## Technology
The project is built using pure Python with the Tkinter library for the graphical user interface.
