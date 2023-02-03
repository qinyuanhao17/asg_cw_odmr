# CW-ODMR Automation ![repoSize](https://img.shields.io/github/repo-size/qinyuanhao17/asg_cw_odmr?logo=Github) ![img](https://img.shields.io/github/license/qinyuanhao17/asg_cw_odmr) ![img](https://img.shields.io/github/contributors/qinyuanhao17/asg_cw_odmr)

This application is designed, not restricted, to do Continues Wave Optically Detected Magnetic Resonance (CW-ODMR) measurements for color centers like $\rm NV$, $\rm V_{Si}$, $\rm V_{Si}V_{C}$ and etc.

## Features

- A single photon detector module based on **Simnics FT1040**.
- A **RIGOL DSG836** RF generator contol module.
- A data processing module dealing and visualizing measured data.
- A RF sweep list generator code in Jupyter Notebook to generate a random sweep list, in order to avoid MW frequency mitigating problems caused by frequency-dependent MW heating through the antenna resonance

## Composition

* control_panel.py is the software main file.
* asg_cw_odmr.ui is the main ui file for this software, and is transformed into asg_cwodmr_ui.py which can be imported into control_panel.py through 'import asg_cw_odmr_ui'.
* resources.qrc saves images and icons that is used in asg_cw_odmr.ui and is transformed into resources_rc.py to be imported into control_panel.py through 'import resources_rc'.
* ft1040_SDK.py wraps controlling functions of FT1040 in python.
* dll_ft1040 folder saves the dynamic link library for smnics FT1040.
* ASGDLL_x64.dll is the dynamic link library for CIQTEK ASG8005.

# Liscence

All parts of this repository is under GPL3 (see LICENSE)
