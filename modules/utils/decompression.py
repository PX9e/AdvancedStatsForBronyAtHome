# coding=utf-8
import gzip
import bz2
from os import remove
compression_signature = {
    b"\x1f\x8b\x08": gzip,
    b"BZh": bz2,
}


def decompression(input_file, direct_output=False, autodelete_file=True):
    """
    Extract the file specified in parameter

    Direct_output is faster than the non direct one but can create memory overflow if the file is too big.

    :param input_file: Path and name of the file to extract
    :type input_file: str

    :param direct_output: Indicate if we want to get a file (stored on hard drive) with extracted data or if we want a
    list of extracted lines stored in memory.
    :type direct_output: bool

    :param autodelete_file: if True delete the compressed file after extraction.
    :type autodelete_file: bool

    :returns if direct_output is False a path of the extracted file either a list of lines.
    """
    first_line = open(input_file, "rb").readline(3)

    file_to_extract = compression_signature[first_line].open(input_file, 'rb')

    if direct_output:
        result = file_to_extract.readlines()
        file_to_extract.close()
        if autodelete_file:
            remove(input_file)
        return result
    else:
        output_file_path = input_file[0:len(input_file) - 3] + ".raw"
        with open(str(output_file_path), "wb") as output_file:
            for line in file_to_extract:
                output_file.write(line)
        file_to_extract.close()
        remove(input_file)
        return output_file_path
