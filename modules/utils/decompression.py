# coding=utf-8
import gzip
import bz2


compression_signature = {
    b"\x1f\x8b\x08": gzip,
    b"BZh": bz2,
}


def decompression(input_file, direct_output=False):
    """
    This function should extract our tarball,
    Exceptions are not handled !
    """
    first_line = open(input_file, "rb").readline(3)

    file_to_extract = compression_signature[first_line].open(input_file, 'rb')

    if direct_output:
        result = file_to_extract.readlines()
        file_to_extract.close()
        return result
    else:
        output_file_path = input_file[0:len(input_file) - 3] + ".raw"
        output_file = open(str(output_file_path), "wb")
        for line in file_to_extract:
            output_file.write(line)
        file_to_extract.close()
        output_file.close()

        return output_file_path
