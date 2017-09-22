# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 14:01:23 2015

@author: dreadnought

"Brevity required, prurience preferred"
"""


import os, errno
import copy
import json
import numpy as np
# what the hell is this?
# hangs on my mac at this import line
# no idea what the fuck is going on here.
# import matplotlib.pylab as plt
from . import cosmics_hsg as cosmics
import scipy.ndimage as ndimage
import pyqtgraph as pg
# from UIs.ImageViewWithPlotItemContainer import ImageViewWithPlotItemContainer

import logging
log = logging.getLogger("EMCCD")


class ConsecutiveImageAnalyzer(object):
    def __init__(self):
        """
        This class will function to hold and control
        all things necessary for performing statistical
        metrics for consecutive, identical situation
        CCD exposures. Namely, this is the raw
        camera image, and the normalization factor
        which may change between images (i.e. FEL pulses)
        :return:
        """
        self._rawImages = []
        self._cleanImages = None
        self._normFactors = []
        # how memory inefficient is it to
        # keep a cache of it?
        self._stackedImages = None

        # parameters for the crr algorithm
        self.crrParams = {
            "ratio": 1.0,
            "noisecoeff":5.0
        }

        # Set to True to to not normalize the
        # images when doing crr
        self.ignoreNormFactors = False

    def addImage(self, image, normFactor = None):
        if isinstance(image, EMCCD_image):
            if self._rawImages and image.raw_array.shape != self._rawImages[0].shape:
                raise ValueError("Input dimensions must match!\n\t got: {}, want: {}".format(
                    image.raw_array.shape, self._rawImages[0].shape
                ))
            self._rawImages.append(image.raw_array)
            if normFactor is None:
                felp = image.equipment_dict.get("fel_pulses", 0)
                # print "from eqp dict", felp
                if felp == 0: felp = 1
            else:
                felp = normFactor
            # print "Added an image, norm factor", felp
            self._normFactors.append(felp)
        else:
            if self._rawImages and image.shape != self._rawImages[0].shape:
                raise ValueError("Input dimensions must match!\n\t got: {}, want: {}".format(
                    image.raw_array.shape, self._rawImages[0].shape
                ))
            if normFactor is None: normFactor = 1
            self._rawImages.append(image)
            self._normFactors.append(normFactor)

        self._stackedImages = None

    def removeImageByIdx(self, index):
        try:
            self._rawImages.pop(index)
            self._normFactors.pop(index)
            self._stackedImages = None
        except Exception as e:
            log.warning("Error trying to pop the images, {}".format(e))

    def removeCosmics(self, ratio = 1.0, noisecoeff = 5.0, debug = False):
        if self._stackedImages is None:
            self.getImages()
        d = np.array(self._stackedImages).astype(float)

        normFactors = np.array(self._normFactors)
        if not self.ignoreNormFactors:
            try:
                d /= normFactors[:,None, None]
            except:
                print("error here")
                print(type(d), d)
                print(type(normFactors), normFactors)
                raise


        med = np.median(d, axis=0)
        # estimate the noise by taking the std along the first
        # 100px of each row, for each vertical pixel.
        # Then just average those, as the noise should be roughly
        # consant, and that will hopefully smear out the presence of
        # sidebands or cosmics within the first 100px?

        signoise = np.std(d[:,:,:100], axis=2).mean()
        cutoff = med * ratio + noisecoeff * signoise

        # if debug:
        #     try:
        #         if d.shape[1]>10:
        #             debug = False
        #             raise RuntimeError("Sorry, can't debug with this large"
        #                                "an image, it causes things to break")
        #         print "median shape", med.shape
        #         cutoff = med * ratio + noisecoeff * np.std(med[:,:100])
        #         print "cutoff shape", cutoff.shape
        #
        #         winlist = []
        #
        #         vw = ImageViewWithPlotItemContainer(view=pg.PlotItem())
        #         vw.view.setAspectLocked(False)
        #         vw.setImage(d.copy())
        #         vw.setWindowTitle("Raw Image")
        #         vw.roi.setSize((d.shape[2], d.shape[1]))
        #         vw.roi.translatable = False
        #         vw.ui.roiPlot.plotItem.addLegend()
        #         for ii in range(0, d.shape[0]):
        #             for kk in range(0, d.shape[1]):
        #                 vw.ui.roiPlot.plot(d[ii,kk], pen=pg.mkPen((ii, d.shape[0]), style=kk+1), name=ii)
        #         # vw.updateImage()
        #
        #         vw.show()
        #         vw.ui.roiBtn.setChecked(True)
        #         vw.ui.roiBtn.clicked.emit(True)
        #         winlist.append(vw)
        #         vw = ImageViewWithPlotItemContainer(view=pg.PlotItem())
        #         vw.view.setAspectLocked(False)
        #         # vw.setImage(d.reshape(d.shape[2], d.shape[1], d.shape[0]))
        #         vw.setImage(med)
        #         vw.setWindowTitle("Median Image")
        #         vw.roi.setSize((med.shape[1], med.shape[0]))
        #         vw.roi.translatable = False
        #         vw.ui.roiPlot.plotItem.addLegend()
        #         for ii in range(0, med.shape[0]):
        #                 vw.ui.roiPlot.plot(med[ii], pen=pg.mkPen(style=ii+1), name=ii)
        #         # vw.updateImage()
        #
        #         vw.show()
        #         vw.ui.roiBtn.setChecked(True)
        #         vw.ui.roiBtn.clicked.emit(True)
        #         winlist.append(vw)
        #
        #
        #         vw = ImageViewWithPlotItemContainer(view=pg.PlotItem())
        #         vw.view.setAspectLocked(False)
        #         # vw.setImage(d.reshape(d.shape[2], d.shape[1], d.shape[0]))
        #         vw.setImage(d-med)
        #         vw.setWindowTitle("d-m")
        #         vw.roi.setSize((med.shape[1], med.shape[0]))
        #         vw.roi.translatable = False
        #         vw.ui.roiPlot.plotItem.addLegend()
        #         for ii in range(0, d.shape[0]):
        #             for kk in range(0, d.shape[1]):
        #                 vw.ui.roiPlot.plot(d[ii,kk]-med[kk], pen=pg.mkPen((ii, d.shape[0]), style=kk+1), name=ii)
        #         for ii in range(0, med.shape[0]):
        #                 vw.ui.roiPlot.plot(cutoff[ii], pen=pg.mkPen(style=ii+1), name=ii)
        #         # vw.updateImage()
        #
        #         vw.show()
        #         vw.ui.roiBtn.setChecked(True)
        #         vw.ui.roiBtn.clicked.emit(True)
        #         winlist.append(vw)
        #
        #
        #         vw = ImageViewWithPlotItemContainer(view=pg.PlotItem())
        #         vw.view.setAspectLocked(False)
        #         # vw.setImage(d.reshape(d.shape[2], d.shape[1], d.shape[0]))
        #         vw.setImage((d-med)>cutoff[None,:,:])
        #         vw.setWindowTitle("Cosmics?")
        #         vw.roi.setSize((d.shape[2], d.shape[1]))
        #         vw.roi.translatable = False
        #         vw.ui.roiPlot.plotItem.addLegend()
        #         for ii in range(0, d.shape[0]):
        #             for kk in range(0, d.shape[1]):
        #                 vw.ui.roiPlot.plot(((d-med)>cutoff[None,:,:])[ii,kk], pen=pg.mkPen((ii, d.shape[0]), style=kk+1), name=ii)
        #         # vw.updateImage()
        #
        #         vw.show()
        #         vw.ui.roiBtn.setChecked(True)
        #         vw.ui.roiBtn.clicked.emit(True)
        #         winlist.append(vw)
        #
        #     except:
        #         log.exception("this failed")



        badPix = np.where((d-med)>cutoff[None,:,:])
        d[badPix] = np.nan
        if not self.ignoreNormFactors:
            d *= normFactors[:,None, None]

        # To be comprable to background
        std = np.nanstd(d, axis=0)

        # if not self.ignoreNormFactors:
        #     d /= normFactors[:,None, None]

        # d[badPix] = np.nanmean(d[:, badPix[1], badPix[2]], axis=0)
        # if not self.ignoreNormFactors:
        #     d *= normFactors[:,None, None]

        # replace the cosmics
        d[badPix] = np.nanmean(d[:, badPix[1], badPix[2]], axis=0)
        self._cleanImages = np.array(d)

        if debug:

                vw = ImageViewWithPlotItemContainer(view=pg.PlotItem())
                vw.view.setAspectLocked(False)
                vw.setImage(self._cleanImages.copy())
                vw.setWindowTitle("Clean Image")
                vw.roi.setSize((d.shape[2], d.shape[1]))
                vw.roi.translatable = False
                vw.ui.roiPlot.plotItem.addLegend()
                for ii in range(0, d.shape[0]):
                    for kk in range(0, d.shape[1]):
                        vw.ui.roiPlot.plot(d[ii,kk], pen=pg.mkPen((ii, d.shape[0]), style=kk+1), name=ii)
                # vw.updateImage()

                vw.show()
                vw.ui.roiBtn.setChecked(True)
                vw.ui.roiBtn.clicked.emit(True)
                winlist.append(vw)
                self.winList = winlist




        d = np.nanmean(d, axis=0).astype(int)

        return d, std

    def subtractImage(self, other):
        """

        :param other:
        :type other: ConsecutiveImageAnalyzer
        :return:
        """
        back = np.mean(other.getImages().astype(float), axis=0)
        sigb = np.std(other.getImages(), axis=0)
        normfact = np.array(self._normFactors)

        img = np.array(self.getImages()).astype(float)
        sigim = np.std(img, axis=0)
        sigT = np.sqrt(sigb**2 + sigim**2)

        img -= back[None, :, :]
        if not self.ignoreNormFactors:
            img /= normfact[:, None, None]
            sigT /= np.sum(normfact)

        sigpost = np.std(img, axis=0)
        sigpost /= np.sqrt(img.shape[0])
        sigT /= np.sqrt(img.shape[0])

        return np.mean(img, axis=0), sigpost, sigT


    def clearImages(self):
        self._rawImages = []
        self._cleanImages = None
        self._normFactors = []
        self._stackedImages = None

    def getImages(self):
        # prefer returning the clean stuff, I think this is
        # what you'd always want
        if self._cleanImages is not None:
            return self._cleanImages.copy()
        if self._stackedImages is not None:
            return self._stackedImages
        elif not self._rawImages:
            return np.zeros((10, 10, 10)) - 1
        self._stackedImages = np.array(self._rawImages[0])[None,:,:]

        if len(self._rawImages)==1:
            return self._stackedImages

        for newImage in self._rawImages[1:]:
            self._stackedImages = np.concatenate(
                (self._stackedImages, newImage[None,:,:]), axis=0
            )
        return self._stackedImages
    def numImages(self):
        return len(self._rawImages)


class EMCCD_image(object):
    origin_import = '\nWavelength,Signal\nnm,arb. u.'
    
    def __init__(self, raw_array=[], file_name='', file_no=None, description='', equipment_dict={}):
        """
        This init is to work with the most basic images with no specialiation
        for HSG or PL or absorbance data.  Feels like we should have something
        more general than those.
        
        raw_array = the CCD image with the pertinent data
        bg_array = the CCD image with the pertinent backgroud data
        description = string that contains a brief description of the file
        equipment_dict = dictionary that contains the important settings of the
                         equipment:
                             CCD_temperature = temp of CCD chip
                             exposure = exposure time
                             gain = EM gaine
                             y_min = lower boundary of ROI
                             y_max = upper boundary of ROI
                             grating = spectrometer grating
                             center_lambda = spectrometer wavelength setting
                             slits = width of slits in microns
                             dark_region (maybe not that useful if can look at y_max + n) 
                             bg_file_name = name of background file
							 series = name for series
        """
        self.raw_array = np.array(raw_array)
        self.raw_shape = self.raw_array.shape
        self.file_name = file_name
        self.saveFileName = '' # where were you actually saved?
        self.file_no = file_no
        self.description = description
        self.equipment_dict = equipment_dict
        if self.equipment_dict and self.equipment_dict.get('y_max', 0) - self.equipment_dict.get('y_min', 0) > int(self.raw_shape[0]):
            log.warning("y_min and y_max were set incorrectly")
            self.equipment_dict['y_max'] = int(self.raw_shape[0])
            self.equipment_dict['y_min'] = 0
        self.clean_array = None
        self.std_array = None # for holding the std of pixels
        self.spectrum = None
        self.addenda = [0, file_name + str(file_no)] # This is important for keeping track of addition and subtraction
        self.subtrahenda = []
        self.equipment_dict["background_darkcount_std"] = -1
        self.equipment_dict["background_file"] = ''

        self.imageSequence = ConsecutiveImageAnalyzer()

        self.isSequence = False

    def __str__(self):
        '''
        This will print the description of the file.  I'm not sure what else
        would be useful at this time.
        '''
        return self.description
    
    def __add__(self, other):
        '''
        This will copy the first element in the sum, then add the clean_arrays
        from self and other to each other.  It can also currently add an int or
        float to the clean_array.  I'm not sure if that kind of addition is 
        useful.
        
        The center_lambda check needs to be changed to match how that 
        dictionary entry works.  It could get ugly without double checking.
        '''
        if self.clean_array is None:
            raise Exception('Source: EMCCD_image.__add__\nThe first array has not been cleaned yet')
            log.error("Unable to add: First array not cleaned")
        ret = copy.deepcopy(self)
        
        # Add a constant offset to the data
        if type(other) in (int, float):
            ret.clean_array = self.clean_array + other
            ret.addenda[0] = ret.addenda[0] + other
        
        # or add the two clean_arrays together
        else:
            if np.isclose(ret.equipment_dict['center_lambda'], 
                          other.equipment_dict['center_lambda']):
                ret.clean_array = self.clean_array + other.clean_array
                ret.addenda[0] = ret.addenda[0] + other.addenda[0]
                ret.addenda.extend(other.addenda[1:])
                ret.subtrahenda.extend(other.subtrahenda)
            else:
                print("self:{}, ret:{}, other:{}".format(
                    self.equipment_dict['center_lambda'],
                    ret.equipment_dict['center_lambda'],
                    other.equipment_dict['center_lambda']
                ))
                # raise Exception('Source: EMCCD_image.__add__\nThese are not from the same grating settings')
                log.error("Unable to add, data not from same grating settings")
        return ret

    def __sub__(self, other):
        '''
        This subtracts constants or other data sets between self.hsg_data.  I 
        think it even keeps track of what data sets are in the file and how 
        they got there.  
        
        The center_lambda check needs to be changed to match how that 
        dictionary entry works.  It could get ugly without double checking.
        '''
        if self.clean_array is None:
            raise Exception('Source: EMCCD_image.__sub__\nThe first array has not been cleaned yet')
        ret = copy.deepcopy(self)
        
        if type(other) in (int, float):
            ret.clean_array = self.clean_array - other
            ret.addenda[0] = ret.addenda[0] - other
        else:
            if np.isclose(ret.equipment_dict['center_lambda'], 
                          other.equipment_dict['center_lambda']):
                ret.clean_array = self.clean_array - other.clean_array
                ret.addenda[0] = ret.addenda[0] - other.addenda[0]
                ret.subtrahenda.extend(other.addenda[1:])
                ret.addenda.extend(other.subtrahenda)


            else:
                raise Exception('Source: EMCCD_image.__sub__\nThese are not from the same grating settings')
        return ret
        
    def __getslice__(self, *args):
        print('getslice ', args)
        #Simply pass the slice along to the data
        return self.spectrum[args[0]:args[1]]
        
    def __iter__(self):
        for i in range(len(self.spectrum)):
            yield self.spectrum[i]
        return
    
    def set_ylimits(self, y_min, y_max):
        '''
        This changes y_min and y_max
        '''
        self.equipment_dict['y_min'] = y_min
        self.equipment_dict['y_max'] = y_max
    
    def cosmic_ray_removal(self, mygain=10, myreadnoise=0.2, mysigclip=5.0, mysigfrac=0.01, myobjlim=3.0, myverbose=True):
        '''
        This is a single operation of cosmic ray removal.

        If EMCCD isn't cold enough, the hot pixels wil be removed as well.  I 
        don't know if this is a bad thing?  I think it should just be a thing
        that doesn't happen.
        
        mygain = the gain.  This does not seem to actually be the EM gain of 
                 the EMCCD
        myreadnoise = Level (imprecise!) of read noise used in the statistical
                      model built to recognize cosmic arrays.  It's a function
                      of gain on our CCD, I believe.  Dark current should be 
                      separate, technically, but it would look like noise 
                      because of shot noise and crap
        mysigclip = I forget
        mysicfrac = I forget
        myobjlim = I forget
        myverbose = Tells hsg_cosmics to print out what it's doing
        
        returns a clean my_array
        '''
        
#        self.clean_array = self.raw_array
#        return
        image_removal = cosmics.cosmicsimage(self.raw_array, gain=mygain, # I don't understand gain
                                             readnoise=myreadnoise, 
                                             sigclip=mysigclip, 
                                             sigfrac=mysigfrac, 
                                             objlim=myobjlim)
        image_removal.run(maxiter=4)
        self.clean_array = image_removal.cleanarray
    
    def make_spectrum(self, std = None):
        '''
        Integrates over vertical axis of the cleaned image
        
        I'm not exactly sure y_min and y_max are counting from the same side as
        in the UI.
        '''
        if self.std_array is None:
            try:
                self.spectrum = self.clean_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            except:
                self.spectrum = self.raw_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
                                          self.equipment_dict['grating'])
            self.spectrum = np.concatenate((wavelengths, self.spectrum)).reshape(2,1600).T
        else:
            self.spectrum = self.clean_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            spec_std = np.mean(self.std_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:], axis=0)
            wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
                                          self.equipment_dict['grating'])
            self.spectrum = np.concatenate((wavelengths, self.spectrum, spec_std)).reshape(3,1600).T

        # elif isinstance(background, EMCCD_image):
            # self.spectrum = self.clean_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            # self.spectrum -= background.clean_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            #
            # spec_std = np.mean(self.std_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:], axis=0)
            # back_std = np.mean(background.std_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:], axis=0)
            # spec_std = np.sqrt(spec_std**2 + back_std**2)
            #
            #
            # wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
            #                               self.equipment_dict['grating'])
            # self.spectrum = np.concatenate((wavelengths, self.spectrum, spec_std)).reshape(3,1600).T


        # else:
        #     raise RuntimeError("What the fuck are you trying to do? I don't want to handle this right now")

        
    def inspect_dark_regions(self):
        '''
        This will look at a dark area, I'm not quite sure how yet, to make sure
        the mean is set to zero.  It will also measure the standard deviation 
        of the noise for use later.
        '''
        dark_region = self.clean_array[0,:] # This is a total kludge
        self.dark_mean = np.mean(dark_region)
        self.std_dev = np.std(dark_region)
        # print "Base line is ", self.dark_mean
        # print "Standard deviation is ", self.std_dev
        height = self.equipment_dict['y_max'] - self.equipment_dict['y_min']
        if height == self.clean_array.shape[0]:
            log.warn("Integrating full image, cannot do dark count subtraction!")
            return
        self.spectrum[:,1] = self.spectrum[:, 1] - self.dark_mean*height
        self.addenda[0] += self.dark_mean*height
        self.clean_array -= self.dark_mean
    
    def save_spectrum(self, folder_str='Spectrum files', prefix=None, postfix = '', origin_header = None):
        '''
        Saves the general spectrum.  Unsure if we need it, but, again, seems
        useful for novel, basic stuff.
        '''

        self.equipment_dict['addenda'] = self.addenda
        self.equipment_dict['subtrahenda'] = self.subtrahenda
        equipment_str = json.dumps(self.equipment_dict, sort_keys=True)
        if origin_header is None:
            origin_import = self.origin_import
        else:
            origin_import = origin_header

        filename = self.getFileName(prefix)
        filename += postfix


        filename += "_spectrum.txt"
        my_header = '#' + equipment_str + '\n' + '#' + self.description.replace('\n','\n#') + origin_import
        np.savetxt(os.path.join(folder_str, 'Spectra', self.file_name, filename), self.spectrum,
                   delimiter=',', header=my_header, comments = '', fmt='%f')

    def getFileName(self, prefix=None):
        """
        Convenience function to get the name used for saving.
        """
        # All the data will end up doig the same thing,
        # only difference is the preffix to the name (?)
        # which can also be set specifically with the function call
        if prefix is None:
            # Get the name of the class calling it
            name = type(self).__name__.lower()
            if "hsg" in name:
                filename = "hsg_"
            elif "pl" in name:
                filename = "pl_"
            elif "abs" in name:
                filename = "absRaw_"
            else:
                filename = ""
        else:
            filename = str(prefix)


        filename += self.file_name + self.file_no
        return filename
    
    def save_images(self, folder_str='Raw files', prefix=None, data = None,
                    fmt = '%d', postfix = ''):
        '''
        Saves the raw_array, not the cleaned one.  Cleaning isn't that hard, 
        and how we do it could change in the future.
        
        This really depends on how the folders are initialized by the UI.  Will
        they already exist by the time we get to saving images, or do they need
        to be created on the fly?
        
        Also, I'm pretty sure self.raw_array is still ints?
        '''
        self.equipment_dict['addenda'] = self.addenda
        self.equipment_dict['subtrahenda'] = self.subtrahenda
        try:
            equipment_str = json.dumps(self.equipment_dict, sort_keys=True)
        except:
            print("Source: EMCCD_image.save_images\nJSON FAILED")
            print(self.equipment_dict)
            return
        
        my_header = "#" + equipment_str + '\n#' +  self.description.replace('\n','\n#')



        # All the data will end up doig the same thing,
        # only difference is the preffix to the name (?)
        # which can also be set specifically with the function call
        if prefix is None:
            name = type(self).__name__.lower()
            if "hsg" in name:
                filename = "hsg_"
                if "fvb" in name:
                    filename += 'fvb_'
            elif "pl" in name:
                filename = "pl_"
            elif "abs" in name:
                filename = "absRaw_"
            else:
                filename = ""
        else:
            filename = str(prefix)

        if data is None:
            data = self.raw_array


        filename += self.file_name + postfix + self.file_no + '.txt'
        self.saveFileName = filename
        np.savetxt(os.path.join(folder_str, "Images", filename), data,
               delimiter=',', header=my_header, comments = '#', fmt=fmt)
        print("Saved image\nDirectory: {}".format(
            os.path.join(folder_str, "Images", filename)
        ))

    def setAsSequence(self):
        """
        This function is called by the expwidget when this object
        becomes a sequence image. Sets things up to be ready to take multiple
        images. Updates things such as FEL pulses/stats in the equipment dict
        to be lists to append to.
        :return:
        """ 
        self.imageSequence.clearImages()
        self.imageSequence.addImage(self)
        self.isSequence = True
        if "fieldStrength" in self.equipment_dict:
            self.equipment_dict["fieldStrength"] = [
                self.equipment_dict["fieldStrength"]
            ]

            self.equipment_dict["fieldInt"] = [
                self.equipment_dict["fieldInt"]
            ]

            self.equipment_dict["fel_pulses"] = [
                self.equipment_dict["fel_pulses"]
            ]

    def addNewImage(self, newImage):
        """
        This function should be called by an object
        which serves to act as a collection of multiple images.

        This will collect the FEL changes (pulses, strength, etc)
        :param newImage:
        :type newImage: EMCCD_image
        :return:
        """
        if "fieldStrength" in self.equipment_dict:
            self.equipment_dict["fieldStrength"].append(
                newImage.equipment_dict["fieldStrength"]
            )

            self.equipment_dict["fieldInt"].append(
                newImage.equipment_dict["fieldInt"]
            )

            self.equipment_dict["fel_pulses"].append(
                newImage.equipment_dict["fel_pulses"]
            )
        self.imageSequence.addImage(newImage)

    def removeImageBySequence(self, index):
        try:
            if "fieldStrength" in self.equipment_dict:
                self.equipment_dict["fieldStrength"].pop(index)
                self.equipment_dict["fieldInt"].pop(index)
                self.equipment_dict["fel_pulses"].pop(index)
            self.imageSequence.removeImageByIdx(index)
        except Exception as e:
            log.warning("Exception trying to remove an image")




class HSG_image(EMCCD_image):
    '''
    This subclass will specialize in HSG initializing and saving, which mostly
    has to do with what the header in the file is at this point.  
    '''
    pass

class HSG_FVB_image(HSG_image):
    def __init__(self, raw_array=[], file_name='', file_no=None, description='', equipment_dict={}):
        super(HSG_FVB_image, self).__init__(raw_array, file_name, file_no, description, equipment_dict)
        self.isSeries = False

    def cosmic_ray_removal(self, offset = 0, medianRatio = 1, noiseCoeff = 5):
        """
        Remove cosmic rays from the raw_array when it is a sequence
        of consecutive exposures.
        :param offset: baseline to add to raw_array.
               Not used, but here if it's needed in the future
        :param medianRatio: Multiplier to the median when deciding a cutoff
        :param noiseCoeff: Multiplier to the noise on the median
                    May need changing for noisy data
        :return:
        """
        # log.warn("Warning: HSG FVB Cosmic removal not implemented")
        # self.clean_array = self.raw_array

        d = np.array(self.raw_array)
        print(d.shape)

        med = ndimage.filters.median_filter(d, size=(d.shape[0], 1), mode='wrap')
        print(med.shape)
        meanMedian  = med.mean(axis=0)
        print(meanMedian.shape)
        # Construct a cutoff for each pixel. It was kind of guess and
        # check
        cutoff = meanMedian * medianRatio + noiseCoeff * np.std(meanMedian[:100])
        print(cutoff.shape)





        winlist = []

        win = pg.GraphicsLayoutWidget()
        win.setWindowTitle("Raw Image")
        p1 = win.addPlot()

        img = pg.ImageItem()
        img.setImage(d.copy().T)
        p1.addItem(img)

        hist = pg.HistogramLUTItem()
        hist.setImageItem(img)
        win.addItem(hist)

        win.nextRow()
        p2 = win.addPlot(colspan=2)
        p2.plot(np.sum(d, axis=1))
        win.show()
        winlist.append(win)

        win2 = pg.GraphicsLayoutWidget()
        win2.setWindowTitle("Median Image")
        p1 = win2.addPlot()

        img = pg.ImageItem()
        img.setImage(med.T)
        p1.addItem(img)

        hist = pg.HistogramLUTItem()
        hist.setImageItem(img)
        win2.addItem(hist)

        win2.nextRow()
        p2 = win2.addPlot(colspan=2)

        p2.plot(np.sum(med, axis=1)/4)
        win2.show()
        winlist.append(win2)




        win2 = pg.GraphicsLayoutWidget()
        win2.setWindowTitle("d-m")
        p1 = win2.addPlot()

        img = pg.ImageItem()
        img.setImage((d - med).T)
        p1.addItem(img)

        hist = pg.HistogramLUTItem()
        hist.setImageItem(img)
        win2.addItem(hist)

        win2.nextRow()
        p2 = win2.addPlot(colspan=2)

        p2.plot((d - med)[0,:], pen='w')
        p2.plot((d - med)[1,:], pen='g')
        p2.plot((d - med)[2,:], pen='r')
        p2.plot((d - med)[3,:], pen='y')
        p2.plot(cutoff, pen='c')
        win2.show()
        winlist.append(win2)







        self.winlist = winlist
        # Find the bad pixel positions
        # Note the [:, None] - needed to cast the correct shapes
        badPixs = np.argwhere((d - med)>(cutoff))
        for pix in badPixs:
            # get the other pixels in the row which aren't the cosmic
            p = d[pix[0], [i for i in range(d.shape[1]) if not i==pix[1]]]
            # Replace the cosmic by the average of the others
            # Could get hairy if more than one cosmic per row.
            # Maybe when doing many exposures?
            d[pix[0], pix[1]] = np.mean(p)
        self.clean_array = np.array(d)


    def make_spectrum(self):
        '''
        Integrates over vertical axis of the cleaned image

        I'm not exactly sure y_min and y_max are counting from the same side as
        in the UI.
        '''
        if not self.isSeries:
            self.spectrum = self.clean_array[self.equipment_dict['y_min']:self.equipment_dict['y_max'],:].sum(axis=0)
            wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
                                          self.equipment_dict['grating'])
            self.spectrum = np.concatenate((wavelengths, self.spectrum)).reshape(2,1600).T

        else:
            self.spectrum = self.raw_array.sum(axis=0)
            wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
                                          self.equipment_dict['grating'])
            self.spectrum = np.concatenate((wavelengths, self.spectrum)).reshape(2,1600).T


    def isEmpty(self):
        """
        returns whether the raw_array is empty
        """
        return bool(self.raw_array.size)

    def updateSaveSettings(self, other):
        """
        Given an other EMCCD_image, this will populate this objects
        save settings (img no, filename, etc)
        """
        self.filename = other.file_name
        self.file_no = other.file_no
        self.description = other.description
        self.equipment_dict.update(other.equipment_dict)

    def addSpectrum(self, other):
        if isinstance(other, EMCCD_image):
            newSpec  = np.array(other.spectrum[:,1])
            pulse = other.equipment_dict["fel_pulses"]
            pulse = 1 if pulse == 0 else pulse
            newSpec /= pulse
            self.equipment_dict["fieldStrength"].append(other.equipment_dict["fieldStrength"])
            self.equipment_dict["fieldInt"].append(other.equipment_dict["fieldInt"])
            self.equipment_dict["fel_pulses"].append(other.equipment_dict["fel_pulses"])
            self.raw_array = np.row_stack((self.raw_array, newSpec))

        elif isinstance(other, np.ndarray):
            self.raw_array = np.row_stack((self.raw_array, other))

    def initializeSeries(self):
        """
        To be called when the class will hold a collection
        of the FVB spectra. Sets up self.spectra and
        makes equipment dict ready to append new values
        """
        self.isSeries = True
        self.clean_array = None
        pulse = self.equipment_dict["fel_pulses"]
        pulse = 1 if pulse == 0 else pulse
        self.raw_array = self.spectrum[:,1].reshape((1, 1600))/pulse
        self.file_no += "seriesed"
        self.equipment_dict["fieldStrength"] = [self.equipment_dict["fieldStrength"]]
        self.equipment_dict["fieldInt"] = [self.equipment_dict["fieldInt"]]
        self.equipment_dict["fel_pulses"] = [self.equipment_dict["fel_pulses"]]

class PL_image(EMCCD_image):
    '''
    This class is for handling PL images and turning them into simple spectra.
    '''
    
    # def __init__(self, raw_array, file_name, description, pl_dict, equipment_dict):
    #     '''
    #     This initializes a PL image instance.  I expect the header to be slightly
    #     different from the HSG or absorption headers.
    #
    #     image_array = 400x1600 array with data in it
    #     bg_array = appropriate bg_array
    #     pl_dict = the important parameters for hsg:
    #         sample_name
    #         sample_temperature
    #         excitation_power
    #         excitation_lambda
    #     experiment_dict = the important experimental apparatus conditions:
    #         CCD_temperature
    #         exposure
    #         gain
    #         y_min
    #         y_max
    #         grating
    #         center_lambda
    #         slits
    #         dark_region (maybe not that useful if can look at y_max + n)
    #     '''
    #     self.raw_array = np.array(raw_array)
    #     self.file_name = file_name
    #     self.description = description
    #     self.pl_dict = pl_dict
    #     self.equipment_dict = equipment_dict
    #     self.clean_array = None
    #     self.spectrum = None
    #     self.addenda = [0, file_name] # This is important for keeping track of addition and subtraction
    #     self.subtrahenda = []
    
    # def save_spectrum(self, folder_str='PL files'):
    #     '''
    #     Saves the general spectrum.  Unsure if we need it, but, again, seems
    #     useful for novel, basic stuff.
    #     '''
    #     try:
    #         os.mkdir(folder_str)
    #     except OSError, e:
    #         if e.errno == errno.EEXIST:
    #             pass
    #         else:
    #             raise
    #
    #     pl_str = json.dumps(self.pl_dict)
    #     self.equipment_dict['addenda': self.addenda]
    #     self.equipment_dict['subtrahenda': self.subtrahenda]
    #     equipment_str = json.dumps(self.equipment_dict, sort_keys=True)
    #
    #     save_file_name = 'pl_' + self.file_name
    #     origin_import = '\nWavelength,Signal\nnm,arb. u.'
    #     my_header = self.description + '\n' + pl_str + '\n' + equipment_str + origin_import
    #     np.savetxt(os.path.join(folder_str, save_file_name), self.spectrum,
    #                delimiter=',', header=my_header, comments='#', fmt='%f')
    #
    # def save_images(self, folder_str='Raw files'):
    #     '''
    #     Saves the raw_array, not the cleaned one.  Cleaning isn't that hard,
    #     and how we do it could change in the future.
    #
    #     This really depends on how the folders are initialized by the UI.  Will
    #     they already exist by the time we get to saving images, or do they need
    #     to be created on the fly?
    #
    #     Also, I'm pretty sure self.raw_array is still ints?
    #     '''
    #     try:
    #         os.mkdir(folder_str)
    #     except OSError, e:
    #         if e.errno == errno.EEXIST:
    #             pass
    #         else:
    #             raise
    #
    #     pl_str = json.dumps(self.pl_dict)
    #     self.equipment_dict['addenda': self.addenda]
    #     self.equipment_dict['subtrahenda': self.subtrahenda]
    #     equipment_str = json.dumps(self.equipment_dict, sort_keys=True)
    #
    #     my_header = self.description + '\n' + pl_str + '\n' + equipment_str
    #
    #     np.savetxt(os.path.join(folder_str, self.file_name), self.raw_array,
    #                delimiter=',', header=my_header, comments='#', fmt='%d')

class Abs_image(EMCCD_image):
    origin_import = '\nWavelength,Raw Trans\nnm,arb. u.'
    def __init__(self, raw_array=[], file_name='', file_no=None, description='', equipment_dict={}):
        super(Abs_image, self).__init__(raw_array, file_name, file_no, description, equipment_dict)
        self.abs_spec = None
        self.equipment_dict["reference_file"] = ""
    def __eq__(self, other):
        if type(other) is not type(self):
            print("not same type: {}/{}/{}".format(type(other), type(self), type(Abs_image())))
            return False
        if self.equipment_dict["gain"] != other.equipment_dict["gain"]:
            return False
        if self.equipment_dict["exposure"] != other.equipment_dict["exposure"]:
            return False
        if self.equipment_dict["grating"] != other.equipment_dict["grating"]:
            return False
        if self.equipment_dict["center_lambda"] != other.equipment_dict["center_lambda"]:
            return False
        return True

    def __div__(self, other):
        # self is the reference spectrum
        # other is the tranmission data

        if type(other) is not type(self):
            raise TypeError("Cannot divide {}".format(type(other)))
        ret = copy.deepcopy(other)
        abs_spec = np.log10(self.spectrum[:,1] / other.spectrum[:,1])
        wavelengths = gen_wavelengths(self.equipment_dict['center_lambda'],
                                      self.equipment_dict['grating'])

        # First is blank
        # other is transmission
        ret.spectrum = np.concatenate((wavelengths, self.spectrum[:,1].T,
                                        other.spectrum[:,1].T, abs_spec)).reshape(4,1600).T
        return ret





def gen_wavelengths(center_lambda, grating):
    '''
    This returns a 1600 element list of wavelengths for each pixel in the EMCCD based on grating and center wavelength
    
    grating = which grating, 1 or 2
    center = center wavelength in nanometers
    '''
    b = 0.75 # length of spectrometer, in m
    k = -1.0 # order looking at
    r = 16.0e-6 # distance between pixles on CCD

    if grating == 1:
        d = 1./1800000.
        gamma = 0.213258508834
        delta = 1.46389935365
    elif grating == 2:
        d = 1./1200000.
        gamma = 0.207412628027
        delta = 1.44998344749
    elif grating == 3:
        d = 1./600000.
        gamma = 0.213428934011
        delta = 1.34584754696
    else:
        print("What a dick, that's not a valid grating")
        return None
    
    center = center_lambda*10**-9
    wavelength_list = np.arange(-799.0,801.0)
    
    output = d*k**(-1)*((-1)*np.cos(delta+gamma+(-1)*np.arccos((-1/4)*(1/np.cos((1/2)*gamma))**2*(2*(np.cos((1/2)*gamma)**4*(2+(-1)*d**(-2)*k**2*center**2+2*np.cos(gamma)))**(1/2)+d**(-1)*k*center*np.sin(gamma)))+np.arctan(b**(-1)*(r*wavelength_list+b*np.cos(delta+gamma))*(1/np.sin(delta+gamma))))+(1+(-1/16)*(1/np.cos((1/2)*gamma))**4*(2*(np.cos((1/2)*gamma)**4*(2+(-1)*d**(-2)*k**2*center**2+2*np.cos(gamma)))**(1/2)+d**(-1)*k*center*np.sin(gamma))**2)**(1/2))   
    
    output = (output + center)*10**9
    return output


def calc_THz_intensity(total_energy, window_trans=1, sample_eff_field=1, pulse_width=37,
                       ratio=None, radius=0.05, ito_reflect=0.7):
    """
    This will calculate the THz intensity at the sample during the cavity dump.
    Do not enter a ratio if you want to do an average intensity calculation.

    total_energy - the total energy in the FEL pulse, in mJ
    pulse_width - the FWHM of the pulse as measured by the fast pyro, in ns
                  if you want for cavity dump intensity, use FWHM of the front
                  porch. Assumed to be 37 ns (pulse width for cavity dump
                  based on photon travel time for two round trips in undulator)
    window_trans - the power transmission of the cryostat window
    sample_eff_field - the effective _field_ at the front of the sample
    ratio - the ratio of the cavity dump to the front porch
    radius - the radius of the FEL spot, assumed to be 0.05 cm
    ito_reflect - the power reflection of the ITO beam combiner, assumed to be
                  around 0.7

    return - the intensity in the FEL spot in W/cm^2
    """
    area = np.pi * (radius)**2
    if ratio is not None:
        # power = 1e-3 * total_energy / (37e-9 + (pulse_width * 1e-9) / ratio)
        power = 1e-3 * total_energy * ratio/ (pulse_width * 1e-9)
    else:
        power = 1e-3 * total_energy / (pulse_width * 1e-9)
    return ito_reflect * window_trans * sample_eff_field**2 * power / area

def calc_THz_field(intensity, n=3.59):
    """
    This will calculate the THz field strength in the sample

    intensity - the intensity of the THz field
    n - the index of the material at the THz frequency, assumed to be 3.59 for GaAs

    return - the peak electric field in V/cm
    """
    return (2 * intensity / (8.85e-12 * 2.99e8 * n))**0.5