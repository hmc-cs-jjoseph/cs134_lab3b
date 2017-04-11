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
            inode_size = int(line[4])
            break

    illegal_blocks = [1, 2] # 1 is superblock, 2 is group descriptor table
    file_blocks = []
    free_blocks = []
    indirect_blocks = []
    # GROUP METADATA
    for line in lines:
        if "GROUP" in line:
            group_blocks_count = int(line[2])
            group_inodes_count = int(line[3])
            group_block_bitmap_base = int(line[6])
            group_inode_bitmap_base = int(line[7])
            group_inodes_base = int(line[8])
            inodes_range = int((group_inodes_count*inode_size)/block_size) # + 1 to round up?
            illegal_blocks += [group_block_bitmap_base]
            illegal_blocks += [group_inode_bitmap_base]
            illegal_blocks += range(group_inodes_base, group_inodes_base + inodes_range)


    # INODES: BLOCK CONSISTENCY
    for line in lines:
        if "INODE" in line:
            for i in range(15):
                block_ptr = int(line[i+12])
                # if its a pointer to an indirect, should it say invalid indirect block?
                if block_ptr > total_blocks_count or block_ptr in illegal_blocks:
                    printstr = "INVALID BLOCK " + str(block_ptr) + " "
                    printstr += "IN INODE " + line[1] + " "
                    printstr += "AT OFFSET " + str(i)
                    print(printstr)
                else:
                    if i >= 12:
                        indirect_blocks += [block_ptr]
                    else:
                        file_blocks += [block_ptr]

                    
    
    # INDIRECT BLOCKS: BLOCK CONSISTENCY
    # if its an invalid pointer to a file, should this say invalid block or invalid indirect block?
    for line in lines:
        if "INDIRECT" in line:
            parent_inode = int(line[1])
            indirection_level = int(line[2])
            offset = int(line[3])
            indirect_block_number = int(line[4])
            block_ptr = int(line[5])
            if block_ptr > total_blocks_count or block_ptr in illegal_blocks:
                printstr = "INVALID INDIRECT BLOCK " + str(block_ptr) + " "
                printstr += "IN INODE " + str(parent_inode) + " "
                printstr += "AT OFFSET " + str(offset)
                print(printstr)
            else:
                file_blocks += [block_ptr]
                indirect_blocks += [indirect_block_number]

    # FREE LIST: BLOCK CONSISTENCY
    free_blocks = []
    for line in lines:
        if "BFREE" in line:
            free_blocks += [int(line[1])]

    referenced_blocks = free_blocks + illegal_blocks + file_blocks + indirect_blocks
    for i in range(total_blocks_count):
        if i not in referenced_blocks:
            print("UNREFERENCED BLOCK", i)





if __name__ == "__main__":
    main(sys.argv[1])
