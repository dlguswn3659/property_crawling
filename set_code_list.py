import pandas as pd
import numpy as np

def make_areacode_list() :
    dong_code = pd.read_excel('./data_files/dongcode_20180703.xlsx',usecols=[1])

    # print(dong_code)

    dongcode_list = list(np.array(dong_code['법정동코드'].tolist()))

    # print(dongcode_list)

    citycode = []
    gucode = []
    dongcode = []

    for i in range(0, len(dongcode_list)) :
        im_dongcode = str(dongcode_list[i])
        citycode.append(im_dongcode[0:2])
        gucode.append(im_dongcode[2:5])
        dongcode.append(im_dongcode[5:10])

    return (dongcode_list, citycode, gucode, dongcode)

    # print(citycode)
    # print(gucode)
    # print(dongcode)