import pydicom
import os
import numpy as np
import cv2
import SimpleITK as sitk
from png2vol import png2vol,volbyname
# plus = 5
# mxval = 1275/plus
# mnval = -1275/plus

def hu_to_grayscale(volume, hu_min = None, hu_max = None, mn = None, mx = None):
    # Clip at max and min values if specified
    if hu_min is not None or hu_max is not None:
        volume = np.clip(volume, hu_min, hu_max)

    # Scale to values between 0 and 1
    if mx is not None:
        mxval = mx
    else:
        mxval = np.max(volume)
    if mn is not None:
        mnval = mn
    else: 
        mnval = np.min(volume)
    # mxval = mnval+hu_max-hu_min
    # mnval = hu_min
    # print(mxval)
    # print(mnval)
    im_volume = (volume - mnval)/max(mxval - mnval, 1e-3)

    # Return values scaled to 0-255 range, but *not cast to uint8*
    # Repeat three times to make compatible with color overlay
    im_volume = 255*im_volume
    #转uint8+增加维度，因为标记如果是彩色则需要RGB三通道，与之相加的CT图也要存成三维数组
    return im_volume
# 使用有标记的图减没标记的图得到只有标记部分灰度图(输出文件夹名称，无标记dicom图片位置，有标记dicom图片位置，输出图片名称，是否显示出来)
def drawNpGrey_mask(dirname,ArrayDicom,start=None,end=None):
    dir="./"+dirname
    if(os.path.exists(dir)==False):
        os.makedirs(dir)
    ArrayDicom = hu_to_grayscale(ArrayDicom)

    ArrayDicom = np.transpose(ArrayDicom, (1, 0, 2))
    if start is None:
        start = 0
    if end is None:
        end = len(ArrayDicom[0, 0])
    # ArrayDicom = hu_to_grayscale(ArrayDicom)
        
    for i in range(end - start):

        if ArrayDicom[:, :,start + i].shape != (512,512):
            # cv2.resize(ArrayDicom[:, :,start + i],(128,128),interpolation=cv2.INTER_CUBIC)
            cv2.imwrite('%s/%05d.png'%(dir,i), cv2.resize(ArrayDicom[:, :,start + i],(512,512),interpolation=cv2.INTER_CUBIC))
            # print("Output:"+'%s/%05d.png'%(dir,i))
            # cv2.imwrite('%s/%05d_mask.png'%(dir,i), cv2.resize(ArrayDicom_mask[:, :,start + i],(128,128),interpolation=cv2.INTER_CUBIC))
            # print("Output:"+'%s/%05d_mask.png'%(dir,i))
        else:
            cv2.imwrite('%s/%05d.png'%(dir,i), ArrayDicom[:, :,start + i])
            # print("Output:"+'%s/%05d.png'%(dir,i))
            # cv2.imwrite('%s/%05d_mask.png'%(dir,i), ArrayDicom_mask[:, :,start + i])
            # print("Output:"+'%s/%05d_mask.png'%(dir,i))

# 生成全部待预测数据集,只需改：
# PathDicom：读取地址
# start，end起始与结束图像编号
# 输出目录drawdcm("data/test1",filenameDCM,"%03d"%i,0)
# scipy.misc.imsave('outfile.jpg', image_array)
def gentest(Pathnii = "D:/awork/master/medical_segmentation/fortest",start=None,end=None,outputdir="data/bml"):

    img = sitk.ReadImage(Pathnii)
    data = sitk.GetArrayFromImage(img)
    print("模型形状",data.shape)
    spacing = img.GetSpacing()
    origin = img.GetOrigin()
    drawNpGrey_mask(outputdir,data)
    return spacing,origin

def nii2array(Pathnii):

    img = sitk.ReadImage(Pathnii)
    data = sitk.GetArrayFromImage(img)
    print("模型形状",data.shape)
    spacing = img.GetSpacing()
    origin = img.GetOrigin()
    return data,spacing,origin

