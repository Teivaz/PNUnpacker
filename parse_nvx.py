from io_nebula import nvx
from io_nebula.stream import InputStream, OutputStream

def main():
	with open("nvx/skin.nvx", "rb") as f:
		m = nvx.Mesh(stream=InputStream(f))
		with open("nvx/skinX.nvx", "wb") as o:
			m.to_stream(OutputStream(o))

if __name__ == "__main__":
	main()
