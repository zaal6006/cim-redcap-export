# cim-redcap-export
## RedCap to CIM files export and process CGP

To Enable CSV Files export from RED Cap system then process split and save to CIM shared folder
Project structure:
  
cim-redcap-export/  
|-  
|-- main.py                  # Application entry point  
|-- config.py                # Reads environment variables  
|-- redcap_client.py         # REDCap API communication  
|-- logger.py                # Logging configuration  
|-- requirements.txt  
|-- README.md  
|-- .env.example             # Example environment variables (no secrets)  
|-- .gitignore  
|  
|-- output/                  # Temporary output (raw CSV)  
  
|-- logs/  
|  
|-- tests/  
  
# updated project structure   
### cim-redcap-export/  
  
│  
├── main.py                <- application entry point  
├── config.py              <- configuration  
├── logger.py              <- logging  
├── redcap_client.py       <- REDCap communication  
├── csv_processor.py        <- split CSV into Patient/Study  
├── exporter.py            <- copy files to network share  
│  
├── output/  
├── logs/  
└── tests/  
