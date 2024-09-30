# 🧬🌐 dt4dds-homepage

- [Overview](#overview)
- [Software Requirements](#software-requirements)
- [Installation Guide](#installation-guide)
- [Usage Guide](#usage-guide)
- [License](#license)

# Overview
This repository contains the homepage for the suite of DT4DDS tools in the following publications:

> Gimpel, A.L., Stark, W.J., Heckel, R., Grass R.N. A digital twin for DNA data storage based on comprehensive quantification of errors and biases. Nat Commun 14, 6026 (2023). https://doi.org/10.1038/s41467-023-41729-1


> Gimpel, A.L., Stark, W.J., Heckel, R., Grass R.N. Challenges for error-correction coding in DNA data storage: photolithographic synthesis and DNA decay. bioRxiv 2024.07.04.602085 (2024). https://doi.org/10.1101/2024.07.04.602085

The hosted version can be found at [dt4dds.ethz.ch](https://dt4dds.ethz.ch).


# Software requirements
The homepage has only been tested on Ubuntu 23.10, using the following packages for Python 3.12:

```
Django==5.0.6
django-widget-tweaks==1.5.0
PyYAML==6.0.1
dt4dds==1.1.0
```


# Installation guide
To clone this repository from Github, use:
```bash
git clone https://github.com/fml-ethz/dt4dds-homepage
cd dt4dds-homepage
```

Initialize and update the submodules for `dt4dds` and `dt4dds-challenges` with:
```bash
git submodule init
git submodule update
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

Finally, collect the static content from the webpage:
```bash
python dt4dds_web/manage.py collectstatic
```


# Usage guide
The homepage is separated into two processes: the webserver `dt4dds-web` and the simulation node `dt4dds-node`. Start these processes with:

```bash
python dt4dds_web/manage.py runserver
python dt4dds_node/main.py
```

You can then navigate to `localhost:8000` to use the homepage locally. A default admin account (username: admin, password: admin) is already created.


# License
This project is licensed under the GPLv3 license, see [here](LICENSE).