vtk_module(vtkIOFFMPEG
  TEST_DEPENDS
    vtkTestingCore
    vtkImagingSources
  KIT
    vtkIO
  DEPENDS
    vtkIOMovie
  PRIVATE_DEPENDS
    vtkCommonCore
    vtkCommonDataModel
    vtkCommonMisc
  )