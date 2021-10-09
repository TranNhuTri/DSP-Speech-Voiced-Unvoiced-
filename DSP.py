from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from math import log

class Wave:
	def __init__(self, nameFile="studio_male.wav"):
		self.Fs, self.data = wavfile.read(nameFile) # đọc file dữ liệu đầu vào

	@property 
	def times(self): # trả về mảng thời gian t
		return np.arange(0, len(self.data)/self.Fs, 1/self.Fs)

	@property
	def framerate(self): # trả về tần số lấy mẫu
		return self.Fs

	@property
	def amplitudes(self): # trả về mảng biên độ của tín hiệu
		return self.data

	def STE(self, N = 0.025): # tính STE
		N = N * self.Fs
		step = int(N // 4)
		E = np.zeros(len(self.data) + 1)

		for i in range(1, len(self.data) + 1):
			E[i] = E[i - 1] + self.data[i - 1]**2

		ste = []
		t = [] # thời gian tương ứng với các giá trị STE
		for i in range(1, len(E), step):
			start = int(i - N//2 + 1) # vị trí bắt đầu của khung
			end = int(i + N//2) # vị trí kết thúc của khung

			ste.append(E[min(len(E) - 1, end)] - E[max(1, start) - 1])
			t.append((i - 1)/self.Fs)

		ste = np.array(ste)
		t = np.array(t)

		return [t, ste]

	def detectSpeechSilent(self, T, minLenSilent = 0.3): # hàm tách khoảng lặng âm thanh
		f = [] # mảng chứa index STE của các vùng khoảng lặng
		g = [] # mảng chứa index STE của các vùng tiếng nói
		Si = [] # mảng chứa index STE vùng khoảng lặng tạm thời
		t, ste = self.STE()

		timeStep = 1/self.Fs # chu kì :))

		isFirstSilentRegion = True
		for i in range(len(ste)): # tách khoảng lặng
			if ste[i] < T:
				Si.append(i)
			else:
				if len(Si) != 0 and t[Si[-1]] - t[Si[0]] + timeStep >= minLenSilent or isFirstSilentRegion == True:
					f.append(Si)
				isFirstSilentRegion = False
				Si = []

		if len(Si) != 0 and t[Si[-1]] - t[Si[0]] + timeStep >= minLenSilent:
			f.append(Si)

		if len(f) > 0: # tách khoảng tiếng nói
			pre = 0
			for i in range(0, len(f)):
				for j in range(pre, f[i][0]):
					g.append(j)
				pre = f[i][-1]
		for i in range(f[-1][-1], len(ste)):
			g.append(i)

		return [f, g]

	def plotSTE(self):
		t, ste = self.STE()
		T = 1e9
		# plt.plot(self.times, self.amplitudes/max(self.amplitudes), '#2b80ffe0')
		plt.plot([0, t[-1]], [T, T], '#ff792be8')
		plt.plot(t, ste, '#ff0000')
		plt.show()


def main():
	wave = Wave()
	wave.plotSTE()
	f, g = wave.detectSpeechSilent(T = 1e9)
	print(len(f))
	print(len(g))

if __name__ == '__main__':
	main()

