from nii import savenii,nii2array
import numpy as np

arr,spa,ori = nii2array("3.nii.gz")
arr = np.array(arr)
arr2 = arr

def grow(arr,axis,hu,pad,aim=1):
    num=0
    lists = []
    lists.append(axis)
    if aim>=(hu-pad) and aim<=(hu+pad):
        raise Exception("the 'aim' must not in [%s,%s]"%(hu-pad,hu+pad))
    x,y,z=axis[0],axis[1],axis[2]
    if x>=arr.shape[0] or y>=arr.shape[1] or z>=arr.shape[2] or x<0 or y<0 or z<0:
        return
    while len(lists):
        ax=lists.pop()
        x,y,z=ax[0],ax[1],ax[2]
        if x>=arr.shape[0] or y>=arr.shape[1] or z>=arr.shape[2] or x<0 or y<0 or z<0:
            continue
        if arr[x,y,z]>(hu-pad) and arr[x,y,z]<(hu+pad):
            arr[x,y,z]=aim
            num+=1
            lists.append([x-1,y,z])
            lists.append([x+1,y,z])
            lists.append([x,y-1,z])
            lists.append([x,y+1,z])
            lists.append([x,y,z-1])
            lists.append([x,y,z+1])
#     arr[arr!=1]=0
#     arr[arr==1]=255
    print(num)
    return num

def findbiggest(arr,hu=255,pad=10):
    nums = []
    mask = 1
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            for k in range(arr.shape[2]):
                if arr[i,j,k]>(hu-pad) and arr[i,j,k]<(hu+pad):
                    nums.append(grow(arr,[i,j,k],hu,pad,aim=mask))
                    mask+=1
    arr[arr==(nums.index(max(nums))+1)]=255
    arr[arr!=255]=0
    return

findbiggest(arr2)
savenii_straight(arr,spa,ori,"3_new")