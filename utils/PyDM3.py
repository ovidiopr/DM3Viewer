#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Python module for parsing GATAN DM3 files"""

################################################################################
## Python script for parsing GATAN DM3 (DigitalMicrograph) files
## --
## warning: *tested on single-image files only*
## --
## based on the DM3_Reader plug-in (v 1.3.4) for ImageJ
## by Greg Jefferis <jefferis@stanford.edu>
## http://rsb.info.nih.gov/ij/plugins/DM3_Reader.html
## --
## Python adaptation: Pierre-Ivan Raynal <raynal@univ-tours.fr>
## http://microscopies.med.univ-tours.fr/
## --
## Several improvements: Ovidio Peña-Rodríguez <ovidio@bytesfall.com>
## http://ovidio.me/
## --
## Format: http://www.er-c.org/cbb/info/dmformat/
##         https://imagej.nih.gov/ij/plugins/DM3Format.gj.html
## --
## 2018-02-26 Made the library compatible with Python 3 (Ovidio)
## 2018-02-19 Added support for various data types (Ovidio)
## 2018-02-17 Removed PIL requirement (Ovidio)
## --
################################################################################

import os
from struct import unpack
from time import time

import numpy as np

__all__ = ["DM3", "VERSION"]

VERSION = '1.1'

debugLevel = 0  # 0=none, 1-3=basic, 4-5=simple, 6-10 verbose


### binary data reading functions ###

def readLong(f):
    """Read 4 bytes as integer in file f"""
    return unpack('>l', f.read(4))[0]


def readShort(f):
    """Read 2 bytes as integer in file f"""
    return unpack('>h', f.read(2))[0]


def readByte(f):
    """Read 1 byte as integer in file f"""
    return unpack('>b', f.read(1))[0]


def readBool(f):
    """Read 1 byte as boolean in file f"""
    return (readByte(f) != 0)


def readChar(f):
    """Read 1 byte as char in file f"""
    return unpack('c', f.read(1))[0]


def readString(f, len_=1):
    """Read len_ bytes as a string in file f"""
    return unpack('>%is'%(len_), f.read(len_))[0]


def readLEShort(f):
    """Read 2 bytes as *little endian* integer in file f"""
    return unpack('<h', f.read(2))[0]


def readLELong(f):
    """Read 4 bytes as *little endian* integer in file f"""
    return unpack('<l', f.read(4))[0]


def readLEUShort(f):
    """Read 2 bytes as *little endian* unsigned integer in file f"""
    return unpack('<H', f.read(2))[0]


def readLEULong(f):
    """Read 4 bytes as *little endian* unsigned integer in file f"""
    return unpack('<L', f.read(4))[0]


def readLEFloat(f):
    """Read 4 bytes as *little endian* float in file f"""
    return unpack('<f', f.read(4))[0]


def readLEDouble(f):
    """Read 8 bytes as *little endian* double in file f"""
    return unpack('<d', f.read(8))[0]


## constants for encoded data types ##
SHORT = 2
LONG = 3
USHORT = 4
ULONG = 5
FLOAT = 6
DOUBLE = 7
BOOLEAN = 8
CHAR = 9
OCTET = 10
STRUCT = 15
STRING = 18
ARRAY = 20

# - association data type <--> reading function
readFunc = {
    SHORT: readLEShort,
    LONG: readLELong,
    USHORT: readLEUShort,
    ULONG: readLEULong,
    FLOAT: readLEFloat,
    DOUBLE: readLEDouble,
    BOOLEAN: readBool,
    CHAR: readChar,
    OCTET: readChar,  # difference with char???
}

