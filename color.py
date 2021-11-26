import cv2 as cv
import numpy as np

# RGB颜色转换为HSL颜色
def rgb2hsl(rgb):
    rgb_normal = [[[rgb[0] / 255, rgb[1] / 255, rgb[2] / 255]]]
    hls = cv.cvtColor(np.array(rgb_normal, dtype=np.float32), cv.COLOR_RGB2HLS)
    return hls[0][0][0], hls[0][0][2], hls[0][0][1]  # hls to hsl


# HSL颜色转换为RGB颜色
def hsl2rgb(hsl):
    hls = [[[hsl[0], hsl[2], hsl[1]]]]  # hsl to hls
    rgb_normal = cv.cvtColor(np.array(hls, dtype=np.float32), cv.COLOR_HLS2RGB)
    return int(rgb_normal[0][0][0] * 255), int(rgb_normal[0][0][1] * 255), int(rgb_normal[0][0][2] * 255)

# HSL渐变色
def get_multi_colors_by_hsl(begin_color, end_color, color_count):
    if color_count < 2:
        return []
    colors = []
    hsl1 = rgb2hsl(begin_color)
    hsl2 = rgb2hsl(end_color)
    steps = [(hsl2[i] - hsl1[i]) / (color_count - 1) for i in range(3)]
    for color_index in range(color_count):
        hsl = [hsl1[i] + steps[i] * color_index for i in range(3)]
        colors.append(hsl2rgb(hsl))
    colorsHex = [RGB_to_Hex(color) for color in colors]
    return colorsHex

def RGB_to_Hex(rgb):
    r, g, b = rgb
    strs = '#'
    strs += str(hex(r))[-2:].replace('x', '0').upper()
    strs += str(hex(g))[-2:].replace('x', '0').upper()
    strs += str(hex(b))[-2:].replace('x', '0').upper()
    return strs


if __name__ == '__main__':
    begin = [0, 255, 0]
    end = [255, 0, 0]
    cnt = 11
    colors = get_multi_colors_by_hsl(begin, end, cnt)
    print(type(colors))
    print(type(colors[0]))
    print(colors)

