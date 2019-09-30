import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import tempfile

import numpy as np

import SimpleITK as sitk

#
# NiftiLoaderModule
#

class NiftiLoaderModule(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "NiftiLoaderModule" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Nifti Loader"]
    self.parent.dependencies = []
    self.parent.contributors = ["Phillip Chlap (University of New South Wales)"]
    self.parent.helpText = """
A simple module to assist with loading segmentations from Nifit files.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
Phillip Chlap, University of New South Wales, Sydney, Australia
"""

#
# NiftiLoaderModuleWidget
#

class NiftiLoaderModuleWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    self.loadDirectoryButton = qt.QPushButton("Load Directory...")
    self.loadDirectoryButton.toolTip = "Load all Nifti files found in a directory."
    self.loadDirectoryButton.enabled = True
    self.layout.addWidget(self.loadDirectoryButton)

    # connections
    self.loadDirectoryButton.connect('clicked(bool)', self.loadDirectoryButtonClicked)

    # Add vertical spacer
    self.layout.addStretch(1)

  def cleanup(self):
    pass

  def loadDirectoryButtonClicked(self):

    file_chooser = ctk.ctkFileDialog()
    directory = str(file_chooser.getExistingDirectory())

    if len(directory) == 0:
      # Cancelled
      return

    logic = NiftiLoaderModuleLogic()
    logic.run(directory)

#
# NiftiLoaderModuleLogic
#

class NiftiLoaderModuleLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self, directory):
    """
    Run the actual algorithm
    """

    files = os.listdir(directory)

    structures = []
    structure_names = []

    total_files = len(files)

    for f in files:

        full_file = os.path.join(directory, f)

        im = sitk.ReadImage(full_file)

        if im.GetPixelID() == 1:
            # Load as structure
            structures.append(im)
            structure_names.append(f.split(".")[0])
        else:
            # Load as volume
            print("Loading {0}".format(full_file))
            slicer.util.loadVolume(full_file)

    
    # Now save all structures as tmp nrrd file so that we can load that in
    if len(structures) > 0:
      all_arr = None
      for s in structures:
          arr = sitk.GetArrayFromImage(s)
          arr = arr[:,:,:,np.newaxis]

          if type(all_arr) == np.ndarray:
              all_arr = np.concatenate((all_arr, arr), axis=3)
          else:
              all_arr = arr

      struct_im = sitk.GetImageFromArray(all_arr)
      struct_im.SetSpacing(s.GetSpacing())
      struct_im.SetOrigin(s.GetOrigin())
      struct_im.SetDirection(s.GetDirection())

      structure_count = 0
      for name in structure_names:
          struct_im.SetMetaData("Segment{0}_Name".format(structure_count), name)
          structure_count += 1

      tmp = tempfile.mkdtemp()
      tmp_file = os.path.join(tmp, "Structures.nrrd")
      sitk.WriteImage(struct_im, tmp_file)

      slicer.util.loadSegmentation(tmp_file)

      os.remove(tmp_file)

    logging.info('Processing completed')

    return True


class NiftiLoaderModuleTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_NiftiLoaderModule1()

  def test_NiftiLoaderModule1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    # TODO: Make some Nifti data available and download for test