## list of image DataTypes ##
dataTypes = {
    0: 'NULL_DATA',
    1: 'SIGNED_INT16_DATA',
    2: 'REAL4_DATA',
    3: 'COMPLEX8_DATA',
    4: 'OBSOLETE_DATA',
    5: 'PACKED_DATA',
    6: 'UNSIGNED_INT8_DATA',
    7: 'SIGNED_INT32_DATA',
    8: 'RGB_DATA',
    9: 'SIGNED_INT8_DATA',
    10: 'UNSIGNED_INT16_DATA',
    11: 'UNSIGNED_INT32_DATA',
    12: 'REAL8_DATA',
    13: 'COMPLEX16_DATA',
    14: 'BINARY_DATA',
    15: 'RGB_UINT8_0_DATA',
    16: 'RGB_UINT8_1_DATA',
    17: 'RGB_UINT16_DATA',
    18: 'RGB_FLOAT32_DATA',
    19: 'RGB_FLOAT64_DATA',
    20: 'RGBA_UINT8_0_DATA',
    21: 'RGBA_UINT8_1_DATA',
    22: 'RGBA_UINT8_2_DATA',
    23: 'RGBA_UINT8_3_DATA',
    24: 'RGBA_UINT16_DATA',
    25: 'RGBA_FLOAT32_DATA',
    26: 'RGBA_FLOAT64_DATA',
    27: 'POINT2_SINT16_0_DATA',
    28: 'POINT2_SINT16_1_DATA',
    29: 'POINT2_SINT32_0_DATA',
    30: 'POINT2_FLOAT32_0_DATA',
    31: 'RECT_SINT16_1_DATA',
    32: 'RECT_SINT32_1_DATA',
    33: 'RECT_FLOAT32_1_DATA',
    34: 'RECT_FLOAT32_0_DATA',
    35: 'SIGNED_INT64_DATA',
    36: 'UNSIGNED_INT64_DATA',
    37: 'LAST_DATA',
}

## other constants ##
IMGLIST = "root.ImageList."
OBJLIST = "root.DocumentObjectList."
MAXDEPTH = 64

DEFAULTCHARSET = 'utf-8'


## END constants ##


