"""
	Various tools for working with files
"""

from HandyLib import config, log
import os, hashlib, functools

def sha256(filename):
	"""
		Calculates the SHA256 hash of a file
	"""

	sha2h = hashlib.sha256()
	try:
		with open(filename, "rb") as f:
			[sha2h.update(chunk) for chunk in iter(functools.partial(f.read, 256), b"")]
	except:
		log("Failed to calculate SHA256 for file: {0}".format(filename), "fail")
		if config("debug"): raise
		return False
	return sha2h.hexdigest()

def unique_filename(filepath, filename):
	"""
		Returns a filename that will not conflict with existing files in a particular path
	"""

	basename, ext = get_file_extension(str(filename))
	i = 0
	while os.path.exists(os.path.join(filepath, "{0} ({1}){2}".format(basename, i, ext)) if i else "{0}/{1}".format(filepath, filename)):
		i += 1
	if i:
		filename = "{0} ({1}){2}".format(basename, i, ext)
	return filename

def get_file_extension(filename, loop=True):
	"""
		Separates a file's name from its extension(s) and returns them.
		`loop` determines whether all extensions are separated, or just the last one.
	"""

	basename, ext = os.path.splitext(filename)
	while os.path.splitext(basename)[1] and loop:
		basename, ext2 = os.path.splitext(basename)
		ext = ext2 + ext
	return basename, ext

def mkdir(directory):
	"""
		Checks if a directory exists, makes it if it doesn't.
		Returns true or false.
	"""

	if not os.path.isdir(directory):
		try:
			os.makedirs(directory)
			log("Created new directory: {0}".format(directory), "success")
			return True
		except OSError as exception:
			log("Tried to make a directory, but couldn't.", "fail")
			if config["debug"]: raise
			return False
	else:
		return True

def extract_file(filepath, filename, flat=False, loop=True):
	"""
		Provides file extraction capabilities for common compression and archive formats and returns a list of the files output.
		`flat` determines whether directory structure of archives is preserved.
		`loop` can be used to run the function a second time, for example with .tar.gz files.
	"""

	import zipfile, gzip, tarfile, shutil

	out_files = []
	# Just in case we get passed something stupid...
	filename = str(filename)
	filepath = str(filepath)
	f_base, f_ext = os.path.splitext(filename)

	# ZIP archives
	if f_ext == ".zip":
		log("Expanding ZIP archive {0}.".format(filename))
		try:
			with zipfile.ZipFile(os.path.join(filepath, filename)) as zip:
				# testzip() returns None or name of first bad file
				if zipfile.ZipFile.testzip(zip) is not None:
					log("Malformed ZIP or contents corrupted! Unable to process.", "fail")
					return False
				if flat:
					# Not using extractall() because we don't want a tree structure
					for member in zip.infolist():
						member = unique_filename(filepath, member)
						if flat:
							zip.extract(member, filepath)
						else:
							zip.extract(member)
						out_files.append(str(member))
				else:
					zip.extractall(filepath)
				# Delete the zip file now that we have its contents
			os.remove(os.path.join(filepath, filename))
		except:
			log("Unable to expand ZIP archive {0}. You should check its headers or something.".format(filename), "fail")
			if config("debug"): raise
			return False

	# GZIP compression
	elif f_ext == ".gz":
		log("Expanding GZIP compressed file {0}.".format(filename))
		try:
			out_fname = unique_filename(filepath, f_base)
			with gzip.open(os.path.join(filepath, filename), "rb") as f_in, open(os.path.join(filepath, out_fname), "wb") as f_out:
				shutil.copyfileobj(f_in, f_out)
			out_files.append(out_fname)
			# Delete the gz file now that we have its contents
			os.remove(os.path.join(filepath, filename))
		except:
			log("Unable to expand GZIP file {0}. It's likely malformed.".format(filename), "fail")
			if config("debug"): raise
			return False

	# TAR archives
	elif f_ext == ".tar":
		log("Expanding TAR archive {0}.".format(filename))
		try:
			with tarfile.open(os.path.join(filepath, filename), "r") as tar:
				if flat:
					# Not using extractall() because we don't want a tree structure
					for member in tar.getmembers():
						if member.isreg():
							if flat:
								# Strip any path information from members
								member.name = unique_filename(filepath, os.path.basename(member.name))
							tar.extract(member, filepath)
							out_files.append(member.name)
			# Delete the tar file now that we have its contents
			os.remove(os.path.join(filepath, filename))
		except:
			log("Unable to expand TAR archive {0}. Something is wrong with it.".format(filename), "fail")
			if config("debug"): raise
			return False

	# The file is not compressed or archived, or not a supported format
	else:
		return

	if not loop:
		return

	# Iterate back through, in case of layered archives or compressed archives (e.g. example.tar.gz)
	for filename in out_files:
		# Set loop switch to False to avoid creating blackhole
		extract_file(filepath, filename, loop=False)
