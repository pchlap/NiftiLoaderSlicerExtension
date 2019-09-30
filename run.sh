#!/bin/bash

rm -r ../Test/NiftiLoader

"/mnt/c/Program Files/Slicer 4.10.2/bin/PythonSlicer.exe" ../Slicer/Utilities/Scripts/ModuleWizard.py --template ../NiftiLoaderExtension/NiftiLoaderModule --target ../Test/NiftiLoader NiftiLoader

"/mnt/c/Program Files/Slicer 4.10.2/Slicer.exe" --additional-module-paths ../Test/NiftiLoader
