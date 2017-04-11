# Author: Jesse Joseph
# Email: jjoseph@hmc.edu
# ID: 040161840

import sys

def main(input_file_name):
    try:
        with open(input_file_name, 'r') as fp:
            lines = fp.readlines()
            lines = [line.strip().split(',') for line in lines]
    except IOError:
        print("Couldn't open file: ", input_file_name, file=sys.stderr)
        print("Usage: ./lab3b <filename>", file=sys.stderr)
        sys.exit(1)

    # SUPERBLOCK METADATA
    for line in lines:
        if "SUPERBLOCK" in line:
            total_blocks_count = int(line[1])
            total_inodes_count = int(line[2])
            block_size = int(line[3])
            break

    # INODES: BLOCK CONSISTENCY
    for line in lines:
        if "INODE" in line:
            for i in range(15):
                block_ptr = int(line[i+12])
                if block_ptr > total_blocks_count:
                    printstr = "INVALID BLOCK " + str(block_ptr) + " "
                    printstr += "IN INODE " + line[1] + " "
                    printstr += "AT OFFSET " + str(i)
                    print(printstr)







if __name__ == "__main__":
    main(sys.argv[1])
