
class Font(object):
    def __init__(self, name, w, h, iw, ih):
        self.name = name
        self.w = w
        self.h = h
        self.iw = iw
        self.ih = ih


fonts = [
    Font('roboto10x18', 10, 18, 1024, 32)
]


c_file = open('../entorama/entorama/raster.c', 'w')
c_file.write("""#include "raster.h"
#include <stdlib.h>


void raster_delete(Raster *raster) {
    free(raster);
}

static Raster *_fill_raster(Raster *raster, unsigned short *code) {
    unsigned k = 0;
    for (unsigned i = 0; i < raster->code_size; ++i) {
        if (code[i] > 255)
            for (unsigned short j = 0; j < code[i] - 255; ++j) {
                raster->data[k] = raster->data[k + 1] = raster->data[k + 2] = 255;
                raster->data[k + 3] = 0;
                k += 4;
            }
        else {
            raster->data[k] = raster->data[k + 1] = raster->data[k + 2] = 255;
            raster->data[k + 3] = (unsigned char)code[i];
            k += 4;
        }
    }
    return raster;
}
""")


h_file = open('../entorama/entorama/raster.h', 'w')
h_file.write("""#ifndef raster_h
#define raster_h


typedef struct Raster {
    unsigned w;
    unsigned h;
    unsigned iw;
    unsigned ih;
    unsigned code_size;
    unsigned data_size;
    unsigned char data[0];
} Raster;

void raster_delete(Raster *raster);

""")


for font in fonts:
    file = open('%s.tga' % font.name, 'rb')
    data = file.read()
    data_len = 18 + font.iw * font.ih * 3

    coded = []

    i = 18
    empty = 0
    while i < data_len:
        if data[i] == 255:
            empty += 1
        else:
            if empty > 0:
                coded.append(empty + 255)
                empty = 0
            coded.append(255 - data[i])
        i += 3
    if empty > 0:
        coded.append(empty + 255)

    c_file.write('\nRaster *raster_create_%s() {\n' % font.name)
    c_file.write('    Raster *raster = malloc(sizeof(Raster) + (%d * %d) * 4);\n' % (font.iw, font.ih))
    c_file.write('    raster->code_size = %s;\n' % len(coded))
    c_file.write('    raster->w = %s;\n' % font.w)
    c_file.write('    raster->h = %s;\n' % font.h)
    c_file.write('    raster->iw = %s;\n' % font.iw)
    c_file.write('    raster->ih = %s;\n' % font.ih)
    c_file.write('\n')
    c_file.write('    unsigned short coded[] = {\n')
    c_file.write('        %s' % ', '.join(str(c) for c in coded))
    c_file.write('\n')
    c_file.write('    };\n')
    c_file.write('\n')
    c_file.write('    return _fill_raster(raster, coded);\n')
    c_file.write('}\n')

    h_file.write('Raster *raster_create_%s();\n' % font.name)


h_file.write("""
#endif
""")
