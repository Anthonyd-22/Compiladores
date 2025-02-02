#include <stdio.h>
#include "platform.h"

int main() {
    printf("Estás en %s\n", PLATFORM);
    printf("Mensaje: %s\n", OS_SPECIFIC_FUNCTION);
    return 0;
}
