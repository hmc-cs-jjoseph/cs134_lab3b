# Author: Jesse Joseph
# Email: jjoseph@hmc.edu
# ID: 040161840

import sys

def main(input_file_name):
    # READ FILESYSTEM SUMMARY
    try:
        with open(input_file_name, 'r') as fp:
            lines = fp.readlines()
            lines = [line.strip().split(',') for line in lines]
    except IOError:
        print("Couldn't open file:", input_file_name, file=sys.stderr)
        print("Usage: ./lab3b <filename>", file=sys.stderr)
        sys.exit(1)

    # SUPERBLOCK METADATA
    for line in lines:
        if "SUPERBLOCK" in line:
            total_blocks_count = int(line[1])
            total_inodes_count = int(line[2])
            block_size = int(line[3])
            inode_size = int(line[4])
            first_non_reserved_inode = int(line[7])
            break

    illegal_blocks = [1, 2] # 1 is superblock, 2 is group descriptor table
    reserved_blocks = []
    file_blocks = []
    file_references = {}
    free_blocks = []
    indirect_blocks = []
    freelist_inodes = []
    directory_list = {}
    # GROUP METADATA
    for line in lines:
        if "GROUP" in line:
            group_blocks_count = int(line[2])
            group_inodes_count = int(line[3])
            group_block_bitmap_base = int(line[6])
            group_inode_bitmap_base = int(line[7])
            group_inodes_base = int(line[8])
            inodes_range = int((group_inodes_count*inode_size)/block_size) # + 1 to round up?
            reserved_blocks += [group_block_bitmap_base]
            reserved_blocks += [group_inode_bitmap_base]
            reserved_blocks += range(group_inodes_base, group_inodes_base + inodes_range)

    # INODES: BLOCK CONSISTENCY
    for line in lines:
        if "INODE" in line:
            inode_number = int(line[1])
            link_count = int(line[6])
            file_type = line[2]
            file_references[inode_number] = {"link_count":link_count}
            file_references[inode_number]["discovered_links"] = 0
            file_references[inode_number]["blocks"] = []
            file_references[inode_number]["indirect"] = []
            file_references[inode_number]["double_indirect"] = []
            file_references[inode_number]["triple_indirect"] = []
            file_references[inode_number]["type"] = file_type
            pointers_per_indirection = int(block_size/4)
            for i in range(15):
                block_ptr = int(line[i+12])
                if block_ptr > total_blocks_count or block_ptr in illegal_blocks:
                    if i == 12:
                        printstr = "INVALID INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12
                    elif i == 13:
                        printstr = "INVALID DOUBLE INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12 + pointers_per_indirection 
                    elif i == 14:
                        printstr = "INVALID TRIPPLE INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12 + pointers_per_indirection + pointers_per_indirection**2
                    else:
                        printstr = "INVALID BLOCK " + str(block_ptr) + " "
                        offset = i
                    printstr += "IN INODE " + str(inode_number) + " "
                    printstr += "AT OFFSET " + str(offset)
                    print(printstr)
                elif block_ptr in reserved_blocks:
                    if i == 12:
                        printstr = "RESERVED INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12
                    elif i == 13:
                        printstr = "RESERVED DOUBLE INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12 + pointers_per_indirection 
                    elif i == 14:
                        printstr = "RESERVED TRIPPLE INDIRECT BLOCK " + str(block_ptr) + " "
                        offset = 12 + pointers_per_indirection + pointers_per_indirection**2
                    else:
                        printstr = "RESERVED BLOCK " + str(block_ptr) + " "
                        offset = i
                    printstr += "IN INODE " + str(inode_number) + " "
                    printstr += "AT OFFSET " + str(offset)
                    print(printstr)
                else:
                    if block_ptr == 0:
                        continue
                    elif i >= 12:
                        indirect_blocks += [block_ptr]
                        if i == 12:
                            file_references[inode_number]["indirect"] += [block_ptr]
                        elif i == 13:
                            file_references[inode_number]["double_indirect"] += [block_ptr]
                        else:
                            file_references[inode_number]["triple_indirect"] += [block_ptr]
                    else:
                        file_references[inode_number]["blocks"] += [block_ptr]
                        if block_ptr not in file_blocks:
                            file_blocks += [block_ptr]
    
    # INDIRECT BLOCKS: BLOCK CONSISTENCY
    for line in lines:
        if "INDIRECT" in line:
            parent_inode = int(line[1])
            indirection_level = int(line[2])
            offset = int(line[3])
            indirect_block_number = int(line[4])
            block_ptr = int(line[5])
            # INVALID BLOCKS
            if block_ptr > total_blocks_count or block_ptr in illegal_blocks:
                if indirection_level == 0:
                    printstr = "INVALID BLOCK " 
                elif indirection_level == 1:
                    printstr = "INVALID INDIRECT BLOCK "
                elif indirection_level == 2:
                    printstr = "INVALID DOUBLE INDIRECT BLOCK "
                else: 
                    printstr = "INVALID TRIPPLE INDIRECT BLOCK "
                printstr += str(block_ptr) + " "
                printstr += "IN INODE " + str(parent_inode) + " "
                printstr += "AT OFFSET " + str(offset)
                print(printstr)
            # RESERVED BLOCKS
            elif block_ptr in reserved_blocks:
                if indirection_level == 0:
                    printstr = "RESERVED BLOCK " 
                elif indirection_level == 1:
                    printstr = "RESERVED INDIRECT BLOCK "
                elif indirection_level == 2:
                    printstr = "RESERVED DOUBLE INDIRECT BLOCK "
                else: 
                    printstr = "RESERVED TRIPPLE INDIRECT BLOCK "
                printstr += str(block_ptr) + " "
                printstr += "IN INODE " + str(parent_inode) + " "
                printstr += "AT OFFSET " + str(offset)
                print(printstr)
            else:
                file_blocks += [block_ptr]
                indirect_blocks += [indirect_block_number]
                if indirection_level == 1:
                    file_references[parent_inode]["indirect"] += [indirect_block_number]
                elif indirection_level == 2:
                    file_references[parent_inode]["double_indirect"] += [indirect_block_number]
                else:
                    file_references[parent_inode]["triple_indirect"] += [indirect_block_number]

    # BLOCK FREE LIST CONSISTENCY
    for line in lines:
        if "BFREE" in line:
            free_blocks += [int(line[1])]

    referenced_blocks = free_blocks + illegal_blocks + file_blocks + indirect_blocks + reserved_blocks
    for i in range(1, total_blocks_count):
        if i not in referenced_blocks:
            print("UNREFERENCED BLOCK", i)

    for block in file_blocks:
        if block in free_blocks:
            printstr = "ALLOCATED BLOCK " + str(block) + " "
            printstr += "ON FREELIST"
            print(printstr)

    
    # INODE FREE LIST CONSISTENCY
    for line in lines:
        if "IFREE" in line:
            freelist_inodes += [int(line[1])]
    
    for inode_number in range(first_non_reserved_inode, total_inodes_count):
        if inode_number not in file_references and inode_number not in freelist_inodes:
            print("UNALLOCATED INODE " + str(inode_number) + " NOT ON FREELIST")

    for inode_number in file_references:
        if inode_number in freelist_inodes:
            print("ALLOCATED INODE " + str(inode_number) + " ON FREELIST")

    # DIRECTORY ENTRIES
    for line in lines:
        if "DIRENT" in line:
            parent_inode = int(line[1])
            inode_number = int(line[3])
            file_name = line[6]

            if inode_number in file_references:
                file_references[inode_number]["discovered_links"] += 1
                file_references[inode_number]["name"] = file_name
                inode_type = file_references[inode_number]["type"]
                if inode_type == "d":
                    if parent_inode in directory_list:
                        directory_list[parent_inode] += [inode_number]
                    else:
                        directory_list[parent_inode] = [inode_number]
            else:
                if inode_number < total_inodes_count:
                    printstr = "DIRECTORY INODE " + str(parent_inode) + " "
                    printstr += "NAME " + file_name + " "
                    printstr += "UNALLOCATED INODE " + str(inode_number)
                    print(printstr)
                else:
                    printstr = "DIRECTORY INODE " + str(parent_inode) + " "
                    printstr += "NAME " + file_name + " "
                    printstr += "INVALID INODE " + str(inode_number)
                    print(printstr)

    # '.' AND '..' CONSISTENCY
    for directory in directory_list:
        if directory == 2:
            this_inode = directory
            parent_inode = directory
        else:
            this_inode = directory
            for search_directory in directory_list:
                if this_inode in directory_list[search_directory][2:]:
                    parent_inode = search_directory

        dot_inode = directory_list[directory][0]
        ddot_inode = directory_list[directory][1]
        if ddot_inode != parent_inode:
            printstr = "DIRECTORY INODE " + str(this_inode) + " "
            printstr += "NAME '..' "
            printstr += "LINK TO INODE " + str(ddot_inode) + " "
            printstr += "SHOULD BE " + str(parent_inode)
            print(printstr)
        if dot_inode != this_inode:
            printstr = "DIRECTORY INODE " + str(this_inode) + " "
            printstr += "NAME '.' "
            printstr += "LINK TO INODE " + str(dot_inode) + " "
            printstr += "SHOULD BE " + str(this_inode)
            print(printstr)

    # LINK COUNT
    for inode_number in file_references:
        discovered_links = file_references[inode_number]["discovered_links"]
        link_count = file_references[inode_number]["link_count"]
        if discovered_links != link_count:
            printstr = "INODE " + str(inode_number) + " "
            printstr += "HAS " + str(discovered_links) + " LINKS "
            printstr += "BUT LINKCOUNT IS " + str(link_count)
            print(printstr)

    # DUPLICATE BLOCKS
    for inode_number in file_references:
        file_info = file_references[inode_number]
        for block_ptr in file_info["blocks"] + file_info["indirect"] + file_info["double_indirect"] + file_info["triple_indirect"]:
            for search_inode in file_references:
                if inode_number == search_inode:
                    continue
                else:
                    if block_ptr in file_references[search_inode]["blocks"]:
                        printstr = "DUPLICATE BLOCK " + str(block_ptr) + " "
                        printstr += "IN INODE " + str(search_inode) + " "
                        printstr += "AT OFFSET 0"
                        print(printstr)
                    if block_ptr in file_references[search_inode]["indirect"]:
                        printstr = "DUPLICATE INDIRECT BLOCK " + str(block_ptr) + " "
                        printstr += "IN INODE " + str(search_inode) + " "
                        printstr += "AT OFFSET 12"
                        print(printstr)
                    if block_ptr in file_references[search_inode]["double_indirect"]:
                        printstr = "DUPLICATE DOUBLE INDIRECT BLOCK " + str(block_ptr) + " "
                        printstr += "IN INODE " + str(search_inode) + " "
                        printstr += "AT OFFSET " + str(12 + pointers_per_indirection)
                        print(printstr)
                    if block_ptr in file_references[search_inode]["triple_indirect"]:
                        printstr = "DUPLICATE TRIPPLE INDIRECT BLOCK " + str(block_ptr) + " "
                        printstr += "IN INODE " + str(search_inode) + " "
                        printstr += "AT OFFSET " + str(12 + pointers_per_indirection + pointers_per_indirection**2)
                        print(printstr)
                    

                    











if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Missing required input: filesystem summary file", file=sys.stderr)
        print("Usage: ./lab3b <filename>", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1])



