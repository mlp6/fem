import struct
scaleFactor = 0.1
wordSize = 4  # 32-bit float

dispout = open('disp_scaled.dat', 'wb')

headerCount = 3
count = 0
with open('disp.dat', 'rb') as dispin:
    while True:
        d = dispin.read(wordSize)
        if not d:
            break
        else:
            value = struct.unpack('f', d)
            if count == 0:
                NUM_NODES = value[0]
            elif count < (headerCount+NUM_NODES):
                dispout.write(struct.pack('f', value[0]))
                count += 1
            else:
                dispout.write(struct.pack('f', value[0]*scaleFactor))
                count += 1

dispout.close()
