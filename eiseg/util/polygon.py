from enum import Enum

import cv2
import matplotlib.pyplot as plt


class Instructions(Enum):
    No_Instruction = 0
    Polygon_Instruction = 1


def get_polygon(label, sample=2):
    results = cv2.findContours(
        image=label, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_TC89_KCOS
    )  # 获取内外边界，用RETR_TREE更好表示
    cv2_v = cv2.__version__.split(".")[0]
    contours = results[1] if cv2_v == "3" else results[0]  # 边界
    hierarchys = results[2] if cv2_v == "3" else results[1]  # 隶属信息
    if len(contours) != 0:  # 可能出现没有边界的情况
        polygons = []
        relas = []
        for contour, hierarchy in zip(contours, hierarchys[0]):
            out = cv2.approxPolyDP(contour, sample, True)
            # 判断自己，如果是子对象就不管自己是谁
            if hierarchy[2] == -1:
                own = None
            else:
                if hierarchy[0] == -1 and hierarchy[1] == -1:
                    own = 0
                elif hierarchy[0] != -1 and hierarchy[1] == -1:
                    own = hierarchy[0] - 1
                else:
                    own = hierarchy[1] + 1
            rela = (own,  # own
                    hierarchy[-1] if hierarchy[-1] != -1 else None)  # parent
            polygon = []
            for p in out:
                polygon.append(p[0])
            polygons.append(polygon)  # 边界
            relas.append(rela)  # 关系
        for i in range(len(relas)):
            if relas[i][1] != None:  # 有父母
                for j in range(len(relas)):
                    if relas[j][0] == relas[i][1]:  # i的父母就是j（i是j的内圈）
                        polygons[j].append(polygons[j][0])  # 闭合
                        polygons[j].extend(polygons[i])
                        polygons[j].append(polygons[i][0])  # 闭合
                        polygons[i] = None
        polygons = list(filter(None, polygons))  # 清除加到外圈的内圈多边形
        return polygons
    else:
        print("没有标签范围，无法生成边界")
        return None


# def get_polygon(label, sample=1):
#     contours = cv2.findContours(
#         image=label, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_TC89_KCOS
#     )
#     points = []
#     count = 0

#     # plt.imshow(label)
#     # plt.savefig("./temp.png")
#     # print("contours", contours[1])

#     cv2_v = cv2.__version__.split(".")[0]
#     print(f"Totally {len(contours[1])} contours")
#     contours = contours[1] if cv2_v == "3" else contours[0]
#     polygons = []
#     for contour in contours:
#         polygon = []
#         for p in contour:
#             if count == sample:
#                 polygon.append(p[0])
#                 count = 0
#             else:
#                 count += 1
#         polygons.append(polygon)
#     return polygons