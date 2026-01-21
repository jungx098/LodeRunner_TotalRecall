# Node

## Setup and Run with npm

1. **Initialize the project**: Run `npm init -y` to create a `package.json` file with default settings (skip this step if `package.json` already exists)
2. **Install Electron**: Install Electron as a development dependency with `npm install --save-dev electron`
3. **Start the application**: Execute `npm run start` to launch the project (requires a `start` script in `package.json`)

### Example Script

```sh
 npm init -y
 npm install --save-dev electron
 npm run start
 ```

# Standalone Package

## Building a Standalone Package with Electron

To build a standalone package for the Electron application, follow these steps:

### Prerequisites
- Ensure you have Node.js and npm installed
- Install Electron and electron-builder in your project:
    ```sh
    npm install --save-dev electron electron-builder
    ```

### Building the Package
- For current platform: `npm run dist`
- For Windows: `npm run distwin` (produces .exe installer)
- For Windows unpacked: `npm run pack`

### Output
The built packages will be available in the `dist` folder with installers ready for distribution.

### Example Script

```sh
npm init -y
npm install --save-dev electron-builder
npm run dist
```

## Running with Python HTTP Server

To run this application using Python's built-in HTTP server:

### Python 3.x (Recommended)

 ```sh
 python -m http.server 8000
 ```

