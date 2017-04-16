# 匯入library
import numpy as np
from PIL import Image
import random
import pylab as pl
import math
import pylab as pl
from collections import defaultdict

# 匯入lena原圖
im = Image.open('lena.jpg').convert('L')

# 把圖片的長寬存起來並分別new雜訊、雜訊+原圖、雜訊和處理過差別的圖、處理過的圖
size = im.size
noise = Image.new("L", im.size)
temp = Image.new("L", im.size)
diff = Image.new("L", im.size)
output = Image.new("L", im.size)

# 設初值，iset為進入偶數次還是基數次；rand1和rand2為高斯分布；var為全域的變異數
iset = 0
rand1 = -1
rand2 = -1
var = 1000

# 每個像素都要做高斯，所以利用雙迴圈(x和y座標)來做
for i in range(0, size[0]):
	for j in range(0, size[1]):
		# iset=0為進入偶數次
		if(iset == 0):
			r = 0
			# 產生兩個在(-1,1)區間uniform的變數
			while(r >= 1.0 or r == 0):
				temp1 = random.uniform(-1,1)
				temp2 = random.uniform(-1,1)
				r = temp1 ** 2 + temp2 ** 2;
			fac = (-2.0 * math.log(r) / r) ** 0.5;
			# 把uniform轉到Gaussian分布
			rand1 = int(temp1 * fac * (var ** 0.5));
			rand2 = int(temp2 * fac * (var ** 0.5));
			iset = 1;
			# 把原圖和雜訊加在一起
			l = im.getpixel((i,j)) + rand2
			# 把雜訊單獨存放到noise圖裡
			noise.putpixel((i,j), rand2)
		# iset=1為進入偶數次
		if(iset == 1):
			iset = 0;
			l = im.getpixel((i,j)) + rand1
			noise.putpixel((i,j), rand1)
		# 把l值存放到temp圖裡
		temp.putpixel((i,j), l)

# mask為3，所以周圍會有1個像素要忽略
ignore = int((3 - 1) / 2)

# 開始帶入Adaptive local noise reduction filter的公式，也是用雙迴圈(x軸和y軸)來做，要扣掉ignore
for i in range(0 + ignore, size[0] - ignore):
	for j in range(0 + ignore, size[1] - ignore):
		# 取出3x3 mask9個的像素
		p1 = temp.getpixel((i-1,j-1))
		p2 = temp.getpixel((i,j-1))
		p3 = temp.getpixel((i+1,j-1))
		p4 = temp.getpixel((i-1,j))
		p5 = temp.getpixel((i,j))
		p6 = temp.getpixel((i+1,j))
		p7 = temp.getpixel((i-1,j+1))
		p8 = temp.getpixel((i,j+1))
		p9 = temp.getpixel((i+1,j+1))
		# 算期望值(平均數)
		ap = (p1+p2+p3+p4+p5+p6+p7+p8+p9)/9
		# 算每個像素平方的期望值(平均數)
		ap2 = (p1**2+p2**2+p3**2+p4**2+p5**2+p6**2+p7**2+p8**2+p9**2)/9
		vp = (p1-ap) ** 2 + (p2-ap) ** 2 + (p3-ap) ** 2 + (p4-ap) ** 2 + (p5-ap) ** 2 + (p6-ap) ** 2 + (p7-ap) ** 2 + (p8-ap) ** 2 + (p9-ap) ** 2
		# 用ap和ap2算出變異數
		vp2 = ap2 - ap ** 2
		# 設定閥值
		interval = 1000
		# 當vp2小於var時，直接把vp2設成1000
		if(vp2 < var):
			l = temp.getpixel((i,j)) - (var / vp2) * (temp.getpixel((i,j)) - ap)
		# 當vp2小於var + interval時，直接帶入公式
		elif(vp2 < var + interval):
			l = temp.getpixel((i,j)) - (var / vp2) * (temp.getpixel((i,j)) - ap)
		# 其餘的都不做直接放雜訊+原圖
		else:
			l = temp.getpixel((i,j))

		# 把計算結果放到output
		output.putpixel((i,j), int(l))

# 判斷雜訊+原圖和結果圖哪裡有改動到
for i in range(0, size[0]):
	for j in range(0, size[1]):
		# 白色有動  黑色沒動
		if (temp.getpixel((i,j)) != output.getpixel((i,j))):
			a=255
		else:
			a=0
		diff.putpixel((i,j),a)


output.save("output.png")
temp.save("temp.png")
noise.save("noise.png")
diff.save("diff.png")