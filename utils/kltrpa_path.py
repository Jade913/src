# -*- coding: utf-8 -*-

import os
import sys

run_dir = os.path.dirname(sys.argv[0])
base_dir = os.path.dirname(run_dir)
log_path = os.path.join(base_dir, 'log')
exportdata_path = os.path.join(base_dir, 'export_data')
download_path = os.path.join(exportdata_path, 'resumeRPA-data')
tabledata_path = os.path.join(exportdata_path, 'table-data')
