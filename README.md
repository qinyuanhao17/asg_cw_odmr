# asg_cw_odmr
1. control_panel.py is the software main file.
2. asg_cw_odmr.ui is the main ui file for this software, and is transformed into asg_cwodmr_ui.py which can be imported into control_panel.py through 'import asg_cw_odmr_ui'.
3. resources.qrc saves images and icons that is used in asg_cw_odmr.ui and is transformed into resources_rc.py to be imported into control_panel.py through 'import resources_rc'.
4. ft1040_SDK.py wraps controlling functions of FT1040 in python.
5. dll_ft1040 folder saves the dynamic link library for smnics FT1040.
6. ASGDLL_x64.dll is the dynamic link library for CIQTEK ASG8005.
