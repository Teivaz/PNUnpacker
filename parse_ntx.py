import os
from io_nebula import ntx
from io_nebula.stream import InputStream


def convert_file(name):
	with open(name, "rb") as f:
		t = ntx.Texture(stream=InputStream(f))
		t.mips[0].save_to_file(name + ".png")

def convert_in_dir(path):
	for root, dirs, files in os.walk(path):
		for file in files:
			path = os.path.join(root, file)
			if os.path.splitext(path)[-1] == ".ntx":
				convert_file(path)


def main():
	#convert_in_dir("nvx")
	convert_file("nvx/texturenone.ntx")


if __name__ == "__main__":
	main()
