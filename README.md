# VNSS Project README

This README file provides instructions for setting up and running the VNSS project using Python 3.12 and a SQL database.

## Prerequisites

- Python 3.12 installed on your system [Download](https://www.python.org/downloads/)
- SQL database server - MySQL [Download](https://dev.mysql.com/downloads/installer/)

## Setup
- Check python installation 
```bash
python --version
```
Or
```bash
python3 --version
```
Or
```bash
py --version
```

It should return something like this.
```
Python 3.12.1
```
### 1. Create a Virtual Environment

To create and activate a virtual environment named "vnss", follow these steps:
   ```python 
   python -m venv vnss
```
If 'python' doesn't work than use py or python3

```python 
.\vnss\Scripts\activate
```

### 2. Install Dependencies

With the virtual environment activated, install the required packages:
```python 
pip install -r requirements.txt
```
- There is a file called requirements.txt use that to install all the dependencies requred for the project.
### 3. Configure the SQL Database

Install MySQL installer using default settings.

## Docker setup(Optional)
- # Installing Docker on Windows
=====================================================

## Prerequisites
---------------

1. **Windows Version**: Ensure you are using Windows 10 Pro, Enterprise, or Education (64-bit).
2. **CPU Virtualization**: Enable CPU virtualization in your BIOS settings.

## Installation Steps
--------------------

1. **Download Docker Desktop**:
   - Visit the official Docker Hub website and download Docker Desktop for Windows.
   - [Docker Desktop Download](https://www.docker.com/products/docker-desktop)

2. **Run the Installer**:
   - Once downloaded, run the installer and follow the on-screen instructions.

3. **Restart Your Computer**:
   - After installation, restart your computer to ensure all changes take effect.

4. **Verify Docker Installation**:
   - Once restarted, Docker Desktop should start automatically.
   - To check the version in terminal or cmd.

   ```bash
   docker version
   ```

   It should return with all the information related to docker.


