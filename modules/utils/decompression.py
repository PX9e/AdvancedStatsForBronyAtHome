

import gzip
from os.path import isfile


def decompression_gz(input_file, direct_output=False):
    content_of_file = gzip.open(input_file, 'rb')
    content_of_file = content_of_file.read()
    if direct_output:
        return content_of_file
    else:
        output_file_path = input_file[0:len(input_file)-3] + ".raw"
        output_file = open(str(output_file_path), "w")
        output_file.write(str(content_of_file))
        output_file.close()

        if isfile(output_file_path):
            return output_file_path
        else:
            return None

