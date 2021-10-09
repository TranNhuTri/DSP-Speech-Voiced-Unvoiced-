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

	def PlotSTE(self):
		t, ste = self.STE()
		T = 1e9
		# plt.plot(self.times, self.amplitudes/max(self.amplitudes), '#2b80ffe0')
		# plt.plot([0, t[-1]], [T, T], '#ff792be8')
		plt.plot(t, ste, '#ff0000')
		plt.show()

	def DetectSpeechSilent(self, T, minLenSilent = 0.3): # hàm tách khoảng lặng âm thanh
		silent = [] # mảng chứa index STE của các vùng khoảng lặng
		speech = [] # mảng chứa index STE của các vùng tiếng nói
		tmpSi = [] # mảng chứa index STE vùng khoảng lặng tạm thời
		t, ste = self.STE()

		timeStep = 1/self.Fs # chu kì :))

		isFirstSilentRegion = True
		for i in range(len(ste)): # tách khoảng lặng
			if ste[i] < T:
				tmpSi.append(i)
			else:
				if len(tmpSi) != 0 and t[tmpSi[-1]] - t[tmpSi[0]] + timeStep >= minLenSilent or isFirstSilentRegion == True:
					silent.append(tmpSi)
				isFirstSilentRegion = False
				tmpSi = []

		if len(silent) != 0 and t[tmpSi[-1]] - t[tmpSi[0]] + timeStep >= minLenSilent:
			silent.append(tmpSi)

		if len(silent) > 0: # tách khoảng tiếng nói
			pre = 0
			for i in range(0, len(silent)):
				for j in range(pre, silent[i][0]):
					speech.append(j)
				pre = silent[i][-1]
		for i in range(silent[-1][-1], len(ste)):
			speech.append(i)

		return [silent, speech]

	def DetectOverlapSTE(self, silent, speech):
		t, ste = self.STE()

		Tmax = 0
		Tmin = max(ste)

		for i in silent:
			for j in i:
				Tmax = max(Tmax, ste[j])
		for i in speech:
			Tmin = min(Tmin, ste[i])

		f = [] # mảng chứa STE của vùng lặng trong overlap
		for i in silent:
			for j in i:
				if ste[j] > Tmin and ste[j] < Tmax:
					f.append(ste[j])
		g = [] # mảng chứa STE của vùng tiếng nói trong overlap
		for i in speech:
			if ste[i] > Tmin and ste[i] < Tmax:
				g.append(ste[j])

		return [f, g, Tmin, Tmax]

	def STEThreshold(self, T = 1e9):

		silent, speech = self.DetectSpeechSilent(T)

		f, g, Tmin, Tmax = self.DetectOverlapSTE(silent, speech)

		if len(f) == 0 or len(g) == 0:
			print("Break")
			return T

		Tmid = (Tmax + Tmin)/2

		i = len([i for i in f if i < Tmid])
		p = len([i for i in g if i > Tmid])
		j = -1
		q = -1
		while i != j or p != q:
			value = sum([max(i - Tmid, 0) for i in f])/len(f) - sum([max(Tmid - i, 0) for i in g])/len(g)
			if value > 0:
				Tmin = Tmid
			else:
				Tmax = Tmid
			Tmid = (Tmax + Tmin)/2
			j = i
			q = p
			i = len([i for i in f if i < Tmid])
			p = len([i for i in g if i > Tmid])

		return Tmid

	def SpeechSilentDiscrimination(self):
		n = self.times
		T = self.STEThreshold();
		f, g = self.DetectSpeechSilent(T)

		t, ste = self.STE()

		fig, [plt1, plt2] = plt.subplots(2, 1)

		for i in f:
			start, end = i[0], i[-1]

			plt1.plot([t[start], t[start]], [0, max(ste)], '#00ca06e0')
			plt1.plot([t[end], t[end]], [0, max(ste)], '#d87bff')

			plt2.plot([t[start], t[start]], [-1, 1], '#00ca06e0')
			plt2.plot([t[end], t[end]], [-1, 1], '#d87bff')

			print(t[start], t[end], end = " ")

		print()

		plt1.plot([0, n[-1]], [T, T], '#ff792be8')
		plt1.plot(t, ste, '#2b80ffe0')

		data = self.amplitudes

		plt2.plot(n, data/max(data), '#2b80ffe0')
		plt2.plot(t, ste/max(ste), '#ff0000')

		plt.show()


def main():
	wave = Wave()
	wave.SpeechSilentDiscrimination()

if __name__ == '__main__':
	main()