class DM3(object):
    """DM3 object. """

    ## utility functions
    def _makeGroupString(self):
        tString = "%i"%(self._curGroupAtLevelX[0])
        for i in range(1, self._curGroupLevel + 1):
            tString += '.%i'%(self._curGroupAtLevelX[i])
        return tString

    def _makeGroupNameString(self):
        tString = b"%s"%(self._curGroupNameAtLevelX[0])
        for i in range(1, self._curGroupLevel + 1):
            tString = b'%s.%s'%(tString, self._curGroupNameAtLevelX[i])
        return tString

    def _readTagGroup(self):
        # go down a level
        self._curGroupLevel += 1
        # increment group counter
        self._curGroupAtLevelX[self._curGroupLevel] += 1
        # set number of current tag to -1
        # --- readTagEntry() pre-increments => first gets 0
        self._curTagAtLevelX[self._curGroupLevel] = -1
        if (debugLevel > 5):
            print("rTG: Current Group Level: %i"%(self._curGroupLevel))
        # is the group sorted?
        isSorted = readBool(self._f)
        # is the group open?
        isOpen = readBool(self._f)
        # number of Tags
        nTags = readLong(self._f)
        if (debugLevel > 5):
            print("rTG: Iterating over the %i tag entries in this group"%(nTags))
        # read Tags
        for i in range(nTags):
            self._readTagEntry()
        # go back up one level as reading group is finished
        self._curGroupLevel += -1
        return 1

    def _readTagEntry(self):
        # is data or a new group?
        isData = (readByte(self._f) == 21)
        self._curTagAtLevelX[self._curGroupLevel] += 1
        # get tag label if exists
        lenTagLabel = readShort(self._f)
        if (lenTagLabel != 0):
            tagLabel = readString(self._f, lenTagLabel)
        else:
            tagLabel = b"%i"%(self._curTagAtLevelX[self._curGroupLevel])
        if (debugLevel > 5):
            print("%i | %s:\nTag label = %s"%(self._curGroupLevel, self._makeGroupString(), tagLabel))
        elif (debugLevel > 0):
            print("%i: Tag label = %s"%(self._curGroupLevel, tagLabel))
        if isData:
            # give it a name
            self._curTagName = b"%s.%s"%(self._makeGroupNameString(), tagLabel)
            # read it
            self._readTagType()
        else:
            # it is a tag group
            self._curGroupNameAtLevelX[self._curGroupLevel + 1] = tagLabel
            self._readTagGroup()  # increments curGroupLevel
        return 1

    def _readTagType(self):
        delim = readString(self._f, 4).decode('UTF-8')
        if (delim != u'%%%%'):
            raise Exception("%x: Tag Type delimiter not %%%%"%(self._f.tell()))
        nInTag = readLong(self._f)
        self._readAnyData()
        return 1

    def _encodedTypeSize(self, eT):
        # returns the size in bytes of the data type
        if eT == 0:
            width = 0
        elif eT in (BOOLEAN, CHAR, OCTET):
            width = 1
        elif eT in (SHORT, USHORT):
            width = 2
        elif eT in (LONG, ULONG, FLOAT):
            width = 4
        elif eT == DOUBLE:
            width = 8
        else:
            # returns -1 for unrecognised types
            width = -1
        return width

    def _readAnyData(self):
        ## higher level function dispatching to handling data types
        ## to other functions
        # - get Type category (short, long, array...)
        encodedType = readLong(self._f)
        # - calc size of encodedType
        etSize = self._encodedTypeSize(encodedType)
        if (debugLevel > 5):
            print("rAnD, %x:\tTag Type = %i\tTag Size = %i"%(self._f.tell(), encodedType, etSize))
        if (etSize > 0):
            self._storeTag(self._curTagName, self._readNativeData(encodedType, etSize))
        elif (encodedType == STRING):
            stringSize = readLong(self._f)
            self._readStringData(stringSize)
        elif (encodedType == STRUCT):
            # does not store tags yet
            structTypes = self._readStructTypes()
            self._readStructData(structTypes)
        elif (encodedType == ARRAY):
            # does not store tags yet
            # indicates size of skipped data blocks
            arrayTypes = self._readArrayTypes()
            self._readArrayData(arrayTypes)
        else:
            raise Exception("rAnD, %x: Can't understand encoded type"%(self._f.tell()))
        return 1

    def _readNativeData(self, encodedType, etSize):
        # reads ordinary data types
        if encodedType in readFunc:
            val = readFunc[encodedType](self._f)
        else:
            raise Exception("rND, %x: Unknown data type %i"%(self._f.tell(), encodedType))
        if (debugLevel > 3):
            print("rND, %x: %s"%(self._f.tell(), str(val)))
        elif (debugLevel > 0):
            print(val)
        return val

    def _readStringData(self, stringSize):
        # reads string data
        if (stringSize <= 0):
            rString = ""
        else:
            if (debugLevel > 3):
                print("rSD @ %s/%x:"%(str(self._f.tell()), self._f.tell()))
            ## !!! *Unicode* string (UTF-16)... convert to Python unicode str
            rString = readString(self._f, stringSize).decode("utf_16_le")
            if (debugLevel > 3):
                print(rString + "   <" + repr(rString) + ">")
        if (debugLevel > 0):
            print("StringVal: %s"%(rString))
        self._storeTag(self._curTagName, rString)
        return rString

    def _readArrayTypes(self):
        # determines the data types in an array data type
        arrayType = readLong(self._f)
        itemTypes = []
        if (arrayType == STRUCT):
            itemTypes = self._readStructTypes()
        elif (arrayType == ARRAY):
            itemTypes = self._readArrayTypes()
        else:
            itemTypes.append(arrayType)
        return itemTypes

    def _readArrayData(self, arrayTypes):
        # reads array data

        arraySize = readLong(self._f)

        if (debugLevel > 3):
            print("rArD, %x: Reading array of size = %i"%(self._f.tell(), arraySize))

        itemSize = 0
        encodedType = 0

        for i in range(len(arrayTypes)):
            encodedType = int(arrayTypes[i])
            etSize = self._encodedTypeSize(encodedType)
            itemSize += etSize
            if (debugLevel > 5):
                print("rArD: Tag Type = %i\tTag Size = %i"%(encodedType, etSize))
            ##! readNativeData(encodedType, etSize) !##

        if (debugLevel > 5):
            print("rArD: Array Item Size = %i"%(itemSize))

        bufSize = arraySize*itemSize

        if ((not self._curTagName.endswith(b"ImageData.Data"))
                and (len(arrayTypes) == 1)
                and (encodedType == USHORT)
                and (arraySize < 256)):
            # treat as string
            val = self._readStringData(bufSize)
        else:
            # treat as binary data
            # - store data size and offset as tags
            self._storeTag(self._curTagName + b".Size", bufSize)
            self._storeTag(self._curTagName + b".Offset", self._f.tell())
            # - skip data w/o reading
            self._f.seek(self._f.tell() + bufSize)

        return 1

    def _readStructTypes(self):
        # analyses data types in a struct

        if (debugLevel > 3):
            print("Reading Struct Types at Pos = %x"%(self._f.tell()))

        structNameLength = readLong(self._f)
        nFields = readLong(self._f)

        if (debugLevel > 5):
            print("nFields = %i"%(nFields))

        if (nFields > 100):
            raise Exception("%x: Too many fields"%(self._f.tell()))

        fieldTypes = []
        nameLength = 0
        for i in range(nFields):
            nameLength = readLong(self._f)
            if (debugLevel > 9):
                print("%ith namelength = %i"%(i, nameLength))
            fieldType = readLong(self._f)
            fieldTypes.append(fieldType)

        return fieldTypes

    def _readStructData(self, structTypes):
        # reads struct data based on type info in structType
        for i in range(len(structTypes)):
            encodedType = structTypes[i]
            etSize = self._encodedTypeSize(encodedType)

            if (debugLevel > 5):
                print("Tag Type = %i\tTag Size = %i"%(encodedType, etSize))

            # get data
            self._readNativeData(encodedType, etSize)

        return 1

    def _storeTag(self, tagName, tagValue):
        # - convert tag value to bytes if it is not already
        if type(tagValue) is int:
            tagValue = b"%i"%(tagValue)
        elif type(tagValue) is float:
            tagValue = b"%f"%(tagValue)
        elif type(tagValue) is str:
            tagValue = tagValue.encode()
        elif type(tagValue) is bool:
            tagValue = b"%r"%(tagValue)
        # store Tags as list and dict
        # print(b"%s = %s" % (tagName,  tagValue))
        self._storedTags.append(b"%s = %s"%(tagName, tagValue))
        self._tagDict[tagName] = tagValue

    ### END utility functions ###

    def __init__(self, filename, debug=0):
        """DM3 object: parses DM3 file."""

        ## initialize variables ##
        self.debug = debug
        self._outputcharset = DEFAULTCHARSET
        self._filename = filename
        self._chosenImage = 1
        # - track currently read group
        self._curGroupLevel = -1
        self._curGroupAtLevelX = [0 for x in range(MAXDEPTH)]
        self._curGroupNameAtLevelX = ['' for x in range(MAXDEPTH)]
        # - track current tag
        self._curTagAtLevelX = ['' for x in range(MAXDEPTH)]
        self._curTagName = ''
        # - open file for reading
        self._f = open(self._filename, 'rb')
        # - create Tags repositories
        self._storedTags = []
        self._tagDict = {}

        if self.debug > 0:
            t1 = time()
        ## read header (first 3 4-byte int)
        # get version
        fileVersion = readLong(self._f)
        # get indicated file size
        fileSize = readLong(self._f)
        # get byte-ordering
        littleEndian = (readLong(self._f) == 1)
        isDM3 = (fileVersion == 3) and littleEndian
        # check file header, raise Exception if not DM3
        if not isDM3:
            raise Exception("'%s' does not appear to be a DM3 file."%os.path.split(self._filename)[1])
        elif self.debug > 0:
            print("'%s' appears to be a DM3 file"%(self._filename))

        if (debugLevel > 5 or self.debug > 1):
            print("Header info.:")
            print("\t-File version: %i"%fileVersion)
            print("\t-Little Endian: %r"%littleEndian)
            print("\t-File size: %i bytes"%fileSize)

        # set name of root group (contains all data)...
        self._curGroupNameAtLevelX[0] = b"root"
        # ... then read it
        self._readTagGroup()
        if self.debug > 0:
            print("-- %i Tags read --"%len(self._storedTags))

        if self.debug > 0:
            t2 = time()
            print("| parse DM3 file: %.3g s"%(t2 - t1))

    @property
    def outputcharset(self):
        """Returns Tag dump/output charset."""
        return self._outputcharset

    @outputcharset.setter
    def outputcharset(self, value):
        """Set Tag dump/output charset."""
        self._outputcharset = value

    @property
    def filename(self):
        """Returns full file path."""
        return self._filename

    @property
    def tags(self):
        """Returns all image Tags."""
        return self._tagDict

    def dumpTags(self, dump_dir='/tmp'):
        """Dumps image Tags in a txt file."""
        dump_file = os.path.join(dump_dir, "%s.tagdump.txt"%(os.path.split(self._filename)[1]))
        try:
            dumpf = open(dump_file, 'w')
        except:
            print("Warning: cannot generate dump file.")
        else:
            for tag in self._storedTags:
                dumpf.write(tag.encode(self._outputcharset) + "\n")
            dumpf.close

    @property
    def info(self):
        """Extracts useful experiment info from DM3 file."""
        # define useful information
        tag_root = b'root.ImageList.1'
        bar_tag = b'%s.ImageTags.DataBar'%(tag_root)
        mic_tag = b'%s.ImageTags.Microscope Info'%(tag_root)
        info_keys = {
            'descrip': b"%s.Description"%(tag_root),
            'acq_date': b"%s.Acquisition Date"%(bar_tag),
            'acq_time': b"%s.Acquisition Time"%(bar_tag),
            'name': b"%s.Name"%(mic_tag),
            'micro': b"%s.Microscope"%(mic_tag),
            'hv': b"%s.Voltage"%(mic_tag),
            'mag': b"%s.Indicated Magnification"%(mic_tag),
            'mode': b"%s.Operation Mode"%(mic_tag),
            'operator': b"%s.Operator"%(mic_tag),
            'specimen': b"%s.Specimen"%(mic_tag),
            #    'image_notes': b"root.DocumentObjectList.10.Text' # = Image Notes
        }
        # get experiment information
        infoDict = {}
        for key, tag_name in info_keys.items():
            if tag_name in self.tags:
                # tags supplied as Python unicode str; convert to chosen charset
                # (typically latin-1 or utf-8)
                infoDict[key] = self.tags[tag_name].decode(self._outputcharset)
        # return experiment information
        return infoDict

    @property
    def thumbnail(self):
        """Returns thumbnail as PIL Image."""
        # get thumbnail
        tag_root = b'root.ImageList.0.ImageData'
        tn_size = int(self.tags[b"%s.Data.Size"%(tag_root)])
        tn_offset = int(self.tags[b"%s.Data.Offset"%(tag_root)])
        tn_width = int(self.tags[b"%s.Dimensions.0"%(tag_root)])
        tn_height = int(self.tags[b"%s.Dimensions.1"%(tag_root)])

        if self.debug > 0:
            print("Notice: tn data in %s starts at %s"%(os.path.split(self._filename)[1], hex(tn_offset)))
            print("Notice: tn size: %sx%s px"%(tn_width, tn_height))

        if (tn_width*tn_height*4) != tn_size:
            raise Exception("Cannot extract thumbnail from %s"%(os.path.split(self._filename)[1]))
        else:
            self._f.seek(tn_offset)
            rawdata = self._f.read(tn_size)
            # - read as 16-bit LE unsigned integer
            tn = np.frombuffer(rawdata, dtype='<h').reshape((tn_width, tn_height))
        # - return image
        return tn

    @property
    def thumbnaildata(self):
        """Returns thumbnail data as numpy.array"""
        return np.copy(self.thumbnail)

    def makePNGThumbnail(self, tn_file=''):
        """Save thumbnail as PNG file."""
        # - cleanup name
        if tn_file == '':
            tn_path = os.path.join('./', "%s.tn.png"%(os.path.split(self.filename)[1]))
        else:
            if os.path.splitext(tn_file)[1] != '.png':
                tn_path = "%s.png"%(os.path.splitext(tn_file)[0])
            else:
                tn_path = tn_file
        # - save tn file
        try:
            import matplotlib.pyplot as plt

            data = self.thumbnail
            dpi = 200
            size = (1.0*data.shape[0]/dpi, 1.0*data.shape[1]/dpi)
            fig = plt.figure()
            fig.set_size_inches(size)
            ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
            ax.set_axis_off()
            fig.add_axes(ax)
            plt.set_cmap('gray')
            ax.imshow(data, aspect='equal')

            plt.savefig(tn_path, dpi=dpi, format='png')
            if self.debug > 0:
                print("Thumbnail saved as '%s'."%(tn_path))
        except:
            print("Warning: could not save thumbnail.")

    @property
    def image(self):
        """Read image data as Numpy Array"""

        def img_reshape(img, nx, ny, nz):
            if nz > 1:  # Three dimensions
                return img.reshape((nx, ny, nz))
            elif ny > 1:  # Two dimensions
                return img.reshape((nx, ny))
            else:  # One dimension
                return img

        # Numpy "raw" decoder modes for the various image dataTypes
        dataTypesDec = {
            1: '<h',  # 16-bit LE signed integer
            2: '<f',  # 32-bit LE floating point
            3: '<f',  # 64-bit LE complex floating point (we read it as float and then convert it)
            5: '<f',  # 32-bit LE packed complex (FFT)
            6: '>B',  # 8-bit unsigned integer
            7: '<i',  # 32-bit LE signed integer
            9: '>b',  # 8-bit signed integer
            10: '<H',  # 16-bit LE unsigned integer
            11: '<I',  # 32-bit LE unsigned integer
            12: '<d',  # 64-bit LE floating point (double)
            13: '<d',  # 128-bit LE complex floating point (we read it as double and then convert it)
            14: '>B',  # binary
        }

        # get relevant Tags
        tag_root = b'root.ImageList.1.ImageData'
        data_offset = int(self.tags[b"%s.Data.Offset"%(tag_root)])
        data_size = int(self.tags[b"%s.Data.Size"%(tag_root)])
        data_type = int(self.tags[b"%s.DataType"%(tag_root)])
        pixel_depth = int(self.tags[b"%s.PixelDepth"%(tag_root)])
        im_width = int(self.tags[b"%s.Dimensions.0"%(tag_root)])
        # If the second dimension doen't exists it means that it is a 1D spectrum
        if b"%s.Dimensions.1"%(tag_root) in self.tags:
            im_height = int(self.tags[b"%s.Dimensions.1"%(tag_root)])
        else:
            im_height = 1
        # If the third dimension doen't exists it means that it is a 2D image, otherwise it has 3D
        if b"%s.Dimensions.2"%(tag_root) in self.tags:
            im_depth = int(self.tags[b"%s.Dimensions.2"%(tag_root)])
        else:
            im_depth = 1

        # If the data size is not consistent raise an error
        if data_size != pixel_depth*im_width*im_height*im_depth:
            raise Exception("Actual data size (%i) does not match the expected size (%i)."%(
            data_size, pixel_depth*im_width*im_height*im_depth))

        if self.debug > 0:
            print("Notice: image data in %s starts at %x"%(os.path.split(self._filename)[1], data_offset))
            print("Notice: image size: %sx%s px"%(im_width, im_height))

        # check if image DataType is implemented, then read
        if data_type in dataTypesDec:
            decoder = dataTypesDec[data_type]
            if self.debug > 0:
                print("Notice: image data type: %s ('%s'), read as %s"%(data_type, dataTypes[data_type], decoder))
                t1 = time()
            self._f.seek(data_offset)
            rawdata = self._f.read(data_size)
            im = np.frombuffer(rawdata, dtype=decoder)

            if self.debug > 0:
                t2 = time()
                print("| read image data: %.3g s"%(t2 - t1))
        else:
            raise Exception("Cannot extract image data from %s: unimplemented DataType (%s:%s)."%
                            (os.path.split(self._filename)[1], data_type, dataTypes[data_type]))

        if data_type == 2:
            if im_depth > 1:  # Three dimensions
                im = np.swapaxes(im.reshape((im_depth, im_height, im_width)), 0, 2)
            else:
                im = img_reshape(im, im_width, im_height, im_depth)
        elif data_type in (3, 13):  # Create the complex array
            im = im[::2] + 1.0j*im[1::2]
            im = img_reshape(im, im_width, im_height, im_depth)
        elif data_type == 5:  # Unpack the complex array
            # TODO: Check the unpacking carefully because there seems to be a problem.
            if im_depth > 1:
                print("Warning: 3D data and complex unpacking expects 2D.")
            im = img_reshape(im, im_width, im_height, im_depth)
            tmp = np.ones(im.shape, dtype=np.complex64)

            tmp[:, 1 + im_height//2:] = im[:, 2::2] + 1.0j*im[:, 3::2]
            tmp[:, 1:im_height//2] = np.conjugate(np.fliplr(np.flipud(tmp[:, 1 + im_height//2:])))

            tmp[1 + im_width//2:, 0] = im[1:im_width//2, 0] + 1.j*im[1:im_width//2, 1]
            tmp[1:im_width//2, 0] = np.conjugate(np.flipud(tmp[1 + im_width//2:, 0]))

            tmp[1 + im_width//2:, im_height//2] = im[1 + im_width//2:, 0] + 1.j*im[1 + im_width//2:, 1]
            tmp[1:im_width//2, im_height//2] = np.conjugate(np.flipud(tmp[1 + im_width//2:, im_height//2]))

            tmp[0, 0] = im[0, 1] + 0.j
            tmp[im_width//2, 0] = im[0, 0] + 0.j
            tmp[0, im_height//2] = im[im_width//2, 1] + 0.j
            tmp[im_width//2, im_height//2] = im[im_width//2, 0] + 0.j

            im = tmp
        elif data_type == 14:  # if dataType is BINARY, binarize dataset (i.e., px_value>0 is True)
            im = im > 0
            im = img_reshape(im, im_width, im_height, im_depth)
        else:
            im = img_reshape(im, im_width, im_height, im_depth)

        return im

    @property
    def imagedata(self):
        """Extracts image data as numpy.array"""
        return np.copy(self.image)

    @property
    def imagetype(self):
        """Returns image data type"""
        if b"root.ImageList.1.ImageData.DataType" in self.tags:
            return int(self.tags[b"root.ImageList.1.ImageData.DataType"])
        else:
            return -1

    @property
    def contrastlimits(self):
        """Returns display range (cuts)."""
        from numpy import amin, amax
        tag_root = b'root.DocumentObjectList.0.ImageDisplayInfo'
        if b"%s.LowLimit"%(tag_root) in self.tags:
            low = int(float(self.tags[b"%s.LowLimit"%(tag_root)]))
        else:
            low = amin(self.imagedata)
        if b"%s.HighLimit"%(tag_root) in self.tags:
            high = int(float(self.tags[b"%s.HighLimit"%(tag_root)]))
        else:
            high = amax(self.imagedata)
        cuts = (low, high)
        return cuts

    @property
    def cuts(self):
        """Returns display range (cuts)."""
        return self.contrastlimits

    def axisunits(self, index=0):
        """Returns pixel size and unit for the given axis."""
        tag_root = b'root.ImageList.1.ImageData.Calibrations.Dimension.%i'%(index)
        origin = float(self.tags[b"%s.Origin"%(tag_root)])
        pixel_size = float(self.tags[b"%s.Scale"%(tag_root)])
        unit = self.tags[b"%s.Units"%tag_root]
        if unit != u'\xb5m':
            unit = unit.decode('UTF-8')
        if self.debug > 0:
            print("pixel size = %f %s"%(pixel_size, unit))
        return (origin, pixel_size, unit)

    @property
    def pxsize(self):
        """Returns pixel size and unit."""
        return self.axisunits(0)

    @property
    def sptunits(self):
        return self.tags[b"root.ImageList.1.ImageData.Calibrations.Brightness.Units"].decode('UTF-8')


## MAIN ##
if __name__ == '__main__':
    print("PyDM3 %s"%(VERSION))