def savenii(vol0,spacing,origin,outname):
    # kidney = volbyname(filepath,"predict")
    # tumor = volbyname(filepath,"predicttumor")
    # kidney[np.equal(kidney,255)] = 1
    # kidney[np.equal(tumor,255)] = 2
    vol = np.transpose(vol0, (2, 0, 1))
    vol = vol[::-1]
    out = sitk.GetImageFromArray(vol)
    out.SetSpacing(spacing)
    out.SetOrigin(origin)
    sitk.WriteImage(out,'%s.nii.gz'%(outname))

def savenii_straight(vol0,spacing,origin,outname):
    # kidney = volbyname(filepath,"predict")
    # tumor = volbyname(filepath,"predicttumor")
    # kidney[np.equal(kidney,255)] = 1
    # kidney[np.equal(tumor,255)] = 2
    # vol = np.transpose(vol0, (2, 0, 1))
    # vol = vol[::-1]
    out = sitk.GetImageFromArray(vol0)
    out.SetSpacing(spacing)
    out.SetOrigin(origin)
    sitk.WriteImage(out,'%s.nii.gz'%(outname))

def saveniidcm(filepath,spacing,origin,outname):
    kidney = volbyname(filepath,"predict")
    tumor = volbyname(filepath,"predicttumor")
    kidney[np.equal(kidney,255)] = 1
    kidney[np.equal(tumor,255)] = 2
    # kidney = np.transpose(kidney, (1, 2, 0))
    out = sitk.GetImageFromArray(kidney)
    out.SetSpacing(spacing)
    # out.SetOrigin(origin)
    sitk.WriteImage(out,'%s.nii.gz'%(outname))


def gentestdcm(PathDicom = "D:/awork/master/medical_segmentation/fortest",start=None,end=None,outputdir="data/bml",sign=""):
    # PathDicom = "D:/awork/master/肾脏/白美玲/dicom"
    lstFilesDCM = [] #用来存放图片文件的地址与名称
    for dirName,subdirList,fileList in os.walk(PathDicom):
    #     print(dirName,subdirList,fileList)#分别代表当前路径,子文件夹,子文件
        for filename in fileList:
            if ".dcm" in filename.lower(): #判断文件是否为dicom文件
                lstFilesDCM.append(os.path.join(dirName,filename)) # 加入到列表中
    if start is None:
        start=0
    if end is None:
        end=len(lstFilesDCM)
    print("共" + str(end) + "张图片")
    filenames = []
    image = sitk.ReadImage(lstFilesDCM[0])
    # ds = pydicom.read_file(lstFilesDCM[0])
    # Spacing2 = (float(ds.SliceThickness), float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1]))
    origin = image.GetOrigin() # x, y, z
    spacing = image.GetSpacing() # x, y, z
    print(spacing,origin)

    for i in range(end-start):
        ds = pydicom.read_file(lstFilesDCM[i])
        filenames.append(len(lstFilesDCM) - int(ds.InstanceNumber))

    drawdcm(outputdir,lstFilesDCM,filenames,0,sign)
    return spacing,origin

def drawdcm(dirname,filenameDCM,name,draw=1,sign=''):
    RefDs = pydicom.read_file(filenameDCM[0]) 
    ConstPixelDims = (int(RefDs.Rows),int(RefDs.Columns),len(filenameDCM))
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)
    for i in range(len(name)):
        ds = pydicom.read_file(filenameDCM[i])
        ArrayDicom[:, :, i] = ds.pixel_array # 轴状面显示
        # ArrayDicom[:, :, i] = hu_to_grayscale(ArrayDicom[:, :, i])

    dir="./"+dirname
    if(os.path.exists(dir)==False):
        os.makedirs(dir)
#     ArrayDicom = numpy.transpose(ArrayDicom, (1, 0))
    # print(np.max(ArrayDicom))
    ArrayDicom = hu_to_grayscale(ArrayDicom)#,-1024.0, 1280.0,-1024.0, 1280.0)
    for i in range(len(name)):
        if ArrayDicom[:, :].shape != (512,512):
            cv2.imwrite('%s/%05d%s.png'%(dir,name[i],sign), cv2.resize(ArrayDicom[:, :, i],(512,512),interpolation=cv2.INTER_CUBIC))
        else:
            cv2.imwrite('%s/%05d%s.png'%(dir,name[i],sign),ArrayDicom[:, :, i])
        print("\r",end="",flush = True)
        print("输出第"+"%05d"%i+"张图片中",end="")