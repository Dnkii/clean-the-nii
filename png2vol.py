import os
import cv2
import numpy as np

def merge_images_train(files):
    image_depth = len(files)
    image_sample = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
    image_height, image_width = image_sample.shape
    image_3d = np.empty((image_depth,image_height, image_width))
    index = 0
    for file in files:
        image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        image_3d[index, :, :] = image
        index += 1
    return image_3d

def make_dataset_train(root):
    images = []
    masks = []
    predicts = []
    for dirName,subdirList,fileList in os.walk(root):
        image_filelist = []
        mask_filelist = []
        predict_filelist = []
        for filename in fileList:
            
            if "mask.png" in filename.lower(): #判断文件是否为dicom文件
                mask_filelist.append(os.path.join(dirName,filename)) # 加入到列表中
            else:
                if "predict.png" in filename.lower():
                    predict_filelist.append(os.path.join(dirName,filename))
                else:
                    image_filelist.append(os.path.join(dirName,filename))
        if len(image_filelist)<2:
            continue
        images.append(image_filelist)
        masks.append(mask_filelist)
        predicts.append(predict_filelist)
    return images, masks

def png2vol(path):
    images,masks = make_dataset_train(path)
    ct3d,mask3d,predict3d = [],[],[]
    for i in range(len(images)):
        x_path = images[i]
        y_path = masks[i]
        image = merge_images_train(x_path)
        ct3d.append(image)
        mask = merge_images_train(y_path)
        mask3d.append(mask)
        # predict = merge_images_train(y_path)
        # predict3d.append(predict)


    return ct3d,mask3d

def volbyname(path,name):
    predict_filelist = []
    for dirName,subdirList,fileList in os.walk(path):
        
        for filename in fileList:
            if "%s.png"%(name) in filename.lower(): #判断文件是否为dicom文件
                predict_filelist.append(os.path.join(dirName,filename)) # 加入到列表中
        break
    image = merge_images_train(predict_filelist)
    return np.transpose(image,(1,2,0))