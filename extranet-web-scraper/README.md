# Extranet Web Scraper

This project is a web scraper for the Extranet website ([https://www.sa.mcss.gov.on.ca/](https://www.sa.mcss.gov.on.ca/)). It downloads files from the website and saves them into their respective folders. The data collected will be used to train a proof of concept (POC) chatbot for Extranet.

## Prerequisites

- Python 3.11.X
- Virtual environment (venv)
- `requirements.txt` file for package dependencies

## Setting Up the Environment

### Windows

1. **Create a virtual environment:**

   ```sh
   python -m venv env
   ```

2. **Activate the virtual environment:**

   ```sh
   source ./env/Scripts/activate
   ```

### MacOS

1. **Create a virtual environment:**

   ```sh
   python3 -m venv env
   ```

2. **Activate the virtual environment:**

   ```sh
   source ./env/bin/activate
   ```

## Installing Dependencies

After activating the virtual environment, install the necessary packages using the `requirements.txt` file:

```sh
pip install -r requirements.txt
```

## Updating `requirements.txt`

If you install a new package and want to update the `requirements.txt` file, run:

```sh
pip freeze > requirements.txt
```

## Setting Environment Variables

Before running the scraper, you need to set the `PASSWORD` environment variable:

### Create the `PASSWORD` Environment Variable with Extranet Password

```sh
export PASSWORD='<password>'
```

## Running the Scraper

The main file for the scraper is `scrapeAllWebsite.py`. To run the scraper, use the following command:

```sh
python scrapeAllWebsite.py
```
